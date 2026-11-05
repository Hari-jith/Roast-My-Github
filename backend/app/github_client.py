"""GitHub API HTTP client with rate-limit handling and error mapping."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from fastapi import HTTPException

from app.config import settings


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse an ISO format datetime string into a timezone-aware datetime."""
    if not dt_str:
        return None
    try:
        # Standardize 'Z' to UTC offset for compatibility across Python versions
        normalized = dt_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


class GitHubClient:
    """Asynchronous client for interacting with the GitHub REST API."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or settings.GITHUB_TOKEN
        self.headers: Dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RoastMyGitHub-App/1.0",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url="https://api.github.com",
                headers=self.headers,
                timeout=httpx.Timeout(10.0),
            )
        return self._client

    async def __aenter__(self) -> "GitHubClient":
        self._get_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _handle_response_errors(self, response: httpx.Response, username: Optional[str] = None) -> None:
        """Map HTTP error status codes to appropriate FastAPI HTTPExceptions."""
        if response.status_code == 404:
            detail_msg = f"GitHub user '{username}' not found." if username else "Requested GitHub resource not found."
            raise HTTPException(status_code=404, detail=detail_msg)

        if response.status_code in (403, 429):
            remaining = response.headers.get("x-ratelimit-remaining", "")
            if remaining == "0" or response.status_code == 429 or "rate limit" in response.text.lower():
                raise HTTPException(
                    status_code=429,
                    detail="GitHub API rate limit exceeded. Please configure a GITHUB_TOKEN in your environment or try again later.",
                )
            raise HTTPException(
                status_code=403,
                detail="GitHub API access forbidden. Ensure your GITHUB_TOKEN has appropriate permissions.",
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=500,
                detail=f"GitHub API error: HTTP {response.status_code} - {response.text[:200]}",
            )

    async def get_profile(self, username: str) -> Dict[str, Any]:
        """Fetch the public user profile data from GitHub."""
        client = self._get_client()
        try:
            response = await client.get(f"/users/{username}")
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to communicate with GitHub API: {str(exc)}",
            )

        self._handle_response_errors(response, username=username)
        return response.json()

    async def get_repos(self, username: str, max_repos: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch public repositories for the user, paginated up to max_repos."""
        client = self._get_client()
        target_limit = max_repos if max_repos is not None else settings.MAX_REPOS
        all_repos: List[Dict[str, Any]] = []
        page = 1
        per_page = min(100, max(1, target_limit))

        while len(all_repos) < target_limit:
            try:
                response = await client.get(
                    f"/users/{username}/repos",
                    params={
                        "per_page": per_page,
                        "page": page,
                        "sort": "updated",
                        "type": "all",
                    },
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch repositories from GitHub: {str(exc)}",
                )

            self._handle_response_errors(response, username=username)
            page_data = response.json()
            if not isinstance(page_data, list) or len(page_data) == 0:
                break

            all_repos.extend(page_data)

            if len(page_data) < per_page or len(all_repos) >= target_limit:
                break

            page += 1

        return all_repos[:target_limit]

    async def get_recent_commits(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch up to 10 recent commits for a repository, silently catching errors."""
        client = self._get_client()
        try:
            response = await client.get(
                f"/repos/{owner}/{repo}/commits",
                params={"per_page": 10},
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
            return []
        except Exception:
            # Catch errors silently as requested
            return []
