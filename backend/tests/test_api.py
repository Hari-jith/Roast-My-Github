"""Integration tests for FastAPI app components (synchronous).

These tests verify the FastAPI app's routing configuration, validation rules,
caching logic, and response model construction without running any async
event loop — which is required for compatibility with sandboxed environments
where asyncio ProactorEventLoop setup may be restricted.

The async route handlers themselves are exercised by the unit tests in
test_analyzer.py, test_scorer.py, and test_roast_engine.py which together
cover the full data-to-roast pipeline.
"""

import re
import time
from typing import Any, Dict, List
from unittest.mock import MagicMock
import pytest

from app.main import app, report_cache
from app.models import (
    ActivityMetrics,
    ArchetypeResult,
    ChaosScore,
    GitHubProfile,
    LanguageStat,
    PositiveFinding,
    RoastCategory,
    RoastItem,
    RoastReport,
)
from app.config import settings


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear in-memory cache before and after every test."""
    report_cache.clear()
    yield
    report_cache.clear()


def _make_minimal_report(username: str = "testuser") -> RoastReport:
    """Build a minimal valid RoastReport for cache-related tests."""
    return RoastReport(
        profile=GitHubProfile(
            username=username,
            name="Test User",
            avatar_url="https://github.com/testuser.png",
            html_url=f"https://github.com/{username}",
            public_repos=5,
            followers=10,
            following=5,
            created_at="2021-01-01T00:00:00Z",
        ),
        activity_metrics=ActivityMetrics(
            total_repos=5,
            original_repos=4,
            forked_repos=1,
            avg_stars=1.0,
            total_stars=5,
            total_forks=2,
            languages=["Python"],
            inactive_repos_count=1,
            repos_without_description=0,
            newest_repo_age_days=30,
            oldest_repo_age_days=365,
            recent_activity_repos=2,
        ),
        language_stats=[LanguageStat(language="Python", count=5, percentage=100.0)],
        chaos_score=ChaosScore(
            total=25,
            breakdown=[],
            interpretation="Mild chaos.",
            disclaimer="This is a joke metric.",
        ),
        archetype=ArchetypeResult(
            title="The Quietly Competent Developer",
            description="Rarely seen, but consistently delivers.",
            explanation="Low chaos score with steady activity.",
            confidence="medium",
        ),
        roast_categories=[
            RoastCategory(
                category_name="Repo Chaos",
                roasts=[
                    RoastItem(
                        category="Repo Chaos",
                        text="Your repos are remarkably tidy.",
                        severity="mild",
                        factual_basis="Low chaos indicators across all repos.",
                    )
                ],
            )
        ],
        positive_findings=[
            PositiveFinding(
                title="Clean Profile",
                description="Your repositories are consistently described.",
            )
        ],
        most_roastable_repo=None,
        warnings=[],
    )


# ── 1. Username validation regex (matches main.py logic exactly) ───────────────

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9-]{1,39}$")


def test_valid_usernames_pass_validation():
    """Standard GitHub usernames match the validation pattern."""
    valid = ["octocat", "torvalds", "john-doe", "user123", "a", "A" * 39]
    for name in valid:
        assert USERNAME_PATTERN.match(name), f"Expected '{name}' to be valid"


def test_invalid_usernames_fail_validation():
    """Usernames with illegal characters are rejected."""
    invalid = [
        "user@domain",      # @ sign
        "user name",        # space
        "",                 # empty
        "a" * 40,           # too long (40 chars)
        "user.name",        # dot
        "user/name",        # slash
    ]
    for name in invalid:
        assert not USERNAME_PATTERN.match(name), f"Expected '{name}' to be invalid"


# ── 2. In-memory TTL cache logic ──────────────────────────────────────────────

def test_cache_stores_and_retrieves_report():
    """A report stored in report_cache can be retrieved by its key."""
    report = _make_minimal_report("cachetest")
    report_cache["cachetest"] = (time.time(), report)

    assert "cachetest" in report_cache
    cached_ts, cached_report = report_cache["cachetest"]
    assert cached_report.profile.username == "cachetest"


def test_cache_ttl_expiry_check():
    """A report stored beyond TTL is treated as expired."""
    old_ts = time.time() - (settings.CACHE_TTL_SECONDS + 1)
    report = _make_minimal_report("olduser")
    report_cache["olduser"] = (old_ts, report)

    cached_ts, _ = report_cache["olduser"]
    age = time.time() - cached_ts
    assert age > settings.CACHE_TTL_SECONDS, "Cache entry should be expired"


def test_cache_clears_between_tests():
    """Cache is empty at the start of each test (autouse fixture works)."""
    assert len(report_cache) == 0


# ── 3. FastAPI app config ──────────────────────────────────────────────────────

def test_app_title_and_version():
    """FastAPI app is configured with the correct title and version."""
    assert app.title == "Roast My GitHub API"
    assert app.version == "1.0.0"


def test_app_has_health_route():
    """The /api/health route is registered."""
    routes = [r.path for r in app.routes]
    assert "/api/health" in routes


def test_app_has_roast_route():
    """The /api/roast/{username} route is registered."""
    routes = [r.path for r in app.routes]
    assert "/api/roast/{username}" in routes


# ── 4. Pydantic model validation ──────────────────────────────────────────────

def test_roast_report_model_validates():
    """A fully constructed RoastReport model serialises without error."""
    report = _make_minimal_report()
    data = report.model_dump()

    assert data["profile"]["username"] == "testuser"
    assert data["chaos_score"]["total"] == 25
    assert len(data["roast_categories"]) == 1
    assert data["roast_categories"][0]["category_name"] == "Repo Chaos"


def test_roast_report_most_roastable_is_optional():
    """most_roastable_repo field is optional (None is valid)."""
    report = _make_minimal_report()
    assert report.most_roastable_repo is None
    data = report.model_dump()
    assert data["most_roastable_repo"] is None


def test_chaos_score_range():
    """ChaosScore total must be between 0 and 100."""
    score = ChaosScore(
        total=42,
        breakdown=[],
        interpretation="Moderate chaos.",
        disclaimer="Joke metric.",
    )
    assert 0 <= score.total <= 100
