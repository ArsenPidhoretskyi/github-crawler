import logging
from typing import Optional

from aiohttp import ClientSession, ClientResponse
from urllib.parse import urljoin


logger = logging.getLogger()


class GitHubSession(ClientSession):
    BASE_URL = "https://github.com"

    def __init__(self, *args, proxy: Optional[dict], **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            }
        )

        super().__init__(*args, **kwargs, headers=headers)

        self.proxy = proxy

    async def _request(self, method: str, url: str, *args, **kwargs) -> ClientResponse:  # type: ignore[override]
        if not url.startswith("http"):
            url = urljoin(self.BASE_URL, url)

        kwargs.setdefault("proxy", self.proxy)

        logger.info(f"Requesting {url}")
        response = await super()._request(method, url, *args, **kwargs)
        return response
