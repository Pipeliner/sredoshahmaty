import argparse
import asyncio
import json
import logging
import os
import re

import dotenv
import httpx
import pendulum
from aiogram import Bot
from aiogram.types import BufferedInputFile
from jinja2 import Environment, FileSystemLoader

# Load environment variables from .env file
dotenv.load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration
LICHESS_OAUTH_TOKEN = os.environ["LICHESS_TOKEN"]
LICHESS_TEAM = os.environ["LICHESS_TEAM"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_GROUP_ID = os.environ["TELEGRAM_GROUP_ID"]
TELEGRAM_GROUP_ID_DEBUG = os.environ["TELEGRAM_GROUP_ID_DEBUG"]
SURVEY_LINK = os.environ.get("SURVEY_LINK", "")

OAUTH_HEADERS = {
    "Authorization": f"Bearer {LICHESS_OAUTH_TOKEN}",
    "Content-Type": "application/json",
}

# Jinja2 setup
env = Environment(loader=FileSystemLoader("templates"), autoescape=True)


# Function to get the next Thursday
def get_next_thursday(
    start_hour: int = 21, start_minute: int = 30, extra_minutes_before_start: int = 3
) -> pendulum.DateTime:
    today = pendulum.now("Europe/Moscow")
    if today.day_of_week == pendulum.THURSDAY:
        if (today.hour, today.minute) < (start_hour, start_minute):
            logging.warning("Today is Thursday, making tournament for today")
            return today.replace(
                hour=start_hour,
                minute=start_minute + extra_minutes_before_start,
                second=0,
                microsecond=0,
            )

    thursday = today.next(pendulum.THURSDAY)
    return thursday.replace(
        hour=start_hour,
        minute=start_minute + extra_minutes_before_start,
        second=0,
        microsecond=0,
    )


# Function to get the last Swiss tournaments for a team
async def get_last_swiss_tournaments(
    client: httpx.AsyncClient, team_id: str, limit: int = 5
) -> list[dict]:
    try:
        response = await client.get(f"https://lichess.org/api/team/{team_id}/swiss")
        response.raise_for_status()
        data = response.text.split("\n")[:limit]
        return [json.loads(tournament) for tournament in data]
    except httpx.HTTPError as e:
        logging.error(f"Error fetching swiss tournaments: {e}")
        return []


# Function to infer the sequence number for the next tournament
def infer_sequence_number(tournaments: list[dict]) -> int:
    for tournament in tournaments:
        match = re.search(r"(\d+)$", tournament["name"])
        if match:
            return int(match.group(1)) + 1
    return 1


# Function to create a new Swiss tournament if needed
async def create_new_swiss_tournament_if_needed(
    client: httpx.AsyncClient,
    custom_title: str | None = None,
) -> dict:
    # Check if a tournament for next Thursday already exists
    if tournament := await thursday_tournament_exists(client, LICHESS_TEAM):
        logging.info("Tournament for next Thursday already exists")
        return tournament

    logging.info("Creating new tournament for next Thursday")
    last_tournaments = await get_last_swiss_tournaments(client, LICHESS_TEAM)

    # Determine the title for the new tournament
    if custom_title:
        if custom_title.isdigit():
            title = f"Средошахматы {custom_title}"
        else:
            title = custom_title
    elif last_tournaments:
        sequence_number = infer_sequence_number(last_tournaments)
        title = f"Средошахматы {sequence_number}"
    else:
        title = "Средошахматы 1"
        logging.warning("No previous tournaments found. Starting with Средошахматы 1.")

    return await create_new_swiss_tournament(client, title)


# Function to create a new Swiss tournament
async def create_new_swiss_tournament(
    client: httpx.AsyncClient,
    title: str,
) -> dict:
    tournament_params = {
        "name": title,
        "clock": {
            "limit": 180,
            "increment": 2,
        },
        "nbRounds": 5,
        "variant": "standard",
        "rated": True,
        "startsAt": get_next_thursday().isoformat(),
    }

    try:
        response = await client.post(
            f"https://lichess.org/api/swiss/new/{LICHESS_TEAM}",
            headers=OAUTH_HEADERS,
            json=tournament_params,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logging.error(f"Error creating new Swiss tournament: {e}")
        raise


# Function to check if a tournament for next Thursday already exists
async def thursday_tournament_exists(client: httpx.AsyncClient, team_id: str) -> dict | None:
    last_tournaments = await get_last_swiss_tournaments(client, team_id, limit=1)
    if last_tournaments:
        last_tournament = last_tournaments[0]
        next_thursday = get_next_thursday()
        starts_at = pendulum.parse(last_tournament["startsAt"])
        if starts_at.date() == next_thursday.date():
            return last_tournament
    return None


# Function to get the URL of a Swiss tournament
def swiss_tournament_url(tournament_id: str) -> str:
    return f"https://lichess.org/swiss/{tournament_id}"


# Function to announce the tournament via Lichess PMs
async def announce_via_lichess_pms(client: httpx.AsyncClient, team_id: str, message: str):
    try:
        response = await client.post(
            f"https://lichess.org/team/{team_id}/pm-all",
            headers={**OAUTH_HEADERS, "Origin": "https://lichess.org"},
            json={"message": message},
        )
        response.raise_for_status()
        logging.info("Announcement sent via PM to the team")
    except httpx.HTTPError as e:
        logging.error(f"Error sending announcement via PM to the team: {e}")


# Function to generate a calendar timestamp
def calendar_timestamp(date: pendulum.DateTime) -> str:
    return date.in_timezone("UTC").format("YYYYMMDDTHHmmss") + "Z"


# Function to generate ICS content for the tournament
def generate_ics_content(
    tournament_id: str, tournament_date: pendulum.DateTime, tournament_title: str
) -> str:
    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Assistant//EN
BEGIN:VEVENT
UID:{calendar_timestamp(tournament_date)}@lichess.org
DTSTAMP:{calendar_timestamp(tournament_date.subtract(days=1))}
DTSTART:{calendar_timestamp(tournament_date)}
DTEND:{calendar_timestamp(tournament_date.add(hours=1))}
SUMMARY:{tournament_title}
DESCRIPTION:Chess tournament on Lichess: {swiss_tournament_url(tournament_id)}
URL:{swiss_tournament_url(tournament_id)}
X-ALT-DESC;FMTTYPE=text/html:Chess tournament on Lichess: <a href="{swiss_tournament_url(tournament_id)}">{swiss_tournament_url(tournament_id)}</a>
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder: 1 hour before event
TRIGGER:-PT1H
END:VALARM
BEGIN:VALARM
ACTION:DISPLAY
DESCRIPTION:Reminder: 10 minutes before event
TRIGGER:-PT10M
END:VALARM
X-GOOGLE-CALENDAR-CONTENT-TITLE:{tournament_title}
X-GOOGLE-CALENDAR-CONTENT-ICON:https://ssl.gstatic.com/calendar/images/notification_icon_event_4x.png
X-GOOGLE-CALENDAR-CONTENT-TYPE:text/html
X-GOOGLE-CALENDAR-CONTENT-VALUE:<font color="#4285F4">{tournament_title}</font><br><a href="{swiss_tournament_url(tournament_id)}">{swiss_tournament_url(tournament_id)}</a>
END:VEVENT
END:VCALENDAR
"""


# Function to announce the tournament via Telegram channel
async def announce_via_telegram_channel(
    bot: Bot,
    channel_id: str,
    message: str,
    pin: bool = True,
    notify: bool = True,
    attach_ics: bool = True,
    tournament_id: str | None = None,
    tournament_date: pendulum.DateTime | None = None,
    tournament_title: str | None = None,
):
    try:
        if attach_ics:
            if not tournament_id or not tournament_date or not tournament_title:
                logging.error("Missing tournament details for ICS attachment")
                return False

            ics_content = generate_ics_content(
                tournament_id, tournament_date, tournament_title
            ).encode()

            file = BufferedInputFile(ics_content, filename="lc.ics")

            response = await bot.send_document(
                chat_id=channel_id,
                document=file,
                caption=message,
                parse_mode="Markdown",
            )
            logging.info("Announcement sent via Telegram channel with ICS attachment")
        else:
            response = await bot.send_message(
                chat_id=channel_id,
                text=message,
                parse_mode="Markdown",
            )
            logging.info("Announcement sent via Telegram channel")

        if pin:
            await bot.pin_chat_message(
                chat_id=channel_id,
                message_id=response.message_id,
                disable_notification=not notify,
            )
            logging.info("Message pinned in the channel")

        return True
    except Exception as e:
        logging.error(f"Failed to send announcement: {str(e)}")
        return False
    finally:
        await bot.session.close()


async def main():
    parser = argparse.ArgumentParser(description="SredoShahmaty Tournament Manager")
    parser.add_argument("custom_title", nargs="?", help="Custom title for the tournament")
    parser.add_argument(
        "--lichess-pm", action="store_true", help="Send announcement via Lichess PM"
    )
    parser.add_argument("--telegram-pm", action="store_true", help="Send announcement via Telegram")
    parser.add_argument(
        "--telegram-pm-debug",
        action="store_true",
        help="Send announcement via Telegram to debug group",
    )
    parser.add_argument("--tg-pin", action="store_true", help="Pin the Telegram message")
    parser.add_argument(
        "--tg-notify",
        action="store_true",
        help="Enable notifications for pinned Telegram message",
    )
    parser.add_argument("--tg-ics", action="store_true", help="Attach ICS file to Telegram message")
    parser.add_argument(
        "--show-next",
        action="store_true",
        help="Display information about the next scheduled tournament",
    )
    args = parser.parse_args()

    timeout = httpx.Timeout(10.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        if args.show_next:
            tournament = await thursday_tournament_exists(client, LICHESS_TEAM)
            if tournament:
                print(f"Next tournament: {tournament['name']} at {tournament['startsAt']}")
                print(f"URL: {swiss_tournament_url(tournament['id'])}")
            else:
                next_thursday = get_next_thursday()
                print(f"No tournament scheduled yet. Next Thursday: {next_thursday}")
            return

        tournament = await create_new_swiss_tournament_if_needed(client, args.custom_title)

        template = env.get_template("announcement.md.j2")

        tasks = []

        if args.lichess_pm:
            announcement = template.render(
                tournament_url=swiss_tournament_url(tournament["id"]),
                tournament_date=pendulum.parse(tournament["startsAt"]),
                survey_link=SURVEY_LINK,
                is_lichess=True,
                is_telegram=False,
            )
            tasks.append(announce_via_lichess_pms(client, LICHESS_TEAM, announcement))

        if args.telegram_pm or args.telegram_pm_debug:
            announcement = template.render(
                tournament_url=swiss_tournament_url(tournament["id"]),
                tournament_date=pendulum.parse(tournament["startsAt"]),
                survey_link=SURVEY_LINK,
                is_lichess=False,
                is_telegram=True,
            )
            group_id = TELEGRAM_GROUP_ID_DEBUG if args.telegram_pm_debug else TELEGRAM_GROUP_ID
            async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
                tasks.append(
                    announce_via_telegram_channel(
                        bot,
                        group_id,
                        announcement,
                        args.tg_pin,
                        args.tg_notify,
                        args.tg_ics,
                        tournament["id"],
                        pendulum.parse(tournament["startsAt"]),
                        tournament["name"],
                    )
                )

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
