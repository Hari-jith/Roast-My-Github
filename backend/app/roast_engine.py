"""Rule-based roast generator analyzing GitHub behavioral anti-patterns."""

import hashlib
from typing import List
from app.models import ActivityMetrics, RepoInfo, RoastItem


def get_user_seed(username: str) -> int:
    """Generate a deterministic integer seed from a username."""
    digest = hashlib.md5(username.lower().encode("utf-8")).hexdigest()
    return int(digest, 16) % 1000


def detect_repo_chaos(
    metrics: ActivityMetrics, repos: List[RepoInfo], seed: int
) -> List[RoastItem]:
    """Detect chaotic naming schemes, excessive forking, and repo duplication."""
    roasts: List[RoastItem] = []
    category = "Repository Chaos"

    # Rule 1: Repos with chaotic versioning/naming keywords
    chaotic_keywords = {"final", "v2", "v3", "new", "old", "updated", "copy", "test", "backup"}
    chaotic_repos = [
        r.name for r in repos
        if any(kw in r.name.lower() for kw in chaotic_keywords)
    ]
    if len(chaotic_repos) >= 2:
        count = len(chaotic_repos)
        samples = ", ".join(f"'{name}'" for name in chaotic_repos[:3])
        templates = [
            f"Your naming convention is basically a digital crime scene. Found {count} repos with panic keywords like 'final', 'v2', or 'test' (including {samples}). Pure 'project-final-final-v2' energy.",
            f"You have {count} repositories screaming existential version crises ({samples}). Git branches were invented so you wouldn't have to keep naming repos 'new-test-v2'.",
            f"Repo names like {samples} ({count} total) prove you don't use version control; you use emotional desperation.",
            f"Naming {count} repos with suffixes like 'copy', 'old', or 'updated' ({samples}) suggests your backup strategy is just 'pray and duplicate'."
        ]
        chosen = templates[(seed + 0) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="medium",
                factual_basis=f"Found {count} repositories containing versioning keywords like 'final', 'v2', 'copy', or 'test'.",
            )
        )

    # Rule 2: Excessive forking (> 30% forks)
    if metrics.total_repos > 0 and (metrics.forked_repos / metrics.total_repos) > 0.3:
        fork_pct = round((metrics.forked_repos / metrics.total_repos) * 100)
        templates = [
            f"{fork_pct}% of your repositories ({metrics.forked_repos} of {metrics.total_repos}) are forks. You're not an open-source contributor; you're a digital hoarder of other people's intellectual property.",
            f"With {metrics.forked_repos} forked repos ({fork_pct}% of your profile), your GitHub is less of a portfolio and more of an unorganized Pinterest board for code.",
            f"Forking {metrics.forked_repos} repos doesn't mean you're contributing to open source, it just means you know where the 'Fork' button is located.",
            f"{fork_pct}% fork ratio! You collect repositories the way tourists collect brochures at the airport—intending to read them, but never doing so."
        ]
        chosen = templates[(seed + 1) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="savage" if fork_pct > 60 else "medium",
                factual_basis=f"{metrics.forked_repos} out of {metrics.total_repos} ({fork_pct}%) repositories are forks.",
            )
        )

    # Rule 3: Low engagement with many repos (total_repos > 20 and avg_stars < 0.5)
    if metrics.total_repos > 20 and metrics.avg_stars < 0.5:
        templates = [
            f"You have {metrics.total_repos} repositories and an average of {metrics.avg_stars} stars. Your code is sitting in full witness protection.",
            f"{metrics.total_repos} repos and your average star count is {metrics.avg_stars}. Even automated GitHub spam bots are ignoring your profile.",
            f"You've launched {metrics.total_repos} projects for an average of {metrics.avg_stars} stars. Talk about relentless dedication to total obscurity.",
            f"An army of {metrics.total_repos} repos and barely {metrics.total_stars} stars total. You're broadcasting on a frequency no one is tuned into."
        ]
        chosen = templates[(seed + 2) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="savage",
                factual_basis=f"Average stars per repo is {metrics.avg_stars} across {metrics.total_repos} repositories.",
            )
        )

    # Rule 4: Repetitive prefixes (>= 3 repos share same prefix)
    prefix_counts = {}
    for r in repos:
        parts = [p for p in r.name.replace("_", "-").split("-") if p]
        if parts and len(parts[0]) >= 3:
            first_word = parts[0].lower()
            prefix_counts[first_word] = prefix_counts.get(first_word, 0) + 1

    frequent_prefix = next((p for p, c in prefix_counts.items() if c >= 3), None)
    if frequent_prefix:
        p_count = prefix_counts[frequent_prefix]
        p_samples = ", ".join(f"'{r.name}'" for r in repos if r.name.lower().startswith(frequent_prefix))[:60]
        templates = [
            f"You have {p_count} repositories starting with '{frequent_prefix}' ({p_samples}...). Did you get stuck in a creative loop or just lose your backspace key?",
            f"The '{frequent_prefix}' franchise is {p_count} repos deep. Even the Fast & Furious movies know when to move on to a new title.",
            f"Repetition alert: {p_count} repositories kicking off with '{frequent_prefix}'. Variety is the spice of life, but you're serving plain white rice.",
            f"Why write one '{frequent_prefix}' repo when you can spawn {p_count} of them? That's not a portfolio, that's a stutter."
        ]
        chosen = templates[(seed + 3) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="mild",
                factual_basis=f"{p_count} repositories share the prefix '{frequent_prefix}'.",
            )
        )

    return roasts


