import time
import requests
from typing import Any, Dict, List, Optional


class JQuantsClient:
    """
    J-Quants API V2 client.

    V2 uses:
      Header: x-api-key: <api_key>

    Daily equity bars endpoint:
      GET https://api.jquants.com/v2/equities/bars/daily

    Note:
      V2 usually expects 5-digit security code.
      Example:
        4661  -> 46610
        7203  -> 72030
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.jquants.com",
        api_version: str = "v2",
        timeout: int = 30,
        rate_limit_sleep: float = 0.2,
    ) -> None:
        if not api_key or api_key == "PUT_YOUR_JQUANTS_API_KEY_HERE":
            raise ValueError("J-Quants API key is missing. Set it in config/config.json.")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version.strip("/")
        self.timeout = timeout
        self.rate_limit_sleep = rate_limit_sleep

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "jquants-mt4-stock-importer/1.0",
        }

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.api_version}/{path.lstrip('/')}"
        resp = requests.get(url, headers=self.headers, params=params or {}, timeout=self.timeout)
        if resp.status_code >= 400:
            raise RuntimeError(
                f"J-Quants API error {resp.status_code}: {resp.text[:1000]}\n"
                f"URL: {resp.url}"
            )
        time.sleep(self.rate_limit_sleep)
        return resp.json()

    @staticmethod
    def normalize_code_for_v2(code: str) -> str:
        """
        J-Quants V2 examples use 5-digit security codes.
        If user enters 4-digit TSE code, append 0.
        """
        code = str(code).strip()
        if len(code) == 4 and code.isdigit():
            return code + "0"
        return code

    def get_daily_quotes(
        self,
        code: str,
        date: Optional[str] = None,
        from_: Optional[str] = None,
        to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch daily stock prices from V2 endpoint.

        Endpoint:
          /v2/equities/bars/daily

        Response generally includes:
          {"daily_quotes": [...], "pagination_key": "..."}
        """
        endpoint = "equities/bars/daily"

        code = self.normalize_code_for_v2(code)

        params: Dict[str, Any] = {"code": code}
        if date:
            params["date"] = date
        if from_:
            params["from"] = from_
        if to:
            params["to"] = to

        rows: List[Dict[str, Any]] = []
        pagination_key = None

        while True:
            page_params = dict(params)
            if pagination_key:
                page_params["pagination_key"] = pagination_key

            payload = self._get(endpoint, page_params)

            page_rows = (
                payload.get("daily_quotes")
                or payload.get("data")
                or payload.get("quotes")
                or []
            )
            if not isinstance(page_rows, list):
                raise RuntimeError(f"Unexpected response shape: {payload}")

            rows.extend(page_rows)

            pagination_key = payload.get("pagination_key") or payload.get("next_page_token")
            if not pagination_key:
                break

        return rows
