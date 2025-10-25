# WaniKani Next Review Checker

Tools for checking the WaniKani API to determine when your next review will be available for unlocked items at your current level.

This project includes:
- **Command-line tool** - Check reviews from the terminal
- **macOS Menu Bar Widget** - Display next review time in your menu bar

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

## Usage

### Command-Line Tool

Set your WaniKani API token as an environment variable:

```bash
export WANIKANI_API_TOKEN='your_token_here'
```

To make this permanent, add the export line to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.).

Run the script:

```bash
uv run cli.py
```

Or if using a traditional Python environment:

```bash
python cli.py
```

#### Example Output

```
鰐蟹 user_name level 10 next review 1 of 17 unlocked items:
  今日 4:00 PM (2h 14m 39s)
```

### macOS Menu Bar Widget

The macos Keyring is used to store the API Token.

Run the menu bar widget:

```bash
uv run macos_widget.py
```

Or if using a traditional Python environment:

```bash
python macos_widget.py
```

Or create a macos application:

```bash
uv run pyinstaller WaniKaniNext.spec
```

The widget will:
- Display the next review time (in local time) and item count in your menu bar
- Show as: `鰐蟹 今日 7:30 PM (12)` format
- Automatically refresh every hour
- Allow manual refresh via the dropdown menu
- Click the menu bar icon to see:
  - Full date and time of next review
  - Time remaining until next review
  - Manual refresh option
  - Last update time
  - Update API Token

**Note:** To run the widget at login, you can add it to your Login Items in System Preferences.

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
