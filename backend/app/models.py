"""Data models for GitHub analysis and roast reports."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class GitHubProfile(BaseModel):
    """Normalized GitHub user profile information."""

    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    html_url: str
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None


class RepoInfo(BaseModel):
    """Detailed summary of an individual repository."""

    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    is_fork: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    html_url: str
    topics: List[str] = Field(default_factory=list)
    size: int = 0


class LanguageStat(BaseModel):
    """Breakdown of language usage across repositories."""

    language: str
    count: int
    percentage: float


class ActivityMetrics(BaseModel):
    """Aggregated activity and distribution metrics across analyzed repositories."""

    total_repos: int = 0
    original_repos: int = 0
    forked_repos: int = 0
    avg_stars: float = 0.0
    total_stars: int = 0
    total_forks: int = 0
    most_starred_repo: Optional[str] = None
    most_starred_repo_url: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    inactive_repos_count: int = 0
    repos_without_description: int = 0
    newest_repo_age_days: int = 0
    oldest_repo_age_days: int = 0
    recent_activity_repos: int = 0


class RoastItem(BaseModel):
    """Individual roast observation."""

    category: str
    text: str
    severity: Literal["mild", "medium", "savage"]
    factual_basis: str


class RoastCategory(BaseModel):
    """A collection of roasts grouped by specific pattern or theme."""

    category_name: str
    roasts: List[RoastItem] = Field(default_factory=list)


class ArchetypeResult(BaseModel):
    """Developer personality archetype determined from analysis."""

    title: str
    description: str
    explanation: str
    confidence: Literal["low", "medium", "high"]


class ScoreBreakdown(BaseModel):
    """Individual factor contributing to the chaos score."""

    factor: str
    score: float
    max_score: float
    explanation: str


class ChaosScore(BaseModel):
    """Overall developer chaos score and contextual interpretation."""

    total: int
    breakdown: List[ScoreBreakdown] = Field(default_factory=list)
    interpretation: str
    disclaimer: str


class PositiveFinding(BaseModel):
    """A genuine or reassuring positive highlight found in the profile."""

    title: str
    description: str


class MostRoastableRepo(BaseModel):
    """The single repository exhibiting the most chaotic traits."""

    name: str
    url: str
    reasons: List[str] = Field(default_factory=list)


class RoastReport(BaseModel):
    """Full comprehensive roast and diagnostic report."""

    profile: GitHubProfile
    activity_metrics: ActivityMetrics
    language_stats: List[LanguageStat] = Field(default_factory=list)
    chaos_score: ChaosScore
    archetype: ArchetypeResult
    roast_categories: List[RoastCategory] = Field(default_factory=list)
    positive_findings: List[PositiveFinding] = Field(default_factory=list)
    most_roastable_repo: Optional[MostRoastableRepo] = None
    warnings: List[str] = Field(default_factory=list)
