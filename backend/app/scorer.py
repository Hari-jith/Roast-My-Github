"""Chaos score calculator analyzing developer GitHub entropy."""

from typing import List
from app.models import ActivityMetrics, ChaosScore, RepoInfo, ScoreBreakdown


def calculate_chaos_score(
    metrics: ActivityMetrics,
    repos: List[RepoInfo],
    seed: int = 0,
) -> ChaosScore:
    """Calculate the comprehensive chaos score based on 5 weighted anti-patterns.

    Factors (total max 100):
    1. Repo naming chaos (0-20): chaotic keywords, duplicated prefixes
    2. Abandonment rate (0-25): % inactive repositories
    3. Missing documentation (0-20): % repositories without descriptive README/summary
    4. Fork ratio (0-15): % forked repositories
    5. Low engagement (0-20): inverse star density ratio
    """
    total_repos = metrics.total_repos
    breakdown: List[ScoreBreakdown] = []

    if total_repos == 0:
        breakdown = [
            ScoreBreakdown(
                factor="Repo Naming Chaos",
                score=0.0,
                max_score=20.0,
                explanation="No repositories found to evaluate naming conventions.",
            ),
            ScoreBreakdown(
                factor="Abandonment Rate",
                score=0.0,
                max_score=25.0,
                explanation="No repositories found to track activity dormancy.",
            ),
            ScoreBreakdown(
                factor="Missing Documentation",
                score=0.0,
                max_score=20.0,
                explanation="No repositories present to assess documentation.",
            ),
            ScoreBreakdown(
                factor="Fork Ratio",
                score=0.0,
                max_score=15.0,
                explanation="No forks detected in empty repository list.",
            ),
            ScoreBreakdown(
                factor="Low Engagement",
                score=0.0,
                max_score=20.0,
                explanation="No projects available for engagement measurement.",
            ),
        ]
        return ChaosScore(
            total=0,
            breakdown=breakdown,
            interpretation="Your GitHub is suspiciously organized. Are you a robot?",
            disclaimer="This score is a joke metric and does not measure programming ability, intelligence, or worth as a developer.",
        )

    # 1. Repo naming chaos (0-20)
    chaotic_keywords = {"final", "v2", "v3", "new", "old", "updated", "copy", "test", "backup"}
    chaotic_named_repos = [
        r.name for r in repos
        if any(kw in r.name.lower() for kw in chaotic_keywords)
    ]
    name_chaos_ratio = min(1.0, len(chaotic_named_repos) / max(total_repos, 1))

    # Repetition check (prefixes)
    prefix_counts = {}
    for r in repos:
        parts = [p for p in r.name.replace("_", "-").split("-") if p]
        if parts and len(parts[0]) >= 3:
            first_word = parts[0].lower()
            prefix_counts[first_word] = prefix_counts.get(first_word, 0) + 1
    has_repeated_prefix = any(c >= 3 for c in prefix_counts.values())

    naming_score = round(min(20.0, (name_chaos_ratio * 15.0) + (5.0 if has_repeated_prefix else 0.0)), 1)
    breakdown.append(
        ScoreBreakdown(
            factor="Repo Naming Chaos",
            score=naming_score,
            max_score=20.0,
            explanation=(
                f"Identified {len(chaotic_named_repos)} repo(s) with panic versioning or backup names"
                f"{' and repetitive naming prefixes' if has_repeated_prefix else ''}."
            ),
        )
    )

    # 2. Abandonment rate (0-25)
    abandonment_ratio = metrics.inactive_repos_count / max(total_repos, 1)
    abandonment_score = round(min(25.0, abandonment_ratio * 25.0), 1)
    breakdown.append(
        ScoreBreakdown(
            factor="Abandonment Rate",
            score=abandonment_score,
            max_score=25.0,
            explanation=f"{metrics.inactive_repos_count} of {total_repos} ({round(abandonment_ratio * 100)}%) repos inactive for >365 days.",
        )
    )

    # 3. Missing documentation (0-20)
    no_desc_ratio = metrics.repos_without_description / max(total_repos, 1)
    documentation_score = round(min(20.0, no_desc_ratio * 20.0), 1)
    breakdown.append(
        ScoreBreakdown(
            factor="Missing Documentation",
            score=documentation_score,
            max_score=20.0,
            explanation=f"{metrics.repos_without_description} of {total_repos} ({round(no_desc_ratio * 100)}%) repos have minimal or missing descriptions.",
        )
    )

    # 4. Fork ratio (0-15)
    fork_ratio = metrics.forked_repos / max(total_repos, 1)
    fork_score = round(min(15.0, fork_ratio * 15.0), 1)
    breakdown.append(
        ScoreBreakdown(
            factor="Fork Ratio",
            score=fork_score,
            max_score=15.0,
            explanation=f"{metrics.forked_repos} of {total_repos} ({round(fork_ratio * 100)}%) repos are forks from other authors.",
        )
    )

    # 5. Low engagement (0-20)
    # Higher stars per repo reduces chaos; zero stars equals max chaos (20.0)
    if metrics.avg_stars >= 5.0:
        engagement_score = 0.0
    else:
        engagement_score = round((1.0 - (metrics.avg_stars / 5.0)) * 20.0, 1)
    engagement_score = min(20.0, max(0.0, engagement_score))
    breakdown.append(
        ScoreBreakdown(
            factor="Low Engagement",
            score=engagement_score,
            max_score=20.0,
            explanation=f"Average star density of {metrics.avg_stars} stars/repo across {total_repos} projects.",
        )
    )

    # Total score clamped to 0-100
    raw_total = sum(item.score for item in breakdown)
    final_total = max(0, min(100, int(round(raw_total))))

    # Interpretations by score tier
    if final_total <= 20:
        interpretation = "Your GitHub is suspiciously organized. Are you a robot?"
    elif final_total <= 40:
        interpretation = "Mild chaos. A few skeletons in the closet, but who's counting?"
    elif final_total <= 60:
        interpretation = "Certified GitHub goblin. Your repo list tells a story of hope and abandonment."
    elif final_total <= 80:
        interpretation = "Chaotic neutral developer. Your commit history is a choose-your-own-adventure."
    else:
        interpretation = "MAXIMUM CHAOS. The GitHub gods weep. Your repos are a beautiful disaster."

    return ChaosScore(
        total=final_total,
        breakdown=breakdown,
        interpretation=interpretation,
        disclaimer="This score is a joke metric and does not measure programming ability, intelligence, or worth as a developer.",
    )
