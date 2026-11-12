"""Pytest fixtures and mock client configurations for test suites."""

from typing import Any, Dict, List
from unittest.mock import AsyncMock
import pytest


@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Realistic GitHub user profile payload for 'octocat'."""
    return {
        "login": "octocat",
        "name": "The Octocat",
        "bio": "GitHub mascot and enthusiastic octo-coder.",
        "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
        "html_url": "https://github.com/octocat",
        "public_repos": 7,
        "followers": 15000,
        "following": 9,
        "created_at": "2011-01-25T18:44:36Z",
        "location": "San Francisco",
        "company": "@github",
        "blog": "https://github.blog",
    }


@pytest.fixture
def sample_repos_data() -> List[Dict[str, Any]]:
    """Diverse collection of 7 realistic GitHub repositories covering varied scenarios."""
    return [
        {
            "name": "Hello-World",
            "description": "My first and greatest repository with comprehensive documentation.",
            "language": "Python",
            "stargazers_count": 250,
            "forks_count": 45,
            "fork": False,
            "created_at": "2012-03-01T10:00:00Z",
            "updated_at": "2026-10-20T12:00:00Z",
            "pushed_at": "2026-10-20T12:00:00Z",
            "html_url": "https://github.com/octocat/Hello-World",
            "topics": ["intro", "beginner"],
            "size": 1024,
        },
        {
            "name": "Spoon-Knife",
            "description": "Well-known tutorial fork repository.",
            "language": "HTML",
            "stargazers_count": 15,
            "forks_count": 2,
            "fork": True,
            "created_at": "2013-05-10T14:30:00Z",
            "updated_at": "2023-01-15T09:00:00Z",  # Inactive (> 365 days)
            "pushed_at": "2023-01-15T09:00:00Z",
            "html_url": "https://github.com/octocat/Spoon-Knife",
            "topics": ["tutorial"],
            "size": 512,
        },
        {
            "name": "octo-app-final-v2",
            "description": None,  # Missing description
            "language": "JavaScript",
            "stargazers_count": 0,
            "forks_count": 0,
            "fork": False,
            "created_at": "2022-01-10T08:00:00Z",
            "updated_at": "2022-02-01T10:00:00Z",  # Inactive
            "pushed_at": "2022-02-01T10:00:00Z",
            "html_url": "https://github.com/octocat/octo-app-final-v2",
            "topics": [],
            "size": 128,
        },
        {
            "name": "octo-app-test-copy",
            "description": "test",  # Minimal description < 10 chars
            "language": "TypeScript",
            "stargazers_count": 0,
            "forks_count": 0,
            "fork": False,
            "created_at": "2022-02-15T11:00:00Z",
            "updated_at": "2022-03-01T14:00:00Z",  # Inactive
            "pushed_at": "2022-03-01T14:00:00Z",
            "html_url": "https://github.com/octocat/octo-app-test-copy",
            "topics": [],
            "size": 256,
        },
        {
            "name": "octo-app-backup",
            "description": "",  # Empty description
            "language": "Go",
            "stargazers_count": 0,
            "forks_count": 0,
            "fork": False,
            "created_at": "2022-04-01T09:00:00Z",
            "updated_at": "2022-04-10T12:00:00Z",  # Inactive
            "pushed_at": "2022-04-10T12:00:00Z",
            "html_url": "https://github.com/octocat/octo-app-backup",
            "topics": [],
            "size": 64,
        },
        {
            "name": "quantum-ai-engine",
            "description": None,  # Ambitious title with no description
            "language": "Rust",
            "stargazers_count": 1,
            "forks_count": 0,
            "fork": False,
            "created_at": "2026-08-15T16:00:00Z",
            "updated_at": "2026-10-15T17:00:00Z",  # Recent activity
            "pushed_at": "2026-10-15T17:00:00Z",
            "html_url": "https://github.com/octocat/quantum-ai-engine",
            "topics": ["ai"],
            "size": 2048,
        },
        {
            "name": "styling-tricks",
            "description": "Experimental styling widgets and effects.",
            "language": "CSS",
            "stargazers_count": 3,
            "forks_count": 1,
            "fork": True,
            "created_at": "2026-06-01T10:00:00Z",
            "updated_at": "2026-09-20T12:00:00Z",  # Recent activity
            "pushed_at": "2026-09-20T12:00:00Z",
            "html_url": "https://github.com/octocat/styling-tricks",
            "topics": ["css"],
            "size": 300,
        },
    ]


@pytest.fixture
def mock_github_client(sample_profile_data: Dict[str, Any], sample_repos_data: List[Dict[str, Any]]) -> AsyncMock:
    """Mock GitHubClient instance returning sample profile and repository data."""
    client = AsyncMock()
    client.get_profile = AsyncMock(return_value=sample_profile_data)
    client.get_repos = AsyncMock(return_value=sample_repos_data)
    client.get_recent_commits = AsyncMock(return_value=[])
    client.close = AsyncMock()
    return client
