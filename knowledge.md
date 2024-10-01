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
   - Main dependencies: httpx, pendulum, aiogram, jinja2, pydantic
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
- New --show-next argument to display information about the next scheduled tournament without creating one
- --telegram-pm-debug flag for sending announcements to a debug Telegram group

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
To maintain and improve code quality, the following tools are integrated into the project:

1. Flake8: A tool that combines PyFlakes, pycodestyle, and McCabe complexity checker.
   - Run manually: `poetry run flake8 .`
   - VSCode integration: Install the "Python" extension and enable Flake8 in settings.

2. Black: An opinionated code formatter that automatically formats your code.
   - Run manually: `poetry run black .`
   - VSCode integration: Install the "Python" extension and set Black as the formatter in settings.

3. Mypy: A static type checker for Python.
   - Run manually: `poetry run mypy .`
   - VSCode integration: Install the "Python" extension and enable Mypy in settings.

4. Pylint: A comprehensive linter that checks for errors and enforces a coding standard.
   - Run manually: `poetry run pylint **/*.py`
   - VSCode integration: Install the "Python" extension and enable Pylint in settings.

5. Bandit: A tool designed to find common security issues in Python code.
   - Run manually: `poetry run bandit -r .`
   - VSCode integration: Install the "Bandit" extension.

6. isort: A utility to sort imports alphabetically, and automatically separated into sections.
   - Run manually: `poetry run isort .`
   - VSCode integration: Install the "Python" extension and enable isort in settings.

7. Ruff: A fast Python linter and code formatter.
   - Configuration is in pyproject.toml
   - Run manually: `poetry run ruff check .`
   - VSCode integration: Install the "Ruff" extension.

To set up pre-commit hooks:

1. Install pre-commit: `pip install pre-commit`
2. Create a `.pre-commit-config.yaml` file in the project root with the following content:

```yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.2.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
-   repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
    -   id: black
-   repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
    -   id: mypy
-   repo: https://github.com/PyCQA/pylint
    rev: v2.15.5
    hooks:
    -   id: pylint
-   repo: https://github.com/PyCQA/bandit
    rev: 1.7.4
    hooks:
    -   id: bandit
-   repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
    -   id: isort
-   repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.260
    hooks:
    -   id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

3. Install the pre-commit hooks: `pre-commit install`

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

## Pydantic Models
- The project now uses pydantic models for Tournaments with `extra = allow`.
- The `Tournament` model is defined in `doit.py` and is used to handle tournament data.
- The `url` method of the `Tournament` model generates the URL for the tournament.
