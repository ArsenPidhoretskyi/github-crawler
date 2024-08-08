import asyncio
import logging
from random import choice
from typing import List, Dict, Optional, Any

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.enums import SearchType
from app.session import GitHubSession


logger = logging.getLogger()


class GithubCrawler:
    LANGUAGE_STATS_SEARCH_ATTRS = {
        "data-ga-click": "Repository, language stats search click, location:repo overview"
    }

    def __init__(self, proxies: List[str]):
        self.__proxies = proxies

        self.__chosen_proxy = self.__get_proxy()

    def __get_proxy(self, excluded_proxy: Optional[str] = None):
        if not self.__proxies:
            logger.warning("No proxies available")
            return

        proxies_to_use = self.__proxies.copy()
        if excluded_proxy:
            proxies_to_use.remove(excluded_proxy)

        if not proxies_to_use:
            logger.warning("No proxies available")
            return

        proxy = choice(proxies_to_use)
        logger.info(f"Using proxy: {proxy}")
        return {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}",
        }

    async def _get(self, endpoint: str, params: Optional[dict] = None):
        try:
            async with GitHubSession(proxy=self.__chosen_proxy) as session:
                async with session.get(endpoint, params=params) as response:
                    return await response.text()

        except Exception as exception:
            logger.exception(f"Exception while _get({endpoint}, params={params}): {exception}")
            raise

    async def _search_on_github(self, keywords: List[str], search_type: SearchType) -> str:
        query = "+".join(keywords)
        params = {
            "q": query,
            "type": search_type.value.lower(),
        }
        response = await self._get("search", params=params)
        return response

    @staticmethod
    def _parse_content(content: str, search_type: SearchType) -> List[str]:
        soup = BeautifulSoup(content, "html.parser")
        return [
            urljoin("https://github.com", item["href"])
            for block in soup.find_all("div", class_=search_type.block_identifier)
            for item in block.find_all("a")
        ]

    async def _get_urls(self, keywords: List[str], search_type: SearchType) -> List[Dict[str, str]]:
        content = await self._search_on_github(keywords, search_type)
        urls = self._parse_content(content, search_type)
        return [{"url": url} for url in urls]

    async def get_repository_information(self, repository_url: str) -> Dict[str, str]:
        response = await self._get(repository_url)
        soup = BeautifulSoup(response, "html.parser")

        languages_stats = {}
        for language_stat in soup.find_all("a", attrs=self.LANGUAGE_STATS_SEARCH_ATTRS):
            language, percentage = language_stat.find_all("span")
            if language and percentage:
                languages_stats[language.get_text(strip=True)] = percentage.get_text(strip=True)

        owner_span = soup.find("span", class_="author flex-self-stretch")
        owner = owner_span.get_text(strip=True) if owner_span else ""
        return {"owner": owner, "language_stats": languages_stats}

    async def __get_with_repository_information(self, repository_url: str) -> Dict[str, str]:
        repository_information = await self.get_repository_information(repository_url)
        return {
            "url": repository_url,
            "extra": repository_information,
        }

    async def crawl(self, keywords: List[str], search_type: SearchType) -> List[Dict[str, Any]]:
        response = await self._get_urls(keywords, search_type)
        if search_type == SearchType.REPOSITORY:
            tasks = [
                asyncio.ensure_future(self.__get_with_repository_information(url_config["url"]))
                for url_config in response
            ]
            response = await asyncio.gather(*tasks)

        return response
