"""Catalyst Center API client for authentication and requests."""

import base64
import binascii
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class CatalystCenterAPIClient:
    """Client for interacting with Catalyst Center APIs."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        verify_ssl: bool = False,
    ):
        """Initialize Catalyst Center API client.

        Args:
            base_url: Catalyst Center base URL
            username: Username for authentication
            password: Password for authentication
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.settings = get_settings()
        self.auth_mode = self.settings.catalyst_center_auth_mode.strip().lower()

        # Token-based auth for Catalyst Center
        self.access_token: Optional[str] = None

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            verify=verify_ssl,
            timeout=httpx.Timeout(self.settings.api_timeout),
            follow_redirects=True,
        )

    def _build_basic_authorization(self) -> str:
        """Build a Basic Authorization header value."""
        encoded_auth = self.settings.catalyst_center_encoded_auth
        if encoded_auth:
            encoded_value = encoded_auth.strip()
            if encoded_value.lower().startswith("basic "):
                return encoded_value
            return f"Basic {encoded_value}"

        credentials = f"{self.username}:{self.password}".encode("utf-8")
        encoded_value = base64.b64encode(credentials).decode("ascii")
        return f"Basic {encoded_value}"

    def _get_aes_key_bytes(self) -> bytes:
        """Resolve the configured AES key into a 32-byte value."""
        key_value = self.settings.catalyst_center_aes_key
        if not key_value:
            raise ValueError(
                "CATALYST_CENTER_AES_KEY must be configured when "
                "CATALYST_CENTER_AUTH_MODE=aes256"
            )

        normalized_key = key_value.strip()

        try:
            decoded_hex = bytes.fromhex(normalized_key)
            if len(decoded_hex) == 32:
                return decoded_hex
        except ValueError:
            pass

        try:
            decoded_b64 = base64.b64decode(normalized_key, validate=True)
            if len(decoded_b64) == 32:
                return decoded_b64
        except (binascii.Error, ValueError):
            pass

        raw_key = normalized_key.encode("utf-8")
        if len(raw_key) == 32:
            return raw_key

        raise ValueError(
            "CATALYST_CENTER_AES_KEY must resolve to exactly 32 bytes. "
            "Provide a 32-character raw string, 64-character hex string, or base64-encoded 32-byte value."
        )

    def _build_aes_authorization(self) -> str:
        """Build the Cisco AES Authorization header value."""
        encrypted_credentials = self.settings.catalyst_center_aes_encrypted_credentials
        if encrypted_credentials:
            encrypted_value = encrypted_credentials.strip()
        else:
            credentials = f"{self.username}:{self.password}".encode("utf-8")
            key = self._get_aes_key_bytes()

            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_credentials = padder.update(credentials) + padder.finalize()

            cipher = Cipher(algorithms.AES(key), modes.ECB())
            encryptor = cipher.encryptor()
            encrypted_bytes = encryptor.update(padded_credentials) + encryptor.finalize()
            encrypted_value = base64.b64encode(encrypted_bytes).decode("ascii")

        return f"CSCO-AES-256 credentials={encrypted_value}"

    def _build_token_auth_headers(self) -> Dict[str, str]:
        """Build headers for the Catalyst Center token request."""
        headers = {"Accept": "application/json"}

        if self.auth_mode == "aes256":
            headers["Authorization"] = self._build_aes_authorization()
        else:
            headers["Authorization"] = self._build_basic_authorization()

        return headers

    async def authenticate(self) -> bool:
        """Authenticate with Catalyst Center using Basic Auth.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Catalyst Center token endpoint
            login_url = urljoin(self.base_url, "/dna/system/api/v1/auth/token")

            response = await self.client.post(
                login_url,
                headers=self._build_token_auth_headers(),
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    # API may return either Token or token
                    self.access_token = data.get("Token") or data.get("token")
                    if self.access_token:
                        logger.info("Authentication successful, auth token obtained")
                        return True
                except Exception:
                    logger.error("Authentication response was not valid JSON")

            logger.error(
                "Authentication failed with status %s: %s",
                response.status_code,
                response.text,
            )
            return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make authenticated request to Catalyst Center.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers

        Returns:
            httpx.Response object

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        # Ensure we're authenticated
        if not self.access_token:
            authenticated = await self.authenticate()
            if not authenticated:
                raise RuntimeError("Failed to authenticate with Catalyst Center")

        # Build full URL
        url = urljoin(self.base_url, path.lstrip("/"))

        # Make request with retry logic
        max_retries = self.settings.api_retry_attempts
        last_exception = None

        for attempt in range(max_retries):
            try:
                request_headers = dict(headers or {})
                if self.access_token:
                    request_headers["X-Auth-Token"] = self.access_token

                response = await self.client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json_data,
                    headers=request_headers,
                )

                # Handle 401 by re-authenticating and retrying with a fresh token
                if response.status_code == 401 and attempt < max_retries - 1:
                    logger.warning("Received 401, re-authenticating...")
                    self.access_token = None
                    authenticated = await self.authenticate()
                    if not authenticated:
                        raise RuntimeError("Failed to refresh Catalyst Center auth token")
                    continue

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                    continue
                else:
                    raise

            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"Request error (attempt {attempt + 1}/{max_retries}): {e}")
                    continue
                else:
                    raise

        # If we get here, all retries failed
        if last_exception:
            raise last_exception

    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
