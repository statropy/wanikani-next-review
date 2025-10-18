# WaniKani Next Review Checker

A command-line tool that checks the WaniKani API to determine when your next review will be available for unlocked items at your current level.

## Features

- Fetches your current WaniKani level
- Finds unlocked kanji and radical assignments at your current level
- Shows when the next review is available in both UTC and local time
- Displays a countdown showing how long until the review is available
- Shows the number of items that will be available for review

## Prerequisites

- Python 3.x
- [uv](https://docs.astral.sh/uv/) package manager (recommended) or pip
- A WaniKani API token ([get yours here](https://www.wanikani.com/settings/personal_access_tokens))

## Installation

1. Clone or download this repository

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Set your WaniKani API token as an environment variable:

```bash
export WANIKANI_API_TOKEN='your_token_here'
```

To make this permanent, add the export line to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.).

## Usage

Run the script:

```bash
uv run main.py
```

Or if using a traditional Python environment:

```bash
python main.py
```

### Example Output

```
Fetching user level...
Current level: 15

Fetching unlocked assignments for level 15...
Found 23 unlocked assignments

Next review available:
  UTC:   2025-10-17 14:30:00 UTC
  Local: 2025-10-17 07:30:00 PDT
  In:    5h 23m 14s
  Items: 12
```

## How It Works

The script:
1. Authenticates with the WaniKani API using your personal access token
2. Retrieves your current level
3. Fetches all unlocked kanji and radical assignments at your current level (SRS stages 0-4)
4. Finds the earliest review time from those assignments
5. Displays the review time in both UTC and your local timezone, along with a countdown

## API Documentation

This tool uses the [WaniKani API v2](https://docs.api.wanikani.com/20170710/).

## License

MIT License - see [LICENSE](LICENSE) for details.

This is an independent project and is not affiliated with WaniKani or Tofugu LLC.

## Claude Code

This project created with assistance from Claude Code and Sonnet 4.5
