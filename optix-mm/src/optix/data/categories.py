"""Map Kalshi event-ticker prefixes to high-level categories.

Becker's published analysis uses a similar mapping from his
src/analysis/kalshi/util/categories.py. This is a compact local copy
sufficient for v0; expand from his table as new prefixes appear.

Reference: Becker (2026), category gap table reproduced below as
ground-truth for the strategy filter.

Category gaps (maker - taker, percentage points):
  WorldEvents    7.32   -- top extraction, lowest volume
  Media          7.28
  Entertainment  4.79
  Crypto         2.69
  Weather        2.57
  Sports         2.23   -- 72% of total volume
  Politics       1.02
  Finance        0.17   -- already efficient, do not trade
"""

from __future__ import annotations

# Prefix -> category. A reasonable starting set; cross-check against the
# Kalshi event browser when new series are listed.
PREFIX_CATEGORY: dict[str, str] = {
    # Sports
    "NFLGAME": "Sports",
    "NBAGAME": "Sports",
    "MLBGAME": "Sports",
    "NHLGAME": "Sports",
    "EPL": "Sports",
    "UCL": "Sports",
    "WCFINAL": "Sports",
    "OPENGOLF": "Sports",
    "MASTERS": "Sports",
    "TENNISWIN": "Sports",
    "F1RACE": "Sports",
    # Politics
    "PRES": "Politics",
    "POTUS": "Politics",
    "SENATE": "Politics",
    "HOUSE": "Politics",
    "GOV": "Politics",
    "FEDCHAIR": "Politics",
    # Crypto
    "KXBTC": "Crypto",
    "KXETH": "Crypto",
    "KXSOL": "Crypto",
    "BTC": "Crypto",
    "ETH": "Crypto",
    # Weather
    "HIGHNY": "Weather",
    "LOWNY": "Weather",
    "RAINNYC": "Weather",
    "SNOWNYC": "Weather",
    "HURRICANE": "Weather",
    "TORNADO": "Weather",
    # Finance — explicitly excluded
    "SPX": "Finance",
    "NDX": "Finance",
    "FED": "Finance",
    "CPI": "Finance",
    "JOBS": "Finance",
    "GDP": "Finance",
    # Entertainment
    "OSCARS": "Entertainment",
    "EMMYS": "Entertainment",
    "GRAMMY": "Entertainment",
    "BOXOFFICE": "Entertainment",
    # Media / culture
    "TWEETCOUNT": "Media",
    "VIDEOVIEWS": "Media",
    "CHARTNUM1": "Media",
    # World events (geopolitics, etc.)
    "WAR": "WorldEvents",
    "CEASEFIRE": "WorldEvents",
    "DIPLOMACY": "WorldEvents",
    "ELECTION": "WorldEvents",
}

# Documented gap from Becker (2026) Table; used for sizing decisions.
CATEGORY_GAP_PP: dict[str, float] = {
    "WorldEvents": 7.32,
    "Media": 7.28,
    "Entertainment": 4.79,
    "Crypto": 2.69,
    "Weather": 2.57,
    "Sports": 2.23,
    "Politics": 1.02,
    "Finance": 0.17,
}


def category_for_event_ticker(event_ticker: str | None) -> str:
    """Return the inferred category, defaulting to 'Other' when prefix unknown."""
    if not event_ticker:
        return "Other"
    # The Kalshi convention has the series prefix before any '-'.
    head = event_ticker.split("-", 1)[0].upper()
    return PREFIX_CATEGORY.get(head, "Other")


def is_target_category(category: str, target_set: set[str]) -> bool:
    """Strategy filter: trade only categories with documented extraction gap."""
    return category in target_set and category != "Finance"
