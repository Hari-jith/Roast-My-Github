"""Developer personality archetype classifier based on GitHub behavioral patterns."""

from typing import List
from app.models import ActivityMetrics, ArchetypeResult, LanguageStat, RepoInfo


def classify_archetype(
    metrics: ActivityMetrics,
    repos: List[RepoInfo],
    language_stats: List[LanguageStat],
    seed: int = 0,
) -> ArchetypeResult:
    """Classify the developer archetype by testing behavioral patterns in priority order.

    Order of evaluation:
    1. The Tutorial Collector (>50% forked repos)
    2. The Abandoned Project Museum Curator (>60% inactive repos and total > 10)
    3. The Framework Hopper (>5 languages, no dominant language > 40%)
    4. The Repository Hoarder (total_repos > 30 and low avg stars)
    5. The One-Project Perfectionist (1-3 repos with high stars >= 5)
    6. The Documentation Optimist (>70% repos without descriptions but avg stars > 1)
    7. The Quietly Competent Developer (active repos >= 3, decent stars >= 5, diverse langs >= 2)
    8. The Ghost Committer (repos exist, zero recent activity, oldest repo > 365 days)
    Default: The Aspiring Developer
    """
    total = metrics.total_repos

    # 1. 'The Tutorial Collector': >50% forked repos
    if total > 0 and (metrics.forked_repos / total) > 0.50:
        fork_pct = round((metrics.forked_repos / total) * 100)
        confidence = "high" if fork_pct > 70 else "medium"
        return ArchetypeResult(
            title="The Tutorial Collector",
            description=(
                "You possess an uncanny ability to click 'Fork' on popular repositories and convince "
                "yourself that you will study the source code this weekend. Your GitHub is less of a workshop "
                "and more of an unorganized open-source warehouse. At least your hoarding instincts are well-intentioned!"
            ),
            explanation=(
                f"{fork_pct}% of your repositories ({metrics.forked_repos} of {total}) are forks "
                "of other people's projects."
            ),
            confidence=confidence,
        )

    # 2. 'The Abandoned Project Museum Curator': >60% inactive repos and total > 10
    if total > 10 and (metrics.inactive_repos_count / total) > 0.60:
        inactive_pct = round((metrics.inactive_repos_count / total) * 100)
        confidence = "high" if inactive_pct > 80 else "medium"
        return ArchetypeResult(
            title="The Abandoned Project Museum Curator",
            description=(
                "You are the chief curator of an expansive museum of forgotten ambitions and discarded side projects. "
                "Every repository started with immense Sunday afternoon enthusiasm before being permanently abandoned "
                "by Tuesday evening. Visitors are respectfully requested not to disturb the digital cobwebs."
            ),
            explanation=(
                f"{metrics.inactive_repos_count} of your {total} repositories ({inactive_pct}%) "
                "have not received a commit or update in over 365 days."
            ),
            confidence=confidence,
        )

    # 3. 'The Framework Hopper': >5 languages, no dominant language (>40%)
    if len(metrics.languages) > 5 and all(stat.percentage <= 40.0 for stat in language_stats):
        confidence = "high" if len(metrics.languages) > 7 else "medium"
        langs_str = ", ".join(metrics.languages[:5])
        return ArchetypeResult(
            title="The Framework Hopper",
            description=(
                "You suffer from severe shiny-new-toy syndrome. As soon as a brand new framework trends "
                "on Hacker News, you initialize a repo, write 'Hello World', and immediately lose interest. "
                "Your tech stack is simply whatever library was released fifteen minutes ago."
            ),
            explanation=(
                f"You have projects across {len(metrics.languages)} distinct languages ({langs_str}...), "
                "with no single language accounting for more than 40% of your work."
            ),
            confidence=confidence,
        )

    # 4. 'The Repository Hoarder': total_repos > 30 and low avg stars (< 1.0)
    if total > 30 and metrics.avg_stars < 1.0:
        confidence = "high" if total > 50 else "medium"
        return ArchetypeResult(
            title="The Repository Hoarder",
            description=(
                "You treat Git repositories like free samples at Costco—you take every single one whether you need it or not. "
                "You have accumulated a sprawling mountain of repos that have long outlived their initial fleeting purpose. "
                "Marie Kondo would weep uncontrollably looking at your repository overview."
            ),
            explanation=(
                f"You have spawned {total} repositories while averaging only {metrics.avg_stars} stars per repo, "
                f"totaling {metrics.total_stars} stars across the entire collection."
            ),
            confidence=confidence,
        )

    # 5. 'The One-Project Perfectionist': 1-3 repos with high stars (>= 5)
    if 1 <= total <= 3 and metrics.total_stars >= 5:
        confidence = "high" if metrics.total_stars >= 20 else "medium"
        return ArchetypeResult(
            title="The One-Project Perfectionist",
            description=(
                "You do not start new repositories lightly. Instead, you pour your heart, soul, and endless refactors "
                "into a tiny handful of creations that have actually caught the eyes of other developers. "
                "Quality over quantity is your sacred creed, even if it borders on obsessive."
            ),
            explanation=(
                f"You maintain a laser-focused portfolio of only {total} repository{'ies' if total > 1 else ''}, "
                f"which have earned a respectable total of {metrics.total_stars} stars."
            ),
            confidence=confidence,
        )

    # 6. 'The Documentation Optimist': >70% repos without descriptions but avg stars > 1
    if total > 0 and (metrics.repos_without_description / total) > 0.70 and metrics.avg_stars > 1.0:
        no_desc_pct = round((metrics.repos_without_description / total) * 100)
        return ArchetypeResult(
            title="The Documentation Optimist",
            description=(
                "You genuinely believe code is 100% self-documenting and that README files are for the weak. "
                "Why bother explaining what your code does when people can just decipher your raw commits? "
                "People somehow still star your work, probably hoping that instructions will appear in the next release."
            ),
            explanation=(
                f"{no_desc_pct}% of your repositories ({metrics.repos_without_description} of {total}) "
                f"lack any description, yet you hold an average of {metrics.avg_stars} stars."
            ),
            confidence="medium",
        )

    # 7. 'The Quietly Competent Developer': active repos >= 3, decent stars >= 5, diverse langs >= 2
    if metrics.recent_activity_repos >= 3 and metrics.total_stars >= 5 and len(metrics.languages) >= 2:
        return ArchetypeResult(
            title="The Quietly Competent Developer",
            description=(
                "Against all statistical probability, your GitHub profile looks like it belongs to someone "
                "who actually builds reliable, functional software. You have ongoing commits, a sensible technology mix, "
                "and undeniable signs of life. We are genuinely disappointed we cannot roast you harder."
            ),
            explanation=(
                f"{metrics.recent_activity_repos} repositories updated in the last 90 days, "
                f"{metrics.total_stars} total stars, and active code across {len(metrics.languages)} programming languages."
            ),
            confidence="medium",
        )

    # 8. 'The Ghost Committer': all repos very old, no recent activity
    if total > 0 and metrics.recent_activity_repos == 0 and metrics.oldest_repo_age_days > 365:
        confidence = "high" if metrics.oldest_repo_age_days > 730 else "medium"
        return ArchetypeResult(
            title="The Ghost Committer",
            description=(
                "You were once an active citizen of the GitHub ecosystem, but now only your spectral footprints remain. "
                "You haven't pushed a commit in months, leaving your projects in permanent suspended animation. "
                "Did you land a comfortable enterprise job or simply remember that the outside world has sunlight?"
            ),
            explanation=(
                f"Your account holds {total} repositories dating back {metrics.oldest_repo_age_days} days, "
                "yet not a single repository has seen activity in the past 90 days."
            ),
            confidence=confidence,
        )

    # Default fallback: The Aspiring Developer
    return ArchetypeResult(
        title="The Aspiring Developer",
        description=(
            "You are standing at the starting gates of your software development journey. "
            "Your profile is still taking shape, waiting for that signature project or chaotic late-night hackathon build. "
            "The world of open source is yours to conquer—now go commit some code!"
        ),
        explanation=(
            f"Currently tracks {total} repository{'ies' if total != 1 else ''} across {len(metrics.languages)} language(s) "
            f"with {metrics.total_stars} total star(s)."
        ),
        confidence="low",
    )