def detect_abandoned_museum(
    metrics: ActivityMetrics, repos: List[RepoInfo], seed: int
) -> List[RoastItem]:
    """Detect dormant repositories and digital museum characteristics."""
    roasts: List[RoastItem] = []
    category = "Abandoned Museum"

    # Rule 1: Inactive repos count >= 5
    if metrics.inactive_repos_count >= 5:
        severity_level = "savage" if metrics.inactive_repos_count > 10 else "medium"
        templates = [
            f"{metrics.inactive_repos_count} repositories haven't seen a single commit in over 365 days. Your profile belongs in the Smithsonian.",
            f"There are {metrics.inactive_repos_count} zombie repositories rotting on your profile. The last time anyone touched them, the world was a different place.",
            f"Digital cobwebs everywhere: {metrics.inactive_repos_count} repos have been completely untouched for over a full calendar year.",
            f"You're curating an exhibit of {metrics.inactive_repos_count} prehistoric projects. Even Indiana Jones would need a torch to find your latest commit."
        ]
        chosen = templates[(seed + 0) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity=severity_level,
                factual_basis=f"{metrics.inactive_repos_count} repositories have had no activity for over 365 days.",
            )
        )

    # Rule 2: Inactive ratio > 60%
    if metrics.total_repos > 0 and (metrics.inactive_repos_count / metrics.total_repos) > 0.6:
        inactive_pct = round((metrics.inactive_repos_count / metrics.total_repos) * 100)
        templates = [
            f"{inactive_pct}% of your code base is officially abandoned ({metrics.inactive_repos_count}/{metrics.total_repos} repos). You start things with fiery passion and finish them with complete silence.",
            f"Over {inactive_pct}% of your repositories are dormant relics. If your GitHub were a restaurant, the health inspector would have condemned it years ago.",
            f"An abandonment rate of {inactive_pct}%! Your GitHub profile is essentially a graveyard of forgotten Saturday afternoon inspirations.",
            f"{inactive_pct}% abandoned rate. You don't have git commit history; you have an autopsy report of discarded ideas."
        ]
        chosen = templates[(seed + 1) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="savage",
                factual_basis=f"{inactive_pct}% of total repositories have been inactive for over 1 year.",
            )
        )

    # Rule 3: Newest repo age > 180 days
    if metrics.total_repos > 0 and metrics.newest_repo_age_days > 180:
        templates = [
            f"Your newest repository is already {metrics.newest_repo_age_days} days old. Are you currently coding in secret, or did you give up on software entirely?",
            f"It has been {metrics.newest_repo_age_days} days since you last spawned a new project. Even Halley's Comet visits with more regularity.",
            f"Zero new projects in the last {metrics.newest_repo_age_days} days. You've officially entered the GitHub hibernation era.",
            f"No new repository for {metrics.newest_repo_age_days} days. Your keyboard must feel so neglected."
        ]
        chosen = templates[(seed + 2) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="medium",
                factual_basis=f"The most recently created repository is {metrics.newest_repo_age_days} days old.",
            )
        )

    return roasts


