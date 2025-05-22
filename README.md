# Patreon Tier Availability Monitor

A Python script that monitors a specific Patreon tier for availability and sends notifications when the tier becomes available.

## Features

- Continuously monitors a Patreon tier for availability
- Sends push notifications via Pushover when the tier becomes available
- Configurable check intervals
- Detailed logging to both console and file

## Requirements

- Python 3.6+
- Required packages (see `requirements.txt`)

## Quick Setup with uv

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. Here's how to set up this project with uv:

```bash
# Install uv if you don't have it yet
pip install uv

# Create and activate a virtual environment
uv venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

## Configuration

Edit `patreon_monitor.py` to configure the following settings:

```python
# Pushover notification settings (for phone notifications)
# Sign up at https://pushover.net/ to get these credentials
PUSHOVER_USER_KEY = "YOUR_USER_KEY_HERE"
PUSHOVER_API_TOKEN = "YOUR_API_TOKEN_HERE"

# Configuration
URL = "https://www.patreon.com/drumsanddrams/membership"  # URL to monitor
CHECK_INTERVAL = 15  # seconds between checks
TIER_NAME = "WHISKEY DRUMMERS"  # Name of the tier to monitor
```

## Usage

Run the script with:

```bash
python patreon_monitor.py
```

The script will:

1. Check the specified Patreon page for the tier availability
2. Log the status to both console and `patreon_monitor.log`
3. Send a notification if the tier becomes available
4. Continue monitoring at the specified interval

## Customization

You can modify the script to:

- Monitor different Patreon pages by changing the `URL`
- Look for different tier names by changing `TIER_NAME`
- Use a different notification service instead of Pushover
- Adjust the check frequency with `CHECK_INTERVAL`

## License

MIT

## Author

Created by Jerren Trifan - <https://github.com/Trifall>
