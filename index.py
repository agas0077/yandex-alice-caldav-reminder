import datetime
import os

import pytz

from CalDavCalendar import Calendar


def handler(event, context):

    response_base = {
        "version": event.get("version"),
        "session": event.get("session"),
    }

    url = os.getenv("CALDAV_URL")
    user_name = os.getenv("CALDAV_USER_NAME")
    password = os.getenv("CALDAV_PASSWORD")

    moscow_tz = pytz.timezone("Europe/Moscow")
    caldav_calendar = Calendar(url, user_name, password, moscow_tz)
    caldav_events = caldav_calendar.get_close_future_events("Мои события")

    # Если мероприятий нет, то ничего говорить не надо,
    # чтобы не было лишних уведомлений.
    if len(caldav_events) == 0:
        return {
            **response_base,
            "response": {"text": "", "end_session": "true"},
        }

    for caldav_event in caldav_events:
        text = "Напоминание о встречах в ближайшие 10 минут.\n"
        start_time = caldav_event["start_datetime"] - datetime.datetime.now(
            tz=moscow_tz
        )
        start_in_time_m = start_time.seconds // 60

        text += (
            f"Встреча: {caldav_event['title']}. Начнется в через "
            f"{start_in_time_m} минут "
        )
    return {
        **response_base,
        "response": {"text": text, "end_session": "true"},
    }


if __name__ == "__main__":
    print(handler({}, {}))
