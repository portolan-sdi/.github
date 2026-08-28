"""Tests for the issue governance rules.

Every call the script makes to GitHub goes through `enforce.request`, so
the fake below stands in for the whole API. Each test asserts on the calls
recorded, which is what the rules are: what got written, and what did not.
"""

from __future__ import annotations

import json
from pathlib import Path

import enforce

CONFIG = {
    "org_wide": ["bug", "enhancement", "task", "urgent"],
    "per_repo": {"portolan-spec": ["schemas"]},
}
NORMS = "https://example.invalid/norms"


class FakeApi:
    """Records writes and answers reads from a canned issue."""

    def __init__(self, labels=None, milestone=None, comments=None, milestones=None):
        self.issue = {
            "number": 7,
            "labels": [{"name": name} for name in (labels or [])],
            "milestone": milestone,
        }
        self.comments = list(comments or [])
        self.milestones = list(milestones or [])
        self.calls: list[tuple[str, str, dict | None]] = []

    def __call__(self, method, path, token, body=None):
        self.calls.append((method, path, body))
        if method == "GET" and path.startswith("/repos/o/r/issues/7") and "comments" not in path:
            return self.issue
        if method == "GET" and "comments" in path:
            return self.comments if "page=1" in path else []
        if method == "GET" and "milestones" in path:
            return self.milestones if "page=1" in path else []
        if method == "POST" and "comments" in path:
            self.comments.append({"body": body["body"]})
            return {"id": 1}
        return {}

    def writes(self, method):
        return [(path, body) for verb, path, body in self.calls if verb == method]


def install(monkeypatch, fake):
    monkeypatch.setattr(enforce, "request", fake)
    return fake


def test_allowed_labels_merges_repo_additions(tmp_path: Path):
    path = tmp_path / "allowed.json"
    path.write_text(json.dumps(CONFIG))
    assert enforce.allowed_labels(str(path), "portolan-spec") == {
        "bug", "enhancement", "task", "urgent", "schemas",
    }
    assert "schemas" not in enforce.allowed_labels(str(path), "rashid")


def test_ships_the_real_config_for_every_named_repo():
    """The config in this repo parses and names only labels, not junk."""
    path = Path(__file__).with_name("allowed-labels.json")
    config = json.loads(path.read_text())
    assert "bug" in config["org_wide"]
    assert "urgent" in config["org_wide"]
    for repo, extras in config["per_repo"].items():
        assert extras, f"{repo} lists no additional labels"
        assert not set(extras) & set(config["org_wide"]), repo


def test_strips_labels_outside_the_set_and_comments_once(monkeypatch):
    fake = install(monkeypatch, FakeApi(labels=["bug", "roadmap:mvp", "spec-sprint"]))
    removed = enforce.strip_labels("o/r", 7, "t", set(CONFIG["org_wide"]), NORMS)

    assert removed == 2
    deleted = [path for path, _ in fake.writes("DELETE")]
    assert any("roadmap%3Amvp" in path for path in deleted)
    assert any("spec-sprint" in path for path in deleted)
    posted = fake.writes("POST")
    assert len(posted) == 1
    assert "`roadmap:mvp`" in posted[0][1]["body"]
    assert enforce.MARKER in posted[0][1]["body"]


def test_leaves_a_clean_issue_untouched(monkeypatch):
    fake = install(monkeypatch, FakeApi(labels=["bug", "urgent"]))
    assert enforce.strip_labels("o/r", 7, "t", set(CONFIG["org_wide"]), NORMS) == 0
    assert fake.writes("DELETE") == []
    assert fake.writes("POST") == []


def test_does_not_repeat_an_identical_comment(monkeypatch):
    body = enforce.comment_body(["roadmap:mvp"], NORMS)
    fake = install(monkeypatch, FakeApi(labels=["roadmap:mvp"], comments=[{"body": body}]))

    assert enforce.strip_labels("o/r", 7, "t", set(CONFIG["org_wide"]), NORMS) == 1
    assert fake.writes("POST") == []


def test_comments_again_when_a_different_label_appears(monkeypatch):
    old = enforce.comment_body(["roadmap:mvp"], NORMS)
    fake = install(monkeypatch, FakeApi(labels=["spec-sprint"], comments=[{"body": old}]))

    enforce.strip_labels("o/r", 7, "t", set(CONFIG["org_wide"]), NORMS)
    assert len(fake.writes("POST")) == 1


def test_sets_backlog_on_a_new_issue_with_no_milestone(monkeypatch):
    fake = install(monkeypatch, FakeApi(
        milestones=[{"title": "Beta", "number": 1}, {"title": "Backlog", "number": 4}],
    ))
    enforce.default_milestone("o/r", 7, "t", "opened")

    patches = fake.writes("PATCH")
    assert patches == [("/repos/o/r/issues/7", {"milestone": 4})]


def test_never_overrides_a_milestone_a_human_set(monkeypatch):
    fake = install(monkeypatch, FakeApi(
        milestone={"title": "Beta", "number": 1},
        milestones=[{"title": "Backlog", "number": 4}],
    ))
    enforce.default_milestone("o/r", 7, "t", "opened")
    assert fake.writes("PATCH") == []


def test_ignores_events_other_than_opened(monkeypatch):
    fake = install(monkeypatch, FakeApi(milestones=[{"title": "Backlog", "number": 4}]))
    enforce.default_milestone("o/r", 7, "t", "edited")
    assert fake.calls == []


def test_skips_quietly_when_the_repo_has_no_backlog(monkeypatch):
    fake = install(monkeypatch, FakeApi(milestones=[{"title": "Beta", "number": 1}]))
    enforce.default_milestone("o/r", 7, "t", "opened")
    assert fake.writes("PATCH") == []
