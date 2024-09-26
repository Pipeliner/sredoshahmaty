import asyncio
import json
import logging
import os
import sys
from typing import Dict, Optional

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
TELEGRAM_GROUP_ID = (
    os.environ["TELEGRAM_GROUP_ID"]
    if "--telegram-pm-debug" not in sys.argv
    else os.environ["TELEGRAM_GROUP_ID_DEBUG"]
)

OAUTH_HEADERS = {
    "Authorization": f"Bearer {LICHESS_OAUTH_TOKEN}",
    "Content-Type": "application/json",
}

# Jinja2 setup
env = Environment(loader=FileSystemLoader("templates"))


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


async def create_new_swiss_tournament_if_needed(
    client: httpx.AsyncClient,
    sequence_number: int = 0,
    custom_title: Optional[str] = None,
) -> Dict:
    if tournament := await thursday_tournament_exists(client, LICHESS_TEAM):
        logging.info("Tournament for next Thursday already exists")
        return tournament

    logging.info("Creating new tournament for next Thursday")
    return await create_new_swiss_tournament(client, sequence_number, custom_title)


async def create_new_swiss_tournament(
    client: httpx.AsyncClient,
    sequence_number: int = 0,
    custom_title: Optional[str] = None,
) -> Dict:
    title = custom_title or f"Средошахматы {sequence_number}"
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


async def get_last_swiss_tournament(
    client: httpx.AsyncClient, team_id: str
) -> Optional[Dict]:
    try:
        response = await client.get(f"https://lichess.org/api/team/{team_id}/swiss")
        response.raise_for_status()
        data = response.text.split("\n")[0]
        return json.loads(data)
    except httpx.HTTPError as e:
        logging.error(f"Error fetching swiss tournaments: {e}")
        return None


async def thursday_tournament_exists(
    client: httpx.AsyncClient, team_id: str
) -> Optional[Dict]:
    last_tournament = await get_last_swiss_tournament(client, team_id)
    next_thursday = get_next_thursday()
    if last_tournament:
        starts_at = pendulum.parse(last_tournament["startsAt"])
        if starts_at.date() == next_thursday.date():
            return last_tournament
    return None


def swiss_tournament_url(tournament_id: str) -> str:
    return f"https://lichess.org/swiss/{tournament_id}"


async def announce_via_lichess_pms(
    client: httpx.AsyncClient, team_id: str, message: str
):
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


def calendar_timestamp(date: pendulum.DateTime) -> str:
    return date.in_timezone("UTC").format("YYYYMMDDTHHmmss") + "Z"


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


async def announce_via_telegram_channel(
    bot: Bot,
    channel_id: str,
    message: str,
    pin: bool = True,
    notify: bool = True,
    attach_ics: bool = True,
    tournament_id: Optional[str] = None,
    tournament_date: Optional[pendulum.DateTime] = None,
    tournament_title: Optional[str] = None,
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
    sequence_number = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    async with httpx.AsyncClient() as client:
        tournament = await create_new_swiss_tournament_if_needed(
            client, sequence_number
        )

        template = env.get_template("announcement.md.j2")

        tasks = []

        if "--lichess-pm" in sys.argv:
            announcement = template.render(
                tournament_url=swiss_tournament_url(tournament["id"]),
                tournament_date=pendulum.parse(tournament["startsAt"]),
                is_lichess=True,
                is_telegram=False,
            )
            tasks.append(announce_via_lichess_pms(client, LICHESS_TEAM, announcement))

        if "--telegram-pm" in sys.argv:
            announcement = template.render(
                tournament_url=swiss_tournament_url(tournament["id"]),
                tournament_date=pendulum.parse(tournament["startsAt"]),
                is_lichess=False,
                is_telegram=True,
            )
            pin = "--tg-pin" in sys.argv
            notify = "--tg-notify" in sys.argv
            ics = "--tg-ics" in sys.argv
            async with Bot(token=TELEGRAM_BOT_TOKEN) as bot:
                tasks.append(
                    announce_via_telegram_channel(
                        bot,
                        TELEGRAM_GROUP_ID,
                        announcement,
                        pin,
                        notify,
                        ics,
                        tournament["id"],
                        pendulum.parse(tournament["startsAt"]),
                        tournament["name"],
                    )
                )

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
