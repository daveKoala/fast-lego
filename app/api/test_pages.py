from fastapi.testclient import TestClient

from app.api import pages
from app.db.models import CatalogItem
from app.main import app

client = TestClient(app)


class _FakeExecResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class _FakeSession:
    def __init__(self, items=None, fail_commit=False):
        self._items = items or []
        self._fail_commit = fail_commit
        self.added = []
        self.committed = False
        self.rolled_back = False

    def exec(self, _statement):
        return _FakeExecResult(self._items)

    def add(self, item):
        self.added.append(item)

    def commit(self):
        if self._fail_commit:
            raise RuntimeError("commit failed")
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def _override_session(items, fail_commit=False):
    session = _FakeSession(items, fail_commit=fail_commit)

    def _dependency():
        return session

    return session, _dependency


def test_welcome_page_renders():
    response = client.get("/")

    assert response.status_code == 200
    assert "Welcome" in response.text
    assert "Request ID:" in response.text
    assert "x-request-id" in response.headers


def test_about_page_renders():
    response = client.get("/about")

    assert response.status_code == 200
    assert "About" in response.text
    assert "x-request-id" in response.headers


def test_search_page_renders():
    response = client.get("/search")

    assert response.status_code == 200
    assert "Search" in response.text
    assert "x-request-id" in response.headers


def test_search_submit_returns_catalog_results():
    _, dependency = _override_session(
        [CatalogItem(name="Galaxy Explorer", category="Space", description="Deep-space ship")]
    )
    app.dependency_overrides[pages.get_session] = dependency
    try:
        response = client.post("/search", data={"query": "space"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Results for" in response.text
    assert "Galaxy Explorer" in response.text
    assert "Space" in response.text


def test_search_submit_empty_results_message():
    _, dependency = _override_session([])
    app.dependency_overrides[pages.get_session] = dependency
    try:
        response = client.post("/search", data={"query": "unknown"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "No matching catalog items found." in response.text


def test_search_submit_still_renders_results_when_log_write_fails():
    _, dependency = _override_session(
        [CatalogItem(name="Galaxy Explorer", category="Space", description="Deep-space ship")],
        fail_commit=True,
    )
    app.dependency_overrides[pages.get_session] = dependency
    try:
        response = client.post("/search", data={"query": "space"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Galaxy Explorer" in response.text
