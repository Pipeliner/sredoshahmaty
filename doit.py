from io import BytesIO
import json
import sys
from typing import Dict, Optional
import httpx
import dotenv
import pendulum
import os
import logging

import asyncio
from aiogram import Bot

from aiogram.types import BufferedInputFile

import logging


# Load environment variables from .env file
dotenv.load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Replace with your actual OAuth token
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


# Function to calculate the next Thursday (possibly today) at 21:30 MSK
def get_next_thursday(
    start_hour=21, start_minute=30, extra_minutes_before_start=3
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


def create_new_swiss_tournament_if_needed(sequence_number=0, custom_title=None):
    if tournament := thursday_tournament_exists(LICHESS_TEAM):
        logging.info("Tournament for next Thursday already exists")
        print(tournament)
        return tournament

    logging.info("Creating new tournament for next Thursday")
    return create_new_swiss_tournament(sequence_number, custom_title)


def create_new_swiss_tournament(sequence_number=0, custom_title=None) -> Dict:
    title = custom_title or f"Средошахматы {sequence_number}"
    tournament_params = {
        "name": title,
        "clock": {
            "limit": 180,  # 3 minutes in seconds
            "increment": 2,  # 2 seconds increment
        },
        "nbRounds": 5,
        "variant": "standard",  # or any other variant you prefer
        "rated": True,  # or False if you don't want it rated
        "startsAt": get_next_thursday().isoformat(),  # Convert to ISO format
    }

    response = httpx.post(
        f"https://lichess.org/api/swiss/new/{LICHESS_TEAM}",
        headers=OAUTH_HEADERS,
        json=tournament_params,
    )

    return response.json()


def get_last_swiss_tournament(team_id: str) -> Optional[Dict]:
    """Get the last Swiss tournament for a given team.

    Example:
    {'id': '4yJeN06c', 'createdBy': 'avimd', 'startsAt': '2024-09-13T18:35:00Z', 'name': 'Средошахматы 2 сезон, призы', 'clock': {'limit': 180, 'increment': 2}, 'variant': 'standard', 'round': 4, 'nbRounds': 4, 'nbPlayers': 10, 'nbOngoing': 0, 'status': 'finished', 'verdicts': {'list': [{'condition': 'Play your games', 'verdict': 'ok'}], 'accepted': True}, 'rated': True, 'stats': {'absences': 9, 'averageRating': 1661, 'byes': 2, 'blackWins': 14, 'games': 14, 'draws': 0, 'whiteWins': 14}}
    """
    response = httpx.get(f"https://lichess.org/api/team/{team_id}/swiss")
    if response.status_code == 200:
        data = response.text.split("\n")[0]
        return json.loads(data)
    else:
        logging.error(
            "Error fetching swiss tournaments:", response.status_code, response.text
        )
        return None


def thursday_tournament_exists(team_id: str) -> Dict:
    last_tournament = get_last_swiss_tournament(team_id)
    if last_tournament:
        starts_at = pendulum.parse(last_tournament["startsAt"])
        if starts_at.day_of_week == pendulum.THURSDAY:
            return last_tournament
    return None


def swiss_tournament_url(tournament_id: str) -> str:
    return f"https://lichess.org/swiss/{tournament_id}"


def announce_via_lichess_pms(team_id: str, message: str):
    with httpx.Client() as client:
        response = client.post(
            f"https://lichess.org/team/{team_id}/pm-all",
            headers={**OAUTH_HEADERS, "Origin": "https://lichess.org"},
            json={"message": message},
        )

    if response.status_code == 200:
        logging.info("Announcement sent via PM to the team")
    else:
        logging.error(
            "Error sending announcement via PM to the team:",
            response.status_code,
            response.text,
        )


def calendar_timestamp(date: pendulum.DateTime) -> str:
    return date.in_timezone("UTC").format("YYYYMMDDTHHmmss") + "Z"


def generate_ics_file(
    tournament_id: str, tournament_date: pendulum.DateTime, tournament_title: str
):
    """BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//Assistant//EN
    BEGIN:VEVENT
    UID:20240912T213000@lichess.org
    DTSTAMP:20240911T000000Z
    DTSTART:20240912T183000Z
    DTEND:20240912T193000Z
    SUMMARY:Средошахматы: 2 сезон // призы!
    DESCRIPTION:Chess tournament on Lichess: https://lichess.org/swiss/Lq2u55Cv
    URL:https://lichess.org/swiss/Lq2u55Cv
    X-ALT-DESC;FMTTYPE=text/html:Chess tournament on Lichess: <a href="https://lichess.org/swiss/Lq2u55Cv">https://lichess.org/swiss/Lq2u55Cv</a>
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
    X-GOOGLE-CALENDAR-CONTENT-TITLE:Средошахматы: 2 сезон // призы!
    X-GOOGLE-CALENDAR-CONTENT-ICON:https://ssl.gstatic.com/calendar/images/notification_icon_event_4x.png
    X-GOOGLE-CALENDAR-CONTENT-TYPE:text/html
    X-GOOGLE-CALENDAR-CONTENT-VALUE:<font color="#4285F4">Средошахматы: 2 сезон // призы!</font><br><a href="https://lichess.org/swiss/Lq2u55Cv">https://lichess.org/swiss/Lq2u55Cv</a>
    END:VEVENT
    END:VCALENDAR
    """

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


def announce_via_telegram_channel(
    channel_id: str,
    message: str,
    pin=True,
    notify=True,
    attach_ics=True,
    tournament_id: str = None,
    tournament_date: Optional[pendulum.DateTime] = None,
    tournament_title: str = None,
):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    if attach_ics:
        if not tournament_id or not tournament_date or not tournament_title:
            logging.error("Missing tournament details for ICS attachment")
            return False

        ics_content = generate_ics_file(
            tournament_id, tournament_date, tournament_title
        ).encode()

        file = BufferedInputFile(ics_content, filename="lc.ics")

    async def send_announcement():
        try:
            if attach_ics:
                response = await bot.send_document(
                    chat_id=channel_id,
                    document=file,
                    caption=message,
                    parse_mode="Markdown",
                    # disable_notification=not notify,
                )
                logging.info(
                    "Announcement sent via Telegram channel with ICS attachment"
                )
            else:
                response = await bot.send_message(
                    chat_id=channel_id,
                    text=message,
                    parse_mode="Markdown",
                    # disable_notification=not notify,
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

    return asyncio.get_event_loop().run_until_complete(send_announcement())


def main():
    sequence_number = sys.argv[1] if len(sys.argv) > 1 else 0

    # TODO: a good UI for this, or maybe generation via LLM, or...
    announcement_text = """Good day to everyone! Today, Thursday, September 19, we're meeting for the traditional WednesdayChess event 🤯 at 9:30 PM MSK / 6:30 PM UTC.
As always, colleagues, friends, and pets are welcome.
To play with us, you need to register on Lichess and click "Join" via the link.
Any questions or uncertainties can be asked in the chat.
Enjoy the game and good luck! 🍀
The tournament consists of 5 rounds. It's not mandatory to play all of them — you can start with just one or two games.
If you're not very good at playing or don't play at all, give it a try! You might enjoy it.
We highly encourage suggestions for improving the format and organization of the tournament.
Join our Telegram group: https://t.me/+N8kwmHoSiVQ2YTZi
{tournament_url}
    
Доброго всем дня! Сегодня, в четверг 19 сентября, встречаемся на традиционных Средошахматах по четвергам 🤯 в 21:30 МСК.
Как и всегда, будем рады вашим коллегам, друзьям и домашним питомцам.
Чтобы играть с нами, нужно зарегистрироваться на Lichess и по ссылке нажать кнопку "Присоединиться".
Любые вопросы и непонятности можно задавать в чате.
Приятной игры и удачи! 🍀
Турнир играется в 5 туров. Не обязательно отыгрывать их все, можно начать с одной-двух партий.
Если вы не очень хорошо играете или вообще не играете, попробуйте! Может быть, вам понравится.
Очень приветствуются предложения по улучшению формата и организации турнира.
Добавляйтесь в нашу группу в Телеграм: https://t.me/+N8kwmHoSiVQ2YTZi
{tournament_url}

---
🤖💖 С сердечным приветом, Средошахматы Бот
"""

    tournament = create_new_swiss_tournament_if_needed(sequence_number)

    announcement_text = announcement_text.replace(
        "{tournament_url}", swiss_tournament_url(tournament["id"])
    ).replace(
        # TODO: better formatting, Russian locale
        "{tournament_date}",
        pendulum.parse(tournament["startsAt"]).to_date_string(),
    )
    print(announcement_text)

    if "--lichess-pm" in sys.argv:
        announce_via_lichess_pms(LICHESS_TEAM, announcement_text)

    if "--telegram-pm" in sys.argv:
        pin = "--tg-pin" in sys.argv
        notify = "--tg-notify" in sys.argv
        ics = "--tg-ics" in sys.argv
        announce_via_telegram_channel(
            TELEGRAM_GROUP_ID,
            announcement_text,
            pin,
            notify,
            ics,
            tournament["id"],
            pendulum.parse(tournament["startsAt"]),
            tournament["name"],
        )


if __name__ == "__main__":
    main()
