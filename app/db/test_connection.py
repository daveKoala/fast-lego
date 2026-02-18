from app.db import Connection


class _FakeConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, _statement):
        return 1


def test_check_database_connection_ok(monkeypatch):
    monkeypatch.setattr(Connection.engine, "connect", lambda: _FakeConnection())

    connected, details = Connection.check_database_connection()

    assert connected is True
    assert details == "Database connection healthy"


def test_check_database_connection_error(monkeypatch):
    def _raise_error():
        raise RuntimeError("db unavailable")

    monkeypatch.setattr(Connection.engine, "connect", _raise_error)

    connected, details = Connection.check_database_connection()

    assert connected is False
    assert "db unavailable" in details
