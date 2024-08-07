from enum import StrEnum


class SearchType(StrEnum):
    REPOSITORY = "repositories"
    ISSUE = "issues"
    WIKI = "wikis"

    @property
    def block_identifier(self) -> str:
        mapping = {
            SearchType.REPOSITORY: "search-title",
            SearchType.ISSUE: "search-title",
            SearchType.WIKI: "search-title",
        }
        return mapping[self]
