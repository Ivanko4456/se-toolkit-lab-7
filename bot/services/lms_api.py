"""
LMS API client.

Makes HTTP requests to the LMS backend with Bearer token authentication.
Handles errors gracefully and returns structured data.
"""

import httpx

from config import LMS_API_URL, LMS_API_KEY


class LMSAPIError(Exception):
    """Exception raised when LMS API request fails."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


def _get_client() -> httpx.Client:
    """Create an HTTP client with LMS API configuration."""
    return httpx.Client(
        base_url=LMS_API_URL,
        headers={"Authorization": f"Bearer {LMS_API_KEY}"},
        timeout=10.0,
    )


def get_items() -> list[dict]:
    """
    Fetch all items (labs and tasks) from the LMS backend.

    Returns:
        List of items (labs/tasks).

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/items/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def get_health() -> dict:
    """
    Check backend health by fetching items.

    Returns:
        Dict with 'healthy' status and 'item_count'.

    Raises:
        LMSAPIError: If the request fails.
    """
    items = get_items()
    return {"healthy": True, "item_count": len(items)}


def get_pass_rates(lab_id: str) -> list[dict]:
    """
    Fetch pass rates for a specific lab.

    Args:
        lab_id: The lab identifier (e.g., "lab-04").

    Returns:
        List of pass rate records with task names and percentages.

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/analytics/pass-rates", params={"lab": lab_id})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise LMSAPIError(f"lab '{lab_id}' not found") from e
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def get_learners() -> list[dict]:
    """
    Fetch list of enrolled learners.

    Returns:
        List of learner records.

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/learners/")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def get_scores(lab_id: str) -> list[dict]:
    """
    Fetch score distribution for a lab (4 buckets).

    Args:
        lab_id: The lab identifier.

    Returns:
        List of score distribution records.

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/analytics/scores", params={"lab": lab_id})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def get_timeline(lab_id: str) -> list[dict]:
    """
    Fetch submissions timeline for a lab.

    Args:
        lab_id: The lab identifier.

    Returns:
        List of timeline records (submissions per day).

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/analytics/timeline", params={"lab": lab_id})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def get_groups(lab_id: str) -> list[dict]:
    """
    Fetch per-group performance for a lab.

    Args:
        lab_id: The lab identifier.

    Returns:
        List of group performance records.

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/analytics/groups", params={"lab": lab_id})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def get_top_learners(lab_id: str, limit: int = 5) -> list[dict]:
    """
    Fetch top N learners for a lab.

    Args:
        lab_id: The lab identifier.
        limit: Number of top learners to return.

    Returns:
        List of top learner records.

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/analytics/top-learners", params={"lab": lab_id, "limit": limit})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def get_completion_rate(lab_id: str) -> dict:
    """
    Fetch completion rate for a lab.

    Args:
        lab_id: The lab identifier.

    Returns:
        Dict with completion rate percentage.

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.get("/analytics/completion-rate", params={"lab": lab_id})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e


def trigger_sync() -> dict:
    """
    Trigger ETL sync pipeline.

    Returns:
        Dict with sync status.

    Raises:
        LMSAPIError: If the request fails.
    """
    try:
        with _get_client() as client:
            response = client.post("/pipeline/sync", json={})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise LMSAPIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}") from e
    except httpx.ConnectError as e:
        raise LMSAPIError(f"connection refused ({LMS_API_URL}). Check that the services are running.") from e
    except httpx.TimeoutException as e:
        raise LMSAPIError(f"request timed out ({LMS_API_URL})") from e
    except Exception as e:
        raise LMSAPIError(f"unexpected error: {e}") from e
