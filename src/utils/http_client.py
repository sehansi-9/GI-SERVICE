from aiohttp import ClientSession, ClientTimeout, TCPConnector
from typing import Optional
import os

class HTTPClient:
    "Single HTTP client for the application"

    def __init__(self):
        self._session: Optional[ClientSession] = None
        self.timeout = ClientTimeout(total=90, connect=30, sock_connect=30, sock_read=90)
        
        # Connection pool configuration
        # For resource-constrained environments (0.5 CPU, 350MB RAM)
        self.pool_size = int(os.getenv("HTTP_POOL_SIZE", "50"))
        self.pool_size_per_host = int(os.getenv("HTTP_POOL_SIZE_PER_HOST", "40"))

    async def start(self):
        """Create session on app startup"""
        if self._session is None or self._session.closed:
            # Configure TCPConnector with connection pool limits
            connector = TCPConnector(
                limit=self.pool_size,  # Max total connections
                limit_per_host=self.pool_size_per_host,  # Max per backend host
                ttl_dns_cache=300,  # DNS cache TTL in seconds
                force_close=False,  # Reuse connections
                enable_cleanup_closed=True  # Clean up closed connections
            )
            self._session = ClientSession(
                timeout=self.timeout,
                connector=connector
            )

    async def close(self):
        """Close session on app shutdown"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    @property
    def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError("HTTP client not initialized")
        return self._session

# Create a global instance
http_client = HTTPClient()