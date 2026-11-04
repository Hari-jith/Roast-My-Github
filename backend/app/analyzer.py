"""Repository analyzer for extracting activity metrics and language distributions."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.github_client import parse_datetime
from app.models import ActivityMetrics, GitHubProfile, LanguageStat, RepoInfo


def parse_profile_info(profile_data: Dict[str, Any]) -> GitHubProfile:
    """Normalize raw GitHub user profile dictionary into GitHubProfile model."""
    return GitHubProfile(
        username=profile_data.get("login") or profile_data.get("username", "unknown"),
        name=profile_data.get("name"),
        bio=profile_data.get("bio"),
        avatar_url=profile_data.get("avatar_url"),
        html_url=profile_data.get("html_url", f"https://github.com/{profile_data.get('login', '')}"),
        public_repos=profile_data.get("public_repos", 0),
        followers=profile_data.get("followers", 0),
        following=profile_data.get("following", 0),
        created_at=profile_data.get("created_at"),
        location=profile_data.get("location"),
        company=profile_data.get("company"),
        blog=profile_data.get("blog"),
    )


def parse_repo_info(repo_data: Dict[str, Any]) -> RepoInfo:
    """Normalize raw GitHub repository dictionary into RepoInfo model."""
    return RepoInfo(
        name=repo_data.get("name", "untitled"),
        description=repo_data.get("description"),
        language=repo_data.get("language"),
        stars=repo_data.get("stargazers_count", 0),
        forks=repo_data.get("forks_count", 0),
        is_fork=bool(repo_data.get("fork", False)),
        created_at=repo_data.get("created_at"),
        updated_at=repo_data.get("updated_at") or repo_data.get("pushed_at"),
        html_url=repo_data.get("html_url", ""),
        topics=repo_data.get("topics") or [],
        size=repo_data.get("size", 0),
    )


def calculate_metrics(
    profile_data: Dict[str, Any], repos_data: List[Dict[str, Any]]
) -> Tuple[ActivityMetrics, List[LanguageStat]]:
    """Analyze profile and repositories data to compute metrics and language statistics.

    Returns:
        A tuple of (ActivityMetrics, List[LanguageStat]).
    """
    total_repos = len(repos_data)
    now = datetime.now(timezone.utc)

    if total_repos == 0:
        empty_metrics = ActivityMetrics(
            total_repos=0,
            original_repos=0,
            forked_repos=0,
            avg_stars=0.0,
            total_stars=0,
            total_forks=0,
            most_starred_repo=None,
            most_starred_repo_url=None,
            languages=[],
            inactive_repos_count=0,
            repos_without_description=0,
            newest_repo_age_days=0,
            oldest_repo_age_days=0,
            recent_activity_repos=0,
        )
        return empty_metrics, []

    original_count = 0
    forked_count = 0
    total_stars = 0
    total_forks = 0
    inactive_count = 0
    no_desc_count = 0
    recent_activity_count = 0

    language_counts: Dict[str, int] = {}
    created_datetimes: List[datetime] = []
    max_stars = -1
    best_repo_name: Optional[str] = None
    best_repo_url: Optional[str] = None

    for repo in repos_data:
        # Fork vs original
        is_fork = bool(repo.get("fork", False))
        if is_fork:
            forked_count += 1
        else:
            original_count += 1

        # Stars & Forks
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        total_stars += stars
        total_forks += forks

        # Most starred repository
        if stars > max_stars:
            max_stars = stars
            best_repo_name = repo.get("name")
            best_repo_url = repo.get("html_url")

        # Description quality (missing or < 10 characters)
        desc = repo.get("description")
        if not desc or len(desc.strip()) < 10:
            no_desc_count += 1

        # Language tracking
        lang = repo.get("language")
        if lang and isinstance(lang, str) and lang.strip():
            cleaned_lang = lang.strip()
            language_counts[cleaned_lang] = language_counts.get(cleaned_lang, 0) + 1

        # Activity dates
        # Use updated_at or pushed_at (whichever is later)
        up_dt = parse_datetime(repo.get("updated_at"))
        push_dt = parse_datetime(repo.get("pushed_at"))
        latest_active = max(filter(None, [up_dt, push_dt]), default=None)

        if latest_active:
            days_since_update = (now - latest_active).days
            if days_since_update > 365:
                inactive_count += 1
            if days_since_update <= 90:
                recent_activity_count += 1
        else:
            # If no date, consider inactive
            inactive_count += 1

        # Repo age tracking
        c_dt = parse_datetime(repo.get("created_at"))
        if c_dt:
            created_datetimes.append(c_dt)

    # Calculate repo age
    if created_datetimes:
        newest_date = max(created_datetimes)
        oldest_date = min(created_datetimes)
        newest_repo_age_days = max(0, (now - newest_date).days)
        oldest_repo_age_days = max(0, (now - oldest_date).days)
    else:
        newest_repo_age_days = 0
        oldest_repo_age_days = 0

    # Calculate language percentages
    total_lang_repos = sum(language_counts.values())
    sorted_langs = sorted(language_counts.items(), key=lambda item: (-item[1], item[0]))
    language_stats: List[LanguageStat] = []
    languages_list: List[str] = []

    for lang_name, count in sorted_langs:
        pct = round((count / total_lang_repos) * 100, 1) if total_lang_repos > 0 else 0.0
        language_stats.append(
            LanguageStat(language=lang_name, count=count, percentage=pct)
        )
        languages_list.append(lang_name)

    avg_stars = round(total_stars / max(total_repos, 1), 2)

    metrics = ActivityMetrics(
        total_repos=total_repos,
        original_repos=original_count,
        forked_repos=forked_count,
        avg_stars=avg_stars,
        total_stars=total_stars,
        total_forks=total_forks,
        most_starred_repo=best_repo_name if (max_stars > 0 or total_repos > 0) else None,
        most_starred_repo_url=best_repo_url if (max_stars > 0 or total_repos > 0) else None,
        languages=languages_list,
        inactive_repos_count=inactive_count,
        repos_without_description=no_desc_count,
        newest_repo_age_days=newest_repo_age_days,
        oldest_repo_age_days=oldest_repo_age_days,
        recent_activity_repos=recent_activity_count,
    )

    return metrics, language_stats
