import os
import httpx


class FacilityClient:
    """Client to validate facility existence via Facility service."""

    def __init__(self):
        self.base_url = os.getenv("FACILITY_SERVICE_URL")

    def ensure_exists(self, facility_id: int):
        if not self.base_url:
            return  # Skip validation if not configured
        url = f"{self.base_url.rstrip('/')}/facility/{facility_id}"
        try:
            resp = httpx.get(url, timeout=5)
            if resp.status_code == 404:
                raise ValueError("Facility not found")
            resp.raise_for_status()
        except Exception as exc:
            raise ValueError(f"Cannot validate facility: {exc}")
