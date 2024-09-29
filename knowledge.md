# SredoShahmaty Project Knowledge

## Project Overview
- This project is a Python-based application for managing chess tournaments, specifically "SredoShahmaty" (Wednesday Chess).
- The main functionality is implemented in `doit.py`.
- It uses the Lichess API for tournament management and Telegram for announcements.

## Key Components
1. Tournament Creation and Management
   - Creates Swiss tournaments on Lichess
   - Checks for existing tournaments before creating new ones
   - Implements intelligent title inference for new tournaments

2. Announcement System
   - Sends announcements via Lichess PMs and Telegram
   - Uses Jinja2 templates for formatting announcements

3. Environment and Configuration
   - Uses `python-dotenv` for managing environment variables
   - Key configuration items include Lichess OAuth token, Telegram bot token, team IDs, and survey link

4. Dependencies
   - Main dependencies: httpx, pendulum, aiogram, jinja2
   - Uses Poetry for dependency management

## File Structure
- `doit.py`: Main script containing core functionality
- `templates/`: Directory for Jinja2 templates
  - `announcement.md.j2`: Template for tournament announcements
- `pyproject.toml` & `poetry.lock`: Poetry configuration and lock files
- `.gitignore`: Git ignore file
- `.env`: Environment variables file (not tracked in git)

## Usage
- The script is run periodically to create tournaments and send announcements
- Command-line arguments control behavior (e.g., `--lichess-pm`, `--telegram-pm`)
- Custom tournament titles can be set via command-line arguments

## Command-line Arguments and Tournament Naming
- Use sys.argv[1] for custom title if it does not start with "--"
- When checking for custom titles, ensure that flags like "--lichess-pm" and "--telegram-pm" are not mistaken for custom titles
- When inferring tournament sequence numbers, only check for the number at the end of the title, not an exact match of the entire title
- The default tournament naming convention is "Средошахматы X", where X is the sequence number

## Project Overview
- This project is a Python-based application for managing chess tournaments, specifically "SredoShahmaty" (Wednesday Chess).
- The main functionality is implemented in `doit.py`.
- It uses the Lichess API for tournament management and Telegram for announcements.
## Key Components
1. Tournament Creation and Management
   - Creates Swiss tournaments on Lichess
   - Checks for existing tournaments before creating new ones
   - Implements intelligent title inference for new tournaments

2. Announcement System
   - Sends announcements via Lichess PMs and Telegram
   - Uses Jinja2 templates for formatting announcements

3. Environment and Configuration
   - Uses `python-dotenv` for managing environment variables
   - Key configuration items include Lichess OAuth token, Telegram bot token, team IDs, and survey link

4. Dependencies
   - Main dependencies: httpx, pendulum, aiogram, jinja2
   - Uses Poetry for dependency management

## File Structure
- `doit.py`: Main script containing core functionality
- `templates/`: Directory for Jinja2 templates
  - `announcement.md.j2`: Template for tournament announcements
- `pyproject.toml` & `poetry.lock`: Poetry configuration and lock files
- `.gitignore`: Git ignore file
- `.env`: Environment variables file (not tracked in git)

## Usage
- The script is run periodically to create tournaments and send announcements
- Command-line arguments control behavior (e.g., `--lichess-pm`, `--telegram-pm`)
- Custom tournament titles can be set via command-line arguments

## CLI Usage and Behavior
- The script uses command-line arguments to control its behavior
- argv[1] (the first argument after the script name) is used for custom title if it doesn't start with "--"
- If argv[1] is just a number, it keeps the previous behavior of default titles (e.g., "Средошахматы X")
- Use `--lichess-pm` and `--telegram-pm` flags to send announcements
- Other flags like `--tg-pin`, `--tg-notify`, and `--tg-ics` control Telegram announcement behavior

## Notes
- The project uses asynchronous programming (asyncio)
- Timezone handling is an important aspect (uses 'Europe/Moscow' timezone)
- ICS (iCalendar) file generation is implemented for calendar integration
- After making changes, thoroughly review the entire script for potential errors or inconsistencies
- Test the script with various inputs and scenarios to ensure it works as expected
- Pay special attention to areas of the code that were modified, checking for any unintended side effects

## Knowledge File Maintenance
- Keep knowledge files concise and focused on important project information
- Avoid using placeholders or comments that indicate partial content (e.g., "<!-- ... existing knowledge file ... -->")
- When updating knowledge files, ensure the entire file content is preserved and new information is integrated seamlessly
- Regularly review and update knowledge files to reflect the current state of the project

## Code Style and Best Practices
- When providing code snippets or examples, always include the full code without using placeholders
- Avoid using comments like "# ... (existing imports and configurations)" as they can lead to broken or incomplete scripts
- Ensure all code provided is functional and can be run as-is
- Use environment variables for configuration that may change or contain sensitive information
## TODO
- Implement error handling and logging for better debugging
- Add unit tests to ensure reliability of core functions
- Develop a comprehensive testing strategy to catch errors before deployment