def detect_readme_dreamer(
    metrics: ActivityMetrics, repos: List[RepoInfo], seed: int
) -> List[RoastItem]:
    """Detect undocumented repositories and grandiose titles without substance."""
    roasts: List[RoastItem] = []
    category = "README Dreamer"

    # Rule 1: repos_without_description > 5
    if metrics.repos_without_description > 5:
        templates = [
            f"{metrics.repos_without_description} repositories have zero description. You treat your projects like mystery grab bags that nobody wants to open.",
            f"You left {metrics.repos_without_description} repos completely undocumented. Apparently, explaining what your code does is beneath your artistic vision.",
            f"{metrics.repos_without_description} repositories with no descriptions. The CIA has fewer redacted files than your repo list.",
            f"You created {metrics.repos_without_description} repos and couldn't be bothered to write one sentence about what they do. Truly a minimalist."
        ]
        chosen = templates[(seed + 0) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="medium",
                factual_basis=f"{metrics.repos_without_description} repositories have missing or trivial (<10 char) descriptions.",
            )
        )

    # Rule 2: repos_without_description / total_repos > 0.5
    if metrics.total_repos > 0 and (metrics.repos_without_description / metrics.total_repos) > 0.5:
        no_desc_pct = round((metrics.repos_without_description / metrics.total_repos) * 100)
        templates = [
            f"{no_desc_pct}% of your repositories have no description whatsoever. If you don't know what they do, how could anyone else?",
            f"More than half your portfolio ({no_desc_pct}%) lacks any explanation. Are these secret government algorithms or did you just forget after 20 minutes?",
            f"With {no_desc_pct}% undocumented repos, browsing your profile is like walking into an unlabeled spice cabinet.",
            f"Over {no_desc_pct}% of your projects have no documentation. You write code like it's a confidential trade secret."
        ]
        chosen = templates[(seed + 1) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="savage",
                factual_basis=f"{no_desc_pct}% of repositories lack any description.",
            )
        )

    # Rule 3: Ambitious names but no description
    ambitious_keywords = ["ai", "engine", "platform", "system", "next", "super", "cloud", "framework", "quantum", "algo", "blockchain", "bot", "uber", "gpt"]
    ambitious_undoc = [
        r.name for r in repos
        if any(ak in r.name.lower() for ak in ambitious_keywords)
        and (not r.description or len(r.description.strip()) < 10)
    ]
    if ambitious_undoc:
        ambitious_sample = ambitious_undoc[0]
        templates = [
            f"Repos like '{ambitious_sample}' sound like billion-dollar Series A startups, yet contain exactly zero words of explanation.",
            f"You named a repository '{ambitious_sample}' and couldn't even spare 5 seconds to type a README. Silicon Valley vaporware at its finest.",
            f"Grand title, zero documentation: '{ambitious_sample}' promised the revolution but delivered an empty void.",
            f"'{ambitious_sample}' sounds revolutionary until you click inside and find a solitary blank file."
        ]
        chosen = templates[(seed + 2) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="mild",
                factual_basis=f"Repository '{ambitious_sample}' has an ambitious name but lacks documentation.",
            )
        )

    return roasts


