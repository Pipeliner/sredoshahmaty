# Templates Directory Knowledge

## Overview
This directory contains Jinja2 templates used for formatting announcements in the SredoShahmaty project.

## Files
1. `announcement.md.j2`
   - Purpose: Template for tournament announcements
   - Used by: The main script (`doit.py`) to generate announcements for Lichess PMs and Telegram messages
   - Features:
     - Supports both English and Russian languages
     - Includes conditional formatting for different announcement types (Lichess vs Telegram)
     - Provides tournament details such as date, time, and URL

## Usage
- Templates are loaded and rendered in `doit.py` using the Jinja2 library
- The rendered templates are used to create messages for Lichess PMs and Telegram announcements

## Notes
- The template supports different announcement timings (e.g., "Starting in 5 minutes", "Starting in hour and a half")
- It includes placeholders for tournament URL, date, and time
- The template is designed to be flexible for both Lichess and Telegram platforms

## Potential Improvements
- Consider separating English and Russian translations for easier maintenance
- Add more comments within the template to explain conditional logic
- Implement a system for managing multiple announcement templates if needed in the future

