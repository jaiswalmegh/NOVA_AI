
import threading
from urllib.parse import urlparse

import requests


class APIService:

    def __init__(self, timeout=15):

        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ValueError("Timeout must be a positive number.")

        if timeout <= 0 or timeout > 120:
            raise ValueError("Timeout must be between 1 and 120 seconds.")

        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "NOVA-AI/2.0",
            "Accept": "application/json, text/plain, */*"
        })

        self._lock = threading.RLock()
        self._closed = False

    # =========================================
    # URL VALIDATION
    # =========================================

    def _validate_url(self, url):

        if not isinstance(url, str) or not url.strip():
            return False

        try:

            parsed = urlparse(url.strip())

            return (
                parsed.scheme in ("http", "https")
                and bool(parsed.netloc)
                and bool(parsed.hostname)
            )

        except ValueError:
            return False

    # =========================================
    # GET REQUEST
    # =========================================

    def get(self, url, params=None, headers=None):

        return self._request(
            method="GET",
            url=url,
            params=params,
            headers=headers
        )

    # =========================================
    # POST REQUEST
    # =========================================

    def post(
        self,
        url,
        data=None,
        json_data=None,
        headers=None
    ):

        return self._request(
            method="POST",
            url=url,
            data=data,
            json_data=json_data,
            headers=headers
        )

    # =========================================
    # PUT REQUEST
    # =========================================

    def put(
        self,
        url,
        data=None,
        json_data=None,
        headers=None
    ):

        return self._request(
            method="PUT",
            url=url,
            data=data,
            json_data=json_data,
            headers=headers
        )

    # =========================================
    # DELETE REQUEST
    # =========================================

    def delete(self, url, headers=None):

        return self._request(
            method="DELETE",
            url=url,
            headers=headers
        )

    # =========================================
    # MAIN REQUEST HANDLER
    # =========================================

    def _request(
        self,
        method,
        url,
        params=None,
        data=None,
        json_data=None,
        headers=None
    ):

        if self._closed:
            return self._error("API service is closed.")

        if not self._validate_url(url):
            return self._error("Invalid or unsupported API URL.")

        try:

            with self._lock:

                if self._closed:
                    return self._error("API service is closed.")

                response = self.session.request(
                    method=method,
                    url=url.strip(),
                    params=params,
                    data=data,
                    json=json_data,
                    headers=headers,
                    timeout=self.timeout
                )

            response.raise_for_status()

            try:

                result = response.json()

            except ValueError:

                result = response.text

            return {
                "success": True,
                "status_code": response.status_code,
                "data": result,
                "message": "API request completed successfully."
            }

        except requests.Timeout:

            return self._error(
                "API request timed out. Please try again."
            )

        except requests.HTTPError as error:

            status_code = (
                error.response.status_code
                if error.response is not None
                else None
            )

            return {
                "success": False,
                "status_code": status_code,
                "data": None,
                "message": "The API returned an HTTP error."
            }

        except requests.ConnectionError:

            return self._error(
                "Unable to connect to the API. Check your internet connection."
            )

        except requests.RequestException as error:

            print(f"NOVA API Request Error: {error}")

            return self._error(
                "An API request error occurred."
            )

        except Exception as error:

            print(f"NOVA API Service Error: {error}")

            return self._error(
                "An unexpected API error occurred."
            )

    # =========================================
    # STANDARD ERROR RESPONSE
    # =========================================

    def _error(self, message):

        return {
            "success": False,
            "status_code": None,
            "data": None,
            "message": message
        }

    # =========================================
    # SERVICE STATUS
    # =========================================

    def is_available(self):

        return not self._closed

    # =========================================
    # CLOSE SERVICE
    # =========================================

    def close(self):

        with self._lock:

            if self._closed:
                return

            self.session.close()
            self._closed = True
