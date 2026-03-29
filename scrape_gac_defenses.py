"""
swgoh.gg GAC Counters Scraper
Scrapes GAC defense counter data for Season 75, merges pages, and ranks by win %.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://swgoh.gg/gac/counters/season/CHAMPIONSHIPS_GRAND_ARENA_GA2_EVENT_SEASON_75/"
PAGES = [BASE_URL, BASE_URL + "?page=2"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TOP_N = 30


# ---------------------------------------------------------------------------
# Scraping helpers
# ---------------------------------------------------------------------------

def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a URL and return a BeautifulSoup object."""
    print(f"[fetch] GET {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    print(f"[fetch] status={resp.status_code}, content-length={len(resp.content)}")
    return BeautifulSoup(resp.text, "html.parser")


def parse_defenses(soup: BeautifulSoup) -> list[dict]:
    """
    Parse defense rows from one page of the GAC counters table.

    The page renders a table (or a list of cards) with columns such as:
        Defense | Counters | Wins | Attempts | Win %
    We inspect the raw HTML to find the right selector and column names.
    """
    rows = []

    # --- attempt 1: standard <table> ---
    table = soup.find("table")
    if table:
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        print(f"[parse] table headers: {headers}")
        for i, tr in enumerate(table.find("tbody").find_all("tr")):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if i < 3:
                print(f"[debug] raw row {i}: {cells}")
            if cells:
                rows.append(dict(zip(headers, cells)))
        return rows

    # --- attempt 2: card / div-based layout ---
    # Adjust selectors based on the actual HTML structure you observe in debug output.
    cards = soup.select(".gac-counter-row, .counter-row, [data-defense]")
    if cards:
        print(f"[parse] found {len(cards)} card elements")
        for i, card in enumerate(cards):
            text = card.get_text(separator="|", strip=True)
            if i < 3:
                print(f"[debug] raw card {i}: {text}")
            # TODO: map card fields once structure is confirmed
            rows.append({"raw": text})
        return rows

    # --- fallback: dump first 2000 chars so you can inspect manually ---
    print("[parse] WARNING: could not find table or card elements.")
    print("[debug] page snippet (first 2000 chars):")
    print(soup.prettify()[:2000])
    return rows


# ---------------------------------------------------------------------------
# Selenium fallback (uncomment if the site requires JS rendering)
# ---------------------------------------------------------------------------
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
#
# def fetch_page_selenium(url: str) -> BeautifulSoup:
#     """Fetch a JS-rendered page using headless Chrome."""
#     opts = Options()
#     opts.add_argument("--headless=new")
#     opts.add_argument("--no-sandbox")
#     opts.add_argument("--disable-dev-shm-usage")
#     opts.add_argument(f"user-agent={HEADERS['User-Agent']}")
#     driver = webdriver.Chrome(options=opts)
#     try:
#         driver.get(url)
#         # Wait for the table or a known element to appear
#         WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "table, .gac-counter-row"))
#         )
#         return BeautifulSoup(driver.page_source, "html.parser")
#     finally:
#         driver.quit()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def clean_pct(val: str) -> float:
    """Convert '73.5%' or '73.5' to float 73.5. Returns -1 on failure."""
    try:
        return float(str(val).replace("%", "").strip())
    except (ValueError, TypeError):
        return -1.0


def find_win_pct_column(columns: list[str]) -> str | None:
    """Return the column name that looks like a win-percentage field."""
    for col in columns:
        lower = col.lower()
        if "win" in lower and ("%" in lower or "pct" in lower or "percent" in lower):
            return col
    # Fallback: last column often holds the percentage
    if columns:
        return columns[-1]
    return None


def main():
    all_rows: list[dict] = []

    for url in PAGES:
        try:
            soup = fetch_page(url)
            rows = parse_defenses(soup)
            print(f"[main] parsed {len(rows)} rows from {url}")
            all_rows.extend(rows)
        except requests.HTTPError as exc:
            print(f"[error] HTTP error for {url}: {exc}")
        except Exception as exc:
            print(f"[error] Unexpected error for {url}: {exc}")

    if not all_rows:
        print("[main] No data collected. Check debug output above.")
        return

    df = pd.DataFrame(all_rows)
    print(f"\n[main] Total rows across all pages: {len(df)}")
    print(f"[main] Columns detected: {list(df.columns)}")

    win_pct_col = find_win_pct_column(list(df.columns))
    if win_pct_col is None:
        print("[main] Could not identify a win-% column. Printing raw data sample:")
        print(df.head(10).to_string())
        return

    print(f"[main] Using '{win_pct_col}' as the win-% column.")
    df["_win_pct_num"] = df[win_pct_col].apply(clean_pct)
    df_sorted = df.sort_values("_win_pct_num", ascending=False).drop(
        columns=["_win_pct_num"]
    )

    print(f"\n{'='*70}")
    print(f"TOP {TOP_N} GAC DEFENSES BY WIN % — Season 75")
    print(f"{'='*70}\n")
    print(df_sorted.head(TOP_N).to_string(index=False))


if __name__ == "__main__":
    main()
