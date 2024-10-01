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

- Use sys.argv[1] for custom title if it does not start with "--" to ensure that flags like "--lichess-pm" and "--telegram-pm" are not mistaken for custom titles
- When inferring tournament sequence numbers, only check for the number at the end of the title, not an exact match of the entire title
- The default tournament naming convention is "Средошахматы X", where X is the sequence number
- New --show-next argument to display information about the next scheduled tournament without creating one
- --telegram-pm flag for sending announcements via Telegram
- --tg-debug-channel flag (formerly --telegram-pm-debug) for sending announcements to a debug Telegram group
- All --tg-\* flags (including --tg-debug-channel, --tg-pin, --tg-notify, --tg-ics) are subflags of --telegram-pm and should only be used in conjunction with it

## Code Style and Best Practices

- When providing code snippets or examples, always include the full code without using placeholders
- Avoid using comments like "# ... (existing imports and configurations)" as they can lead to broken or incomplete scripts
- Ensure all code provided is functional and can be run as-is
- Use environment variables for configuration that may change or contain sensitive information
- After making changes, thoroughly review the entire script for potential errors or inconsistencies
- Test the script with various inputs and scenarios to ensure it works as expected
- Pay special attention to areas of the code that were modified, checking for any unintended side effects
- Never use placeholders or ellipsis (...) in functional code files, as this leads to truncated files and broken functionality
- When updating code files, always provide the complete, runnable code to maintain full functionality
- When editing a file, always include the entire file content, even parts that haven't changed
- After editing, verify that the file is complete and no parts have been omitted or represented with placeholders
- Avoid using diff-style notation (e.g., "@@ -1,16 +1,109 @@") in files
- Always use timeouts when making HTTP requests with httpx to prevent potential security vulnerabilities (CWE-400)

## Code Quality Tools and Usage

To set up pre-commit hooks:

1. Install pre-commit: `pip install pre-commit`
2. Install the pre-commit hooks: `pre-commit install`

Now, these checks will run automatically before each commit. You can also run them manually with `pre-commit run --all-files`.

## Notes

- The project uses asynchronous programming (asyncio)
- Timezone handling is an important aspect (uses 'Europe/Moscow' timezone)
- ICS (iCalendar) file generation is implemented for calendar integration

## Quality of Life (QoL) Improvements and Future Enhancements

### For Event Organizers

1. Tournament Template System: Implement a system to save and load tournament settings templates for quick setup of recurring events.
2. Automated Reporting: Generate post-tournament reports with statistics and insights to help improve future events.
3. Player Management: Create a simple database or integration with Lichess API to track regular participants, their preferences, and performance over time.
4. Customizable Announcement Templates: Allow organizers to easily modify announcement templates without changing the code.

### For Players

1. Tournament Reminders: Implement an opt-in system for players to receive reminders via Lichess message or email before the tournament starts.
2. Player Dashboard: Create a web interface where players can view their tournament history, statistics, and upcoming events.
3. Feedback System: Implement a simple way for players to provide feedback after each tournament, helping organizers improve the experience.
4. Achievements System: Introduce a system of achievements or badges for regular participation, good sportsmanship, or exceptional performance.

### General Improvements

1. Localization: Implement full localization support for multiple languages to cater to a diverse player base.
2. Integration with Other Platforms: Consider integrating with other chess platforms or social media to expand reach and engagement.
3. Tournament Variants: Implement support for different tournament formats or chess variants to add variety to the events.

## TODO

- Implement error handling and logging for better debugging
- Add unit tests to ensure reliability of core functions
- Develop a comprehensive testing strategy to catch errors before deployment
- Implement top priority QoL improvements from the list above
- Regularly review and update the list of potential improvements based on user feedback and changing needs
