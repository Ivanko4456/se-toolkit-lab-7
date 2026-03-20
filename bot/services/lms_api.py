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
