"""Unit tests for the chaos score calculator module."""

import pytest
from app.models import ActivityMetrics, RepoInfo
from app.scorer import calculate_chaos_score


def test_high_chaos_scenario() -> None:
    """Test chaos score calculation for a profile exhibiting maximum chaotic behaviors."""
    metrics = ActivityMetrics(
        total_repos=20,
        original_repos=4,
        forked_repos=16,  # 80% forks
        avg_stars=0.0,    # 0 stars
        total_stars=0,
        total_forks=0,
        inactive_repos_count=18,  # 90% inactive
        repos_without_description=19,  # 95% without description
        newest_repo_age_days=400,
        oldest_repo_age_days=1500,
        recent_activity_repos=0,
    )
    chaotic_repos = [
        RepoInfo(
            name=f"test-project-final-v{i}",
            description=None,
            language="Python",
            stars=0,
            forks=0,
            is_fork=True,
            html_url=f"https://github.com/user/test-project-final-v{i}",
        )
        for i in range(20)
    ]

    score = calculate_chaos_score(metrics, chaotic_repos, seed=42)

    assert score.total >= 80
    assert 0 <= score.total <= 100
    assert "MAXIMUM CHAOS" in score.interpretation
    assert "joke metric" in score.disclaimer.lower()


def test_low_chaos_scenario() -> None:
    """Test chaos score calculation for an exceptionally clean, well-maintained profile."""
    metrics = ActivityMetrics(
        total_repos=10,
        original_repos=10,
        forked_repos=0,   # 0% forks
        avg_stars=25.0,   # High stars
        total_stars=250,
        total_forks=50,
        inactive_repos_count=0,  # 0% inactive
        repos_without_description=0,  # 0% missing desc
        newest_repo_age_days=15,
        oldest_repo_age_days=500,
        recent_activity_repos=10,
    )
    clean_repos = [
        RepoInfo(
            name=f"production-service-{i}",
            description="Comprehensive enterprise microservice architecture with documentation.",
            language="Go",
            stars=25,
            forks=5,
            is_fork=False,
            html_url=f"https://github.com/user/production-service-{i}",
        )
        for i in range(10)
    ]

    score = calculate_chaos_score(metrics, clean_repos, seed=42)

    assert score.total <= 20
    assert 0 <= score.total <= 100
    assert "robot" in score.interpretation.lower()


def test_score_range_and_breakdown_factors() -> None:
    """Test that score is always clamped to 0-100 and breakdown contains all expected factors."""
    # Test with empty repository profile
    empty_metrics = ActivityMetrics(
        total_repos=0,
        original_repos=0,
        forked_repos=0,
        avg_stars=0.0,
        total_stars=0,
        total_forks=0,
        inactive_repos_count=0,
        repos_without_description=0,
        newest_repo_age_days=0,
        oldest_repo_age_days=0,
        recent_activity_repos=0,
    )

    empty_score = calculate_chaos_score(empty_metrics, [], seed=123)
    assert empty_score.total == 0

    expected_factors = {
        "Repo Naming Chaos",
        "Abandonment Rate",
        "Missing Documentation",
        "Fork Ratio",
        "Low Engagement",
    }

    factor_names = {b.factor for b in empty_score.breakdown}
    assert factor_names == expected_factors
    assert sum(b.max_score for b in empty_score.breakdown) == 100.0


def test_moderate_chaos_tier() -> None:
    """Test that moderate chaos values map to appropriate middle score bands."""
    metrics = ActivityMetrics(
        total_repos=10,
        original_repos=8,
        forked_repos=2,
        avg_stars=1.5,
        total_stars=15,
        total_forks=2,
        inactive_repos_count=4,
        repos_without_description=3,
        newest_repo_age_days=50,
        oldest_repo_age_days=400,
        recent_activity_repos=3,
    )
    repos = [
        RepoInfo(
            name=f"my-app-{i}",
            description="A regular web application" if i < 7 else None,
            language="JavaScript",
            stars=1,
            forks=0,
            is_fork=(i >= 8),
            html_url=f"https://github.com/user/my-app-{i}",
        )
        for i in range(10)
    ]

    score = calculate_chaos_score(metrics, repos, seed=99)
    assert 20 <= score.total <= 70
    assert len(score.breakdown) == 5
