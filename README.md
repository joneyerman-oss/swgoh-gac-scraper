# swgoh-gac-scraper

Scrapes GAC (Grand Arena Championship) counter data from [swgoh.gg](https://swgoh.gg) for Season 75, merges both result pages, and prints the **top 30 defenses ranked by win percentage**.

## What it does

1. Fetches page 1 and page 2 of the Season 75 GAC counters leaderboard using `requests` + `BeautifulSoup`.
2. Uses a realistic browser `User-Agent` header to avoid 403 blocks.
3. Parses the HTML table (or card layout) to extract defense names, win counts, attempt counts, and win %.
4. Merges both pages into a single dataset and sorts by win % descending.
5. Prints the top 30 defenses to the terminal.
6. Includes a **Selenium fallback** (commented out) in case the site requires JavaScript rendering.
7. Prints raw debug rows for the first 3 results to help you verify column mapping.

## Setup

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python scrape_gac_defenses.py
```

### Selenium fallback

If the site requires JS rendering and the `requests` approach returns empty data:

1. Install ChromeDriver matching your Chrome version.
2. `pip install selenium`
3. In `scrape_gac_defenses.py`, uncomment the Selenium section at the top and replace calls to `fetch_page()` with `fetch_page_selenium()`.

## Output example

```
======================================================================
TOP 30 GAC DEFENSES BY WIN % — Season 75
======================================================================

Defense                         Counters  Wins  Attempts  Win %
SLKR + Hux + FOST + ...             ...   ...       ...  82.4%
...
```

## Dependencies

| Package        | Purpose                        |
|----------------|--------------------------------|
| requests       | HTTP fetching                  |
| beautifulsoup4 | HTML parsing                   |
| pandas         | Data manipulation & display    |
| lxml           | Fast HTML parser backend       |
| selenium       | JS-rendered page fallback      |

## Notes

- swgoh.gg may update its page structure between seasons. Check the `[debug]` output if column mapping breaks.
- The script targets Season 75 (`GA2_EVENT_SEASON_75`). To scrape a different season, update `BASE_URL` in the script.
