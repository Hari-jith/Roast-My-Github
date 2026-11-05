"""FastAPI application entrypoint for 'Roast My GitHub'."""

import logging
import re
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware

from app.analyzer import calculate_metrics, parse_profile_info, parse_repo_info
from app.archetype import classify_archetype
from app.config import settings
from app.github_client import GitHubClient
from app.models import (
    MostRoastableRepo,
    PositiveFinding,
    RepoInfo,
    RoastCategory,
    RoastReport,
)
from app.roast_engine import (
    detect_abandoned_museum,
    detect_commit_patterns,
    detect_language_identity,
    detect_popularity_department,
    detect_readme_dreamer,
    detect_repo_chaos,
    get_user_seed,
)
from app.scorer import calculate_chaos_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roast_my_github")

# In-memory cache: username.lower() -> (timestamp, RoastReport)
report_cache: Dict[str, Tuple[float, RoastReport]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """App lifespan logging port and configuration on startup."""
    logger.info(f"Starting Roast My GitHub API server on port {settings.PORT}...")
    yield
    logger.info("Shutting down Roast My GitHub API server...")


app = FastAPI(
    title="Roast My GitHub API",
    description="Savage, humorous, and data-driven GitHub profile diagnostic & roast engine.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


def _find_positive_findings(
    metrics, repos_info: List[RepoInfo]
) -> List[PositiveFinding]:
    """Identify genuine positive and reassuring aspects of the developer's profile."""
    positives: List[PositiveFinding] = []

    if metrics.total_stars > 0:
        top_name = metrics.most_starred_repo or "your highlighted project"
        positives.append(
            PositiveFinding(
                title="Recognized Community Work",
                description=(
                    f"Your open-source contributions have earned {metrics.total_stars} star(s), "
                    f"with '{top_name}' leading the pack."
                ),
            )
        )

    if metrics.recent_activity_repos > 5:
        positives.append(
            PositiveFinding(
                title="Active Developer Momentum",
                description=(
                    f"You have actively contributed to {metrics.recent_activity_repos} repositories "
                    "in the last 90 days. Exceptional drive and consistency!"
                ),
            )
        )

    if len(metrics.languages) >= 3:
        top_few = ", ".join(metrics.languages[:4])
        positives.append(
            PositiveFinding(
                title="Polyglot Versatility",
                description=(
                    f"You comfortably span across {len(metrics.languages)} distinct technologies "
                    f"({top_few}), proving strong technical adaptability."
                ),
            )
        )

    well_documented = [
        r for r in repos_info
        if r.description and len(r.description.strip()) >= 25
    ]
    if well_documented:
        positives.append(
            PositiveFinding(
                title="Clean Documentation",
                description=(
                    f"Found {len(well_documented)} project(s) featuring clear, thoughtful descriptions "
                    f"(such as '{well_documented[0].name}')."
                ),
            )
        )

    if not positives:
        positives.append(
            PositiveFinding(
                title="Clean Slate Potential",
                description="A fresh GitHub presence with infinite space to build your next breakthrough.",
            )
        )

    return positives


def _find_most_roastable_repo(repos_info: List[RepoInfo]) -> Optional[MostRoastableRepo]:
    """Find the single repository exhibiting the most chaotic traits."""
    if not repos_info:
        return None

    chaotic_keywords = {"final", "v2", "v3", "new", "old", "updated", "copy", "test", "backup", "demo", "temp"}

    def evaluate_repo(repo: RepoInfo) -> Tuple[int, List[str]]:
        reasons: List[str] = []
        score = 0

        # Missing or tiny description
        if not repo.description or len(repo.description.strip()) < 10:
            score += 2
            reasons.append("Zero or negligible description provided")

        # Chaotic naming
        if any(kw in repo.name.lower() for kw in chaotic_keywords):
            score += 2
            reasons.append("Alarming naming convention ('final', 'v2', 'test', etc.)")

        # Zero stars
        if repo.stars == 0:
            score += 1
            reasons.append("Completely unstarred (0 stars)")

        # Forked
        if repo.is_fork:
            score += 1
            reasons.append("Cloned from someone else's work (fork)")

        return score, reasons

    ranked_repos = [(evaluate_repo(r), r) for r in repos_info]
    ranked_repos.sort(key=lambda item: -item[0][0])

    top_eval, top_repo = ranked_repos[0]
    top_score, top_reasons = top_eval

    if not top_reasons:
        top_reasons = ["Selected by consensus as prime roast material"]

    return MostRoastableRepo(
        name=top_repo.name,
        url=top_repo.html_url,
        reasons=top_reasons,
    )


@app.get("/api/roast/{username}", response_model=RoastReport)
async def get_github_roast(
    username: str = Path(..., description="GitHub username to inspect and roast"),
) -> RoastReport:
    """Analyze a GitHub user's profile and generate a comprehensive diagnostic roast report."""
    # 1. Validate username format
    username_clean = username.strip()
    if not re.match(r"^[a-zA-Z0-9-]{1,39}$", username_clean):
        raise HTTPException(
            status_code=422,
            detail="Invalid GitHub username format. Allowed: 1-39 alphanumeric characters or hyphens.",
        )

    cache_key = username_clean.lower()
    now_ts = time.time()

    # 2. Check in-memory cache
    if cache_key in report_cache:
        cached_ts, cached_report = report_cache[cache_key]
        if now_ts - cached_ts < settings.CACHE_TTL_SECONDS:
            logger.info(f"Serving cached roast report for '{username_clean}'")
            return cached_report

    # 3. Fetch data from GitHub API
    github_client = GitHubClient()
    try:
        profile_data = await github_client.get_profile(username_clean)
        repos_data = await github_client.get_repos(username_clean, max_repos=settings.MAX_REPOS)
    finally:
        await github_client.close()

    # 4. Calculate metrics and parse models
    profile = parse_profile_info(profile_data)
    repos_info = [parse_repo_info(r) for r in repos_data]
    metrics, language_stats = calculate_metrics(profile_data, repos_data)

    seed = get_user_seed(username_clean)

    # 5. Execute roast detectors
    categories_raw = [
        ("Repository Chaos", detect_repo_chaos(metrics, repos_info, seed)),
        ("Abandoned Museum", detect_abandoned_museum(metrics, repos_info, seed)),
        ("README Dreamer", detect_readme_dreamer(metrics, repos_info, seed)),
        ("Language Identity", detect_language_identity(metrics, repos_info, seed)),
        ("Popularity Department", detect_popularity_department(metrics, repos_info, seed)),
        ("Commit Patterns", detect_commit_patterns(metrics, repos_info, seed)),
    ]

    roast_categories: List[RoastCategory] = [
        RoastCategory(category_name=cat_name, roasts=roasts)
        for cat_name, roasts in categories_raw
        if roasts
    ]

    # 6. Highlights and personality assessments
    positive_findings = _find_positive_findings(metrics, repos_info)
    most_roastable = _find_most_roastable_repo(repos_info)
    archetype = classify_archetype(metrics, repos_info, language_stats, seed)
    chaos_score = calculate_chaos_score(metrics, repos_info, seed)

    warnings: List[str] = []
    if len(repos_data) >= settings.MAX_REPOS:
        warnings.append(f"Analysis was limited to the top {settings.MAX_REPOS} most recently updated repositories.")
    if metrics.total_repos == 0:
        warnings.append("User has no public repositories available for complete analysis.")

    # 7. Assemble report
    report = RoastReport(
        profile=profile,
        activity_metrics=metrics,
        language_stats=language_stats,
        chaos_score=chaos_score,
        archetype=archetype,
        roast_categories=roast_categories,
        positive_findings=positive_findings,
        most_roastable_repo=most_roastable,
        warnings=warnings,
    )

    # 8. Cache report
    report_cache[cache_key] = (now_ts, report)

    return report
