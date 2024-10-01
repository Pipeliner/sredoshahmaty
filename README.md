# SredoShahmaty (WednesdayChess)

SredoShahmaty is a Python-based application for managing and announcing chess tournaments on Lichess, specifically for the "WednesdayChess" series.

## Features

- Automatically creates Swiss tournaments on Lichess
- Sends announcements via Lichess group PMs and Telegram
- Generates ICS (iCalendar) files for calendar integration
- Supports custom tournament titles and sequence numbering

## Requirements

- Python 3.12+
- Poetry for dependency management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/sredoshahmaty.git
   cd sredoshahmaty
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add the following variables:
   ```
   LICHESS_TOKEN=your_lichess_oauth_token
   LICHESS_TEAM=your_lichess_team_id
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_GROUP_ID=your_telegram_group_id
   TELEGRAM_GROUP_ID_DEBUG=your_telegram_debug_group_id
   SURVEY_LINK=your_survey_link
   ```

## Usage

Run the main script with various command-line arguments:

```
poetry run python doit.py [custom_title] [options]
```

Options:
- `--show-next`: Display information about the next scheduled tournament, if any. This option does not create a new tournament.
- `--lichess-pm`: Send announcement via Lichess PM
- `--telegram-pm`: Send announcement via Telegram
  - `--tg-debug-channel`: Send announcement to debug Telegram channel (requires `--telegram-pm`)
  - `--tg-pin`: Pin the Telegram message (requires `--telegram-pm`)
  - `--tg-notify`: Enable notifications for pinned Telegram message (requires `--telegram-pm`)
  - `--tg-ics`: Attach ICS file to Telegram message (requires `--telegram-pm`)

When run without `--show-next`, the script checks if a tournament for the next Thursday exists. If not, it creates a new tournament. Additionally, notifications may be sent via either Lichess or Telegram or both, depending on the flags used.

Examples:

1. Show next scheduled tournament:
   ```
   poetry run python doit.py --show-next
   ```

2. Create a tournament with default title and send announcements:
   ```
   poetry run python doit.py --lichess-pm --telegram-pm
   ```

3. Create a tournament with a custom title and send announcements:
   ```
   poetry run python doit.py "Special Chess Event" --lichess-pm --telegram-pm
   ```

4. Create a tournament and send a debug Telegram message with ICS attachment:
   ```
   poetry run python doit.py --telegram-pm --tg-debug-channel --tg-ics
   ```

## Development

This project uses pre-commit hooks for code quality. To set up:

1. Install pre-commit: `pip install pre-commit`
2. Install the pre-commit hooks: `pre-commit install`

Run the hooks manually with: `pre-commit run --all-files`

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information or contact details here]