def detect_language_identity(
    metrics: ActivityMetrics, repos: List[RepoInfo], seed: int
) -> List[RoastItem]:
    """Detect language hopping or obsessive single-language usage."""
    roasts: List[RoastItem] = []
    category = "Language Identity Crisis"

    lang_count = len(metrics.languages)

    # Rule 1: > 5 languages and no language > 40%
    if lang_count > 5:
        # Check if dominant language <= 40%
        # Language distribution can be checked from repos
        repo_langs = [r.language for r in repos if r.language]
        max_lang_share = max((repo_langs.count(l) / len(repo_langs) for l in set(repo_langs)), default=0) if repo_langs else 0
        if max_lang_share <= 0.40:
            top_langs = ", ".join(metrics.languages[:4])
            templates = [
                f"You use {lang_count} different languages and not one crosses 40% of your work. You don't master languages; you just speed-date tech stacks.",
                f"{lang_count} programming languages across your repos with zero commitment. You have software developer commitment issues.",
                f"Your stack includes {top_langs} and more ({lang_count} total). You're a jack of all trades, master of copy-pasting tutorials.",
                f"With {lang_count} languages on display, your GitHub looks less like a resume and more like the Tower of Babel."
            ]
            chosen = templates[(seed + 0) % len(templates)]
            roasts.append(
                RoastItem(
                    category=category,
                    text=chosen,
                    severity="medium",
                    factual_basis=f"Employs {lang_count} languages ({top_langs}...) with no single language exceeding 40% share.",
                )
            )

    # Rule 2: Only 1 language across all repos
    if lang_count == 1 and metrics.total_repos >= 2:
        only_lang = metrics.languages[0]
        templates = [
            f"100% of your repos are in {only_lang}. Your comfort zone isn't just a comfort zone; it's a reinforced concrete bunker.",
            f"Pure {only_lang} purist across all {metrics.total_repos} repos! Rumor has it you get hives if you see syntax from any other language.",
            f"You've written strictly {only_lang} across every single project. Loyalty or fear of learning new syntax? We respect the stubbornness.",
            f"All {metrics.total_repos} repos in {only_lang}. If {only_lang} ever gets deprecated, your entire career goes down with it."
        ]
        chosen = templates[(seed + 1) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="mild",
                factual_basis=f"All {metrics.total_repos} repositories are written strictly in {only_lang}.",
            )
        )

    # Rule 3: Specific language combos get specific jokes
    langs_lower = {l.lower() for l in metrics.languages}
    # HTML/CSS only
    if langs_lower and langs_lower.issubset({"html", "css", "scss", "sass"}):
        templates = [
            "You've only written HTML and CSS. You're not programming yet, you're just arranging digital living room furniture!",
            "Pure HTML and CSS profile: 'Web dev curious' who still thinks centering a div counts as high-concurrency systems engineering.",
            "All markup and styling, zero business logic. Your buttons look gorgeous, they just don't do anything when clicked.",
            "HTML and CSS only. You're living proof that you can build 10 websites without writing a single 'if' statement."
        ]
        chosen = templates[(seed + 2) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="mild",
                factual_basis="Profile contains strictly HTML/CSS styling with no computational languages.",
            )
        )
    elif langs_lower and langs_lower.issubset({"python", "jupyter notebook"}):
        templates = [
            "Just Python and Jupyter Notebooks. Your definition of deployment is clicking 'Restart Kernel and Run All Cells'.",
            "A portfolio of Python scripts and notebooks. Somewhere out there, an unhandled exception is crying in an untitled.ipynb file.",
            "Data science enthusiast detected: 100% Python and notebooks, 0% production readiness.",
            "Your entire engineering philosophy: import pandas, import matplotlib, and pray the memory leak doesn't crash Chrome."
        ]
        chosen = templates[(seed + 2) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="mild",
                factual_basis="Profile consists exclusively of Python and Jupyter Notebook files.",
            )
        )

    return roasts


