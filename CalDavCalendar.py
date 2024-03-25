import datetime

import caldav
import dotenv

dotenv.load_dotenv()


class Calendar:
    def __init__(self, url, user_name, password, timezone) -> None:
        self.url = url
        self.user_name = user_name
        self.password = password
        self.client = caldav.DAVClient(
            url=self.url, username=self.user_name, password=self.password
        )
        self.timezone = timezone

    def get_calendars(self):
        principal = self.client.principal()
        calendars = principal.calendars()
        return calendars

    def get_calendar(self, calendar_name):
        for calendar in self.get_calendars():
            if calendar.name == calendar_name:
                return calendar

    def parse_events(self, events_list):
        parsed_events = []
        for eventraw in events_list:
            for component in eventraw.icalendar_instance.walk():
                if component.name == "VEVENT":
                    parsed_events.append(
                        {
                            "title": str(component.get("summary")),
                            "description": str(component.get("description")),
                            "start_datetime": component.get("dtstart").dt,
                            "end_datetime": component.get("dtend").dt,
                        }
                    )
        parsed_events.sort(key=lambda event: event["start_datetime"])
        return parsed_events

    def get_events(self, calendar_name, start_datetime, end_datetime):
        calendar = self.get_calendar(calendar_name)
        if calendar:
            events = calendar.date_search(
                start=start_datetime,
                end=end_datetime,
                expand=True,
            )
            parsed_events = self.parse_events(events)
            return parsed_events

    def get_today_events(self, calendar_name):
        today = datetime.date.today()
        start_datetime = datetime.datetime(
            today.year, today.month, today.day, 0, 0, 0, tzinfo=self.timezone
        )
        end_datetime = datetime.datetime(
            today.year,
            today.month,
            today.day,
            23,
            59,
            59,
            tzinfo=self.timezone,
        )
        events = self.get_events(
            calendar_name=calendar_name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        return events

    def get_close_future_events(self, calendar_name):
        start_datetime = datetime.datetime.now(tz=self.timezone)
        end_datetime = datetime.datetime.now(
            tz=self.timezone
        ) + datetime.timedelta(minutes=10)
        events = self.get_today_events(
            calendar_name=calendar_name,
        )
        events = [
            event
            for event in events
            if start_datetime <= event.get("start_datetime") <= end_datetime
        ]
        return events
