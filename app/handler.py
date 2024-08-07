import json
import logging
import asyncio
from typing import List, Optional

from app.enums import SearchType
from app.crawler import GithubCrawler


logging.getLogger().setLevel(logging.INFO)


async def handle(keywords: List[str], search_type: SearchType, proxies: Optional[List[str]]) -> List[dict]:
    crawler = GithubCrawler(proxies)
    return await crawler.crawl(keywords, search_type)


if __name__ == "__main__":
    input_data = {
        "keywords": ["openstack", "nova", "css"],
        "proxies": [],  # ["171.231.28.200:49236", "181.188.27.162:8080"],
        "search_type": SearchType.REPOSITORY,
    }

    content = asyncio.run(handle(**input_data))
    print(json.dumps(content, indent=2))