def detect_popularity_department(
    metrics: ActivityMetrics, repos: List[RepoInfo], seed: int
) -> List[RoastItem]:
    """Detect engagement, zero-star situations, and one-hit wonders."""
    roasts: List[RoastItem] = []
    category = "Popularity Department"

    # Rule 1: total_stars == 0
    if metrics.total_stars == 0 and metrics.total_repos > 0:
        templates = [
            f"You have accumulated a grand total of ZERO stars across {metrics.total_repos} repositories. Even GitHub's auto-generated welcoming bot didn't star your work.",
            f"Zero stars across {metrics.total_repos} repos. Your code isn't just private; it's practically classified by the Department of Defense.",
            f"A crisp 0 stars. Not even your mom or your alt account gave you a sympathy star.",
            f"{metrics.total_repos} repositories, 0 stars. If a tree falls in the forest and no one stars it, did you really code it?"
        ]
        chosen = templates[(seed + 0) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="savage",
                factual_basis=f"Zero stars accumulated across all {metrics.total_repos} repositories.",
            )
        )

    # Rule 2: total_stars < 5 and total_repos > 10
    elif metrics.total_stars < 5 and metrics.total_repos > 10:
        templates = [
            f"You've built {metrics.total_repos} repositories and only gathered {metrics.total_stars} stars. That's an ROI of sadness.",
            f"{metrics.total_repos} repos for a combined total of {metrics.total_stars} stars. You are the indie acoustic band playing to an empty coffee shop.",
            f"With {metrics.total_stars} stars across {metrics.total_repos} projects, you're averaging {metrics.avg_stars} stars per repo. The silence is deafening.",
            f"You've pushed {metrics.total_repos} repos into the void and came back with {metrics.total_stars} stars. Talk about screaming into the abyss."
        ]
        chosen = templates[(seed + 1) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="medium",
                factual_basis=f"{metrics.total_stars} total stars earned across {metrics.total_repos} repositories.",
            )
        )

    # Rule 3: 1 repo with >> 10x avg stars (one-hit wonder)
    max_stars = max((r.stars for r in repos), default=0)
    if metrics.total_repos >= 3 and max_stars >= 10 and max_stars >= (10 * metrics.avg_stars):
        repo_name = metrics.most_starred_repo or "your top repo"
        templates = [
            f"Classic one-hit wonder: '{repo_name}' has {max_stars} stars, while your entire rest of your profile sits in total darkness.",
            f"'{repo_name}' is carrying your entire GitHub reputation on its fragile shoulders ({max_stars} out of {metrics.total_stars} stars).",
            f"You peaked on '{repo_name}' ({max_stars} stars) and have been chasing that dopamine dragon ever since.",
            f"One project has {max_stars} stars, and the rest have tumbleweeds. You're the developer equivalent of Gotye."
        ]
        chosen = templates[(seed + 2) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="medium",
                factual_basis=f"Repository '{repo_name}' holds {max_stars} stars, exceeding 10x the profile average ({metrics.avg_stars}).",
            )
        )

    return roasts


def detect_commit_patterns(
    metrics: ActivityMetrics, repos: List[RepoInfo], seed: int
) -> List[RoastItem]:
    """Detect inactivity windows and ghost commits."""
    roasts: List[RoastItem] = []
    category = "Commit Patterns"

    # Rule 1: recent_activity_repos == 0 but has repos
    if metrics.total_repos > 0 and metrics.recent_activity_repos == 0:
        templates = [
            "Zero repositories updated in the last 90 days. Your contribution graph looks like a flatline on an EKG monitor.",
            "0 active repos in 3 months. Are you retired, in witness protection, or did you switch careers to artisanal sourdough baking?",
            f"Not a single commit across all {metrics.total_repos} repos in the last 90 days. GitHub is sending out search and rescue teams.",
            "Complete radio silence for 90+ days. The green squares on your contribution graph have turned to dust."
        ]
        chosen = templates[(seed + 0) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="savage",
                factual_basis="0 repositories updated in the last 90 days.",
            )
        )

    # Rule 2: oldest_repo > 1000 days and recent_activity < 3
    if metrics.oldest_repo_age_days > 1000 and metrics.recent_activity_repos < 3:
        templates = [
            f"Your account spans over {metrics.oldest_repo_age_days} days, yet you only have {metrics.recent_activity_repos} active repos recently. Truly a digital antique store.",
            f"You've been on GitHub for {metrics.oldest_repo_age_days} days and have {metrics.recent_activity_repos} active repos to show for it. Senior developer status without the commits.",
            f"A {metrics.oldest_repo_age_days}-day old account with barely {metrics.recent_activity_repos} active repos. A living monument to ancient coding epochs.",
            f"Over {metrics.oldest_repo_age_days} days on GitHub and only {metrics.recent_activity_repos} active repos. You're a tenured professor who stopped giving lectures."
        ]
        chosen = templates[(seed + 1) % len(templates)]
        roasts.append(
            RoastItem(
                category=category,
                text=chosen,
                severity="medium",
                factual_basis=f"Oldest repository is {metrics.oldest_repo_age_days} days old with only {metrics.recent_activity_repos} active repos in the last 90 days.",
            )
        )

    return roasts
