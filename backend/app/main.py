from __future__ import annotations

from fastapi import FastAPI

from backend.app.routes import router

app = FastAPI(title="Finance AI Backend", version="0.1.0")
app.include_router(router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}
