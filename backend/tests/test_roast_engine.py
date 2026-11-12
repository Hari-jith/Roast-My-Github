"""Unit tests for the rule-based roast engine and detectors."""

import pytest
from app.models import ActivityMetrics, RepoInfo
from app.roast_engine import (
    detect_abandoned_museum,
    detect_commit_patterns,
    detect_language_identity,
    detect_popularity_department,
    detect_readme_dreamer,
    detect_repo_chaos,
    get_user_seed,
)


def test_detect_repo_chaos() -> None:
    """Test detect_repo_chaos triggers when repos contain chaotic names and excessive forks."""
    metrics = ActivityMetrics(
        total_repos=10,
        original_repos=5,
        forked_repos=5,  # 50% forks
        avg_stars=0.2,
        total_stars=2,
        total_forks=0,
        inactive_repos_count=2,
        repos_without_description=2,
        newest_repo_age_days=10,
        oldest_repo_age_days=200,
        recent_activity_repos=2,
    )
    chaotic_repos = [
        RepoInfo(name="project-final-v2", html_url="", stars=0, forks=0, is_fork=False),
        RepoInfo(name="project-test-copy", html_url="", stars=0, forks=0, is_fork=True),
        RepoInfo(name="project-backup", html_url="", stars=0, forks=0, is_fork=True),
        RepoInfo(name="another-v3-new", html_url="", stars=0, forks=0, is_fork=False),
    ]

    roasts = detect_repo_chaos(metrics, chaotic_repos, seed=10)

    assert len(roasts) > 0
    categories = {r.category for r in roasts}
    assert "Repository Chaos" in categories
    # Check that factual basis mentions metrics
    assert any("versioning" in r.factual_basis.lower() or "forks" in r.factual_basis.lower() for r in roasts)


def test_detect_abandoned_museum() -> None:
    """Test detect_abandoned_museum fires when many repositories are inactive (> 365 days)."""
    metrics = ActivityMetrics(
        total_repos=15,
        original_repos=15,
        forked_repos=0,
        avg_stars=2.0,
        total_stars=30,
        total_forks=5,
        inactive_repos_count=12,  # 80% inactive
        repos_without_description=2,
        newest_repo_age_days=250,  # > 180 days
        oldest_repo_age_days=1200,
        recent_activity_repos=1,
    )
    dummy_repos = [
        RepoInfo(name=f"old-repo-{i}", html_url="", stars=2, forks=0, is_fork=False)
        for i in range(15)
    ]

    roasts = detect_abandoned_museum(metrics, dummy_repos, seed=25)

    assert len(roasts) >= 2
    for r in roasts:
        assert r.category == "Abandoned Museum"
    # Should include savage or medium severity
    assert any(r.severity in ("medium", "savage") for r in roasts)


def test_detect_readme_dreamer() -> None:
    """Test detect_readme_dreamer flags missing descriptions and ambitious titles."""
    metrics = ActivityMetrics(
        total_repos=10,
        original_repos=10,
        forked_repos=0,
        avg_stars=1.0,
        total_stars=10,
        total_forks=0,
        inactive_repos_count=2,
        repos_without_description=8,  # 80% without description
        newest_repo_age_days=10,
        oldest_repo_age_days=300,
        recent_activity_repos=5,
    )
    repos = [
        RepoInfo(name="quantum-ai-cloud-platform", description=None, html_url="", stars=0, forks=0, is_fork=False),
        RepoInfo(name="simple-script", description=None, html_url="", stars=0, forks=0, is_fork=False),
    ]

    roasts = detect_readme_dreamer(metrics, repos, seed=42)

    assert len(roasts) >= 2
    for r in roasts:
        assert r.category == "README Dreamer"
    # Ambitious title roast
    assert any("quantum-ai-cloud-platform" in r.text or "ambitious" in r.factual_basis.lower() for r in roasts)


def test_detect_language_identity() -> None:
    """Test detect_language_identity for language hoppers and single language purists."""
    # Hopper scenario
    hopper_metrics = ActivityMetrics(
        total_repos=8,
        languages=["Python", "Rust", "Go", "TypeScript", "Zig", "Kotlin"],
        inactive_repos_count=0,
        repos_without_description=0,
        newest_repo_age_days=10,
        oldest_repo_age_days=100,
        recent_activity_repos=8,
    )
    hopper_repos = [
        RepoInfo(name=f"r-{i}", language=lang, html_url="", stars=0, forks=0, is_fork=False)
        for i, lang in enumerate(["Python", "Rust", "Go", "TypeScript", "Zig", "Kotlin", "Python", "Rust"])
    ]
    hopper_roasts = detect_language_identity(hopper_metrics, hopper_repos, seed=7)
    assert len(hopper_roasts) > 0
    assert hopper_roasts[0].category == "Language Identity Crisis"

    # Single-language purist scenario
    purist_metrics = ActivityMetrics(
        total_repos=4,
        languages=["Rust"],
        inactive_repos_count=0,
        repos_without_description=0,
        newest_repo_age_days=10,
        oldest_repo_age_days=100,
        recent_activity_repos=4,
    )
    purist_repos = [
        RepoInfo(name=f"r-{i}", language="Rust", html_url="", stars=0, forks=0, is_fork=False)
        for i in range(4)
    ]
    purist_roasts = detect_language_identity(purist_metrics, purist_repos, seed=7)
    assert len(purist_roasts) > 0
    assert "Rust" in purist_roasts[0].text


def test_detect_popularity_department() -> None:
    """Test detect_popularity_department handles zero stars and one-hit wonders."""
    zero_star_metrics = ActivityMetrics(
        total_repos=6,
        avg_stars=0.0,
        total_stars=0,
        languages=["Python"],
    )
    repos = [
        RepoInfo(name=f"repo-{i}", stars=0, forks=0, is_fork=False, html_url="")
        for i in range(6)
    ]
    roasts = detect_popularity_department(zero_star_metrics, repos, seed=99)
    assert len(roasts) > 0
    assert roasts[0].severity == "savage"
    # Check for zero stars mention (word 'Zero' or digit '0') case-insensitively
    fb_lower = roasts[0].factual_basis.lower()
    txt_lower = roasts[0].text.lower()
    assert 'zero' in fb_lower or '0' in fb_lower or 'zero' in txt_lower or ' 0 ' in txt_lower


def test_determinism_same_inputs_same_outputs() -> None:
    """Test that identical seeds and inputs produce deterministic, identical roast text."""
    seed = get_user_seed("TestUser123")
    assert seed == get_user_seed("testuser123")  # Case insensitive seed consistency

    metrics = ActivityMetrics(
        total_repos=12,
        forked_repos=6,
        avg_stars=0.0,
        total_stars=0,
        inactive_repos_count=7,
        repos_without_description=8,
        newest_repo_age_days=200,
        oldest_repo_age_days=900,
        recent_activity_repos=0,
    )
    repos = [
        RepoInfo(name="repo-final-v2", html_url="", stars=0, forks=0, is_fork=True),
        RepoInfo(name="repo-copy", html_url="", stars=0, forks=0, is_fork=True),
    ]

    result1 = detect_repo_chaos(metrics, repos, seed)
    result2 = detect_repo_chaos(metrics, repos, seed)

    assert len(result1) == len(result2)
    for item1, item2 in zip(result1, result2):
        assert item1.text == item2.text
        assert item1.severity == item2.severity
        assert item1.factual_basis == item2.factual_basis
