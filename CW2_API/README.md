# Coursework 2: Search Engine Tool (prototype)

Python command-line search tool for **https://quotes.toscrape.com/**: crawl with a politeness delay, build a case-insensitive inverted index (word frequency and positions), persist it to disk, and query it interactively.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run the interactive shell from the repository root:

```bash
python -m src.main
```

Optional: custom index path:

```bash
python -m src.main --index data\index.json
```

### Commands

| Command | Description |
|--------|-------------|
| `build` | Crawl the site, build the inverted index, save to `data/index.json` (takes time: **≥6 seconds between requests**). |
| `load` | Load a previously built index from disk. |
| `print <word>` | Show postings for one word (URLs, frequency, token positions). |
| `find <word> [<word> ...]` | List pages that contain **all** given words (boolean AND). Example: `find good friends`. |
| `quit` | Exit the shell. |

## Testing

```bash
pytest
```

## Dependencies

- `requests` — HTTP
- `beautifulsoup4` — HTML parsing
- `pytest` — tests (dev)

## Project layout

- `src/crawler.py` — site crawl and text extraction
- `src/indexer.py` — tokenisation, inverted index, load/save JSON
- `src/search.py` — `print` / `find` logic
- `src/main.py` — interactive CLI
- `tests/` — unit tests
- `data/` — generated `index.json` after `build`
