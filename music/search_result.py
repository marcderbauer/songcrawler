from dataclasses import dataclass, field

@dataclass
class SearchResult:
    header:list[str]
    rows:list[list[str]]
    uris:list