from __future__ import annotations

import json
import os
import re
from datetime import date
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, ValidationError

from backend.storage.uploads import get_doc_paths, read_json


class InvoiceLineItem(BaseModel):
    description: str
    qty: float = 1.0
    unit_price: float = 0.0
    amount: float = 0.0


class InvoiceSchema(BaseModel):
    supplier: str
    invoice_no: str
    invoice_date: str
    due_date: str
    currency: str
    subtotal: float
    tax: float
    total: float
    line_items: list[InvoiceLineItem] = Field(default_factory=list)


class BankTransaction(BaseModel):
    date: str
    description: str
    amount: float


class BankStatementSchema(BaseModel):
    bank: str
    account: str
    period_start: str
    period_end: str
    opening_balance: float
    closing_balance: float
    transactions: list[BankTransaction] = Field(default_factory=list)


class ReceiptItem(BaseModel):
    name: str
    amount: float


class ReceiptSchema(BaseModel):
    merchant: str
    date: str
    total: float
    currency: str
    items: list[ReceiptItem] = Field(default_factory=list)


SchemaName = Literal["invoice", "bank_statement", "receipt"]


def _load_extracted_text(doc_id: str, base_dir: Any = None) -> str:
    paths = get_doc_paths(doc_id, base_dir=base_dir)
    extracted_dir = paths["extracted_dir"]

    parts: list[str] = []
    for filename, key in [
        ("native_text.json", "text"),
        ("ocr_text.json", "full_text"),
    ]:
        artifact = extracted_dir / filename
        if artifact.exists():
            payload = read_json(artifact)
            for page in payload.get("pages", []):
                value = page.get(key)
                if value:
                    parts.append(str(value))

    return "\n".join(parts).strip()


def _extract_amount(text: str, keyword: str, default: float) -> float:
    pattern = rf"{keyword}\s*[:#-]?\s*(\d+(?:\.\d{{1,2}})?)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return float(match.group(1))
    return default


def _extract_invoice_no(text: str) -> str:
    match = re.search(r"(?:invoice\s*(?:no|number)?\s*[:#-]?\s*)([A-Za-z0-9-]+)", text, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return "UNKNOWN"


def _extract_currency(text: str) -> str:
    match = re.search(r"\b(AUD|USD|EUR|GBP|SGD|NZD)\b", text)
    return match.group(1) if match else "USD"


def _today() -> str:
    return date.today().isoformat()


def _stub_invoice(text: str) -> InvoiceSchema:
    subtotal = _extract_amount(text, "subtotal", 100.0)
    tax = _extract_amount(text, "tax", round(subtotal * 0.1, 2))
    total = _extract_amount(text, "total", round(subtotal + tax, 2))
    supplier = "ACME"
    supplier_match = re.search(r"supplier\s*[:#-]?\s*([A-Za-z0-9 &.-]+)", text, flags=re.IGNORECASE)
    if supplier_match:
        supplier = supplier_match.group(1).strip()

    return InvoiceSchema(
        supplier=supplier,
        invoice_no=_extract_invoice_no(text),
        invoice_date=_today(),
        due_date=_today(),
        currency=_extract_currency(text),
        subtotal=subtotal,
        tax=tax,
        total=total,
        line_items=[
            InvoiceLineItem(
                description="Auto-detected item",
                qty=1,
                unit_price=subtotal,
                amount=subtotal,
            )
        ],
    )


def _stub_bank_statement(text: str) -> BankStatementSchema:
    closing = _extract_amount(text, "closing balance", 0.0)
    opening = _extract_amount(text, "opening balance", max(0.0, closing - 100.0))
    return BankStatementSchema(
        bank="Example Bank",
        account="XXXX-1234",
        period_start=_today(),
        period_end=_today(),
        opening_balance=opening,
        closing_balance=closing,
        transactions=[BankTransaction(date=_today(), description="Auto-detected", amount=closing - opening)],
    )


def _stub_receipt(text: str) -> ReceiptSchema:
    total = _extract_amount(text, "total", 0.0)
    merchant = "Unknown Merchant"
    merchant_match = re.search(r"merchant\s*[:#-]?\s*([A-Za-z0-9 &.-]+)", text, flags=re.IGNORECASE)
    if merchant_match:
        merchant = merchant_match.group(1).strip()
    return ReceiptSchema(
        merchant=merchant,
        date=_today(),
        total=total,
        currency=_extract_currency(text),
        items=[ReceiptItem(name="Auto item", amount=total)],
    )


def _schema_model(schema_name: SchemaName):
    if schema_name == "invoice":
        return InvoiceSchema
    if schema_name == "bank_statement":
        return BankStatementSchema
    return ReceiptSchema


def _schema_json(schema_name: SchemaName) -> dict[str, Any]:
    return _schema_model(schema_name).model_json_schema()


def _extract_response_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"]

    output = payload.get("output", [])
    for item in output:
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                return text
    return ""


def _llm_structure(schema_name: SchemaName, extracted_text: str) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for llm mode")

    prompt = {
        "schema": _schema_json(schema_name),
        "instruction": "Return only valid JSON matching the schema.",
        "extracted_text": extracted_text,
    }

    body = {
        "model": "gpt-4.1-mini",
        "input": json.dumps(prompt),
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    with httpx.Client(timeout=60) as client:
        response = client.post("https://api.openai.com/v1/responses", headers=headers, json=body)
        response.raise_for_status()
        payload = response.json()

    text = _extract_response_text(payload)
    if not text:
        raise ValueError("No text output from model")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Model did not return valid JSON") from exc


def structure(
    doc_id: str,
    schema_name: SchemaName,
    mode: Literal["stub", "llm"] = "stub",
    base_dir: Any = None,
) -> dict[str, Any]:
    text = _load_extracted_text(doc_id=doc_id, base_dir=base_dir)

    if mode == "stub":
        if schema_name == "invoice":
            return _stub_invoice(text).model_dump()
        if schema_name == "bank_statement":
            return _stub_bank_statement(text).model_dump()
        if schema_name == "receipt":
            return _stub_receipt(text).model_dump()
        raise ValueError("Unsupported schema")

    if mode != "llm":
        raise ValueError("mode must be one of: stub, llm")

    model = _schema_model(schema_name)
    raw = _llm_structure(schema_name=schema_name, extracted_text=text)
    try:
        return model.model_validate(raw).model_dump()
    except ValidationError as exc:
        raise ValueError("Structured output validation failed") from exc
