def test_backend_modules_import() -> None:
    from backend.app.main import app

    assert app is not None
