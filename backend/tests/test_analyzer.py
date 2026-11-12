"""Unit tests for the repository analyzer module."""

from typing import Any, Dict, List
import pytest

from app.analyzer import calculate_metrics, parse_profile_info, parse_repo_info


def test_calculate_metrics_normal(sample_profile_data: Dict[str, Any], sample_repos_data: List[Dict[str, Any]]) -> None:
    """Test calculate_metrics with a realistic collection of diverse repositories."""
    metrics, lang_stats = calculate_metrics(sample_profile_data, sample_repos_data)

    assert metrics.total_repos == 7
    assert metrics.original_repos == 5
    assert metrics.forked_repos == 2
    assert metrics.total_stars == (250 + 15 + 0 + 0 + 0 + 1 + 3)
    assert metrics.avg_stars == round((250 + 15 + 1 + 3) / 7, 2)
    assert metrics.most_starred_repo == "Hello-World"
    assert metrics.most_starred_repo_url == "https://github.com/octocat/Hello-World"
    assert metrics.inactive_repos_count >= 3
    assert metrics.repos_without_description >= 4
    assert metrics.recent_activity_repos >= 2

    # Language checks
    assert len(metrics.languages) == 7
    assert len(lang_stats) == 7
    # Sum of percentages should roughly equal 100%
    total_pct = sum(stat.percentage for stat in lang_stats)
    assert 99.0 <= total_pct <= 101.0


def test_calculate_metrics_empty(sample_profile_data: Dict[str, Any]) -> None:
    """Test calculate_metrics when the user has zero repositories."""
    metrics, lang_stats = calculate_metrics(sample_profile_data, [])

    assert metrics.total_repos == 0
    assert metrics.original_repos == 0
    assert metrics.forked_repos == 0
    assert metrics.avg_stars == 0.0
    assert metrics.total_stars == 0
    assert metrics.most_starred_repo is None
    assert metrics.most_starred_repo_url is None
    assert metrics.languages == []
    assert lang_stats == []
    assert metrics.inactive_repos_count == 0
    assert metrics.repos_without_description == 0
    assert metrics.newest_repo_age_days == 0
    assert metrics.oldest_repo_age_days == 0
    assert metrics.recent_activity_repos == 0


def test_calculate_metrics_all_forked(sample_profile_data: Dict[str, Any]) -> None:
    """Test calculate_metrics when 100% of the repositories are forks."""
    all_forked_repos = [
        {
            "name": f"forked-project-{i}",
            "description": f"Forked repository description number {i}",
            "language": "Python",
            "stargazers_count": 2,
            "forks_count": 0,
            "fork": True,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2026-10-01T12:00:00Z",
            "pushed_at": "2026-10-01T12:00:00Z",
            "html_url": f"https://github.com/octocat/forked-project-{i}",
        }
        for i in range(5)
    ]

    metrics, lang_stats = calculate_metrics(sample_profile_data, all_forked_repos)

    assert metrics.total_repos == 5
    assert metrics.original_repos == 0
    assert metrics.forked_repos == 5
    assert metrics.total_stars == 10
    assert metrics.avg_stars == 2.0


def test_calculate_metrics_language_distribution(sample_profile_data: Dict[str, Any]) -> None:
    """Test that languages are properly counted, ordered desc by count, and percentages are correct."""
    custom_repos = [
        {"name": "p1", "language": "Python", "fork": False, "stargazers_count": 10},
        {"name": "p2", "language": "Python", "fork": False, "stargazers_count": 5},
        {"name": "p3", "language": "Python", "fork": False, "stargazers_count": 0},
        {"name": "ts1", "language": "TypeScript", "fork": False, "stargazers_count": 2},
        {"name": "ts2", "language": "TypeScript", "fork": False, "stargazers_count": 1},
        {"name": "r1", "language": "Rust", "fork": False, "stargazers_count": 8},
        {"name": "no-lang", "language": None, "fork": False, "stargazers_count": 0},
    ]

    metrics, lang_stats = calculate_metrics(sample_profile_data, custom_repos)

    assert metrics.total_repos == 7
    # 6 repos have languages: 3 Python (50%), 2 TypeScript (33.3%), 1 Rust (16.7%)
    assert metrics.languages == ["Python", "TypeScript", "Rust"]
    assert len(lang_stats) == 3
    assert lang_stats[0].language == "Python"
    assert lang_stats[0].count == 3
    assert lang_stats[0].percentage == 50.0

    assert lang_stats[1].language == "TypeScript"
    assert lang_stats[1].count == 2
    assert lang_stats[1].percentage == 33.3

    assert lang_stats[2].language == "Rust"
    assert lang_stats[2].count == 1
    assert lang_stats[2].percentage == 16.7


def test_parse_helpers() -> None:
    """Test parse_profile_info and parse_repo_info model mappings."""
    profile_raw = {"login": "testuser", "name": "Tester", "public_repos": 12}
    profile = parse_profile_info(profile_raw)
    assert profile.username == "testuser"
    assert profile.name == "Tester"
    assert profile.public_repos == 12

    repo_raw = {"name": "test-repo", "stargazers_count": 42, "fork": True}
    repo = parse_repo_info(repo_raw)
    assert repo.name == "test-repo"
    assert repo.stars == 42
    assert repo.is_fork is True
