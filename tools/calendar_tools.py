import asyncio
from datetime import datetime, timezone, timedelta

from googleapiclient.discovery import build

from auth.google_auth import get_google_credentials

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
]

def get_calendar_service():
    try:
        creds = get_google_credentials(
            scopes=CALENDAR_SCOPES,
            token_file="calendar_token.json",
        )

        return build(
            "calendar",
            "v3",
            credentials=creds,
        )
    except Exception as error:
        print("Error:", error)


async def get_upcoming_events(max_results: int = 10) -> dict:
    """Get upcoming calendar events."""

    print("[TOOL] get_upcoming_events called")

    try:
        service = get_calendar_service()

        now = datetime.now(timezone.utc).isoformat()
        

        response = await asyncio.to_thread(
            lambda: service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = response.get("items", [])

        return {
            "success": True,
            "event_count": len(events),
            "events": [
                clean_event(event)
                for event in events
            ],
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def get_events_in_range(
    start_time: str,
    end_time: str,
) -> dict:
    """
    Get calendar events between two ISO datetime values.

    Example:
    2026-07-10T09:00:00+05:30
    """

    print("[TOOL] get_events_in_range called")

    try:
        service = get_calendar_service()

        response = await asyncio.to_thread(
            lambda: service.events()
            .list(
                calendarId="primary",
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = response.get("items", [])

        return {
            "success": True,
            "event_count": len(events),
            "events": [
                clean_event(event)
                for event in events
            ],
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def check_availability(
    start_time: str,
    end_time: str,
) -> dict:
    """
    Check whether the user is free during a time range.
    """

    print("[TOOL] check_availability called")

    try:
        service = get_calendar_service()

        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [
                {
                    "id": "primary"
                }
            ],
        }

        response = await asyncio.to_thread(
            lambda: service.freebusy()
            .query(body=body)
            .execute()
        )

        busy_periods = (
            response
            .get("calendars", {})
            .get("primary", {})
            .get("busy", [])
        )

        return {
            "success": True,
            "available": len(busy_periods) == 0,
            "requested_start": start_time,
            "requested_end": end_time,
            "busy_periods": busy_periods,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def detect_conflicts(
    start_time: str,
    end_time: str,
) -> dict:
    """
    Find events conflicting with a proposed time range.
    """

    print("[TOOL] detect_conflicts called")

    result = await get_events_in_range(
        start_time=start_time,
        end_time=end_time,
    )

    if not result.get("success"):
        return result

    conflicts = result["events"]

    return {
        "success": True,
        "has_conflict": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicting_events": conflicts,
    }


async def find_free_slots(
    start_time: str,
    end_time: str,
    duration_minutes: int = 60,
) -> dict:
    """
    Find free slots within a time window.
    """

    print("[TOOL] find_free_slots called")

    try:
        service = get_calendar_service()

        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [
                {
                    "id": "primary"
                }
            ],
        }

        response = await asyncio.to_thread(
            lambda: service.freebusy()
            .query(body=body)
            .execute()
        )

        busy_periods = (
            response
            .get("calendars", {})
            .get("primary", {})
            .get("busy", [])
        )

        window_start = datetime.fromisoformat(
            start_time.replace("Z", "+00:00")
        )

        window_end = datetime.fromisoformat(
            end_time.replace("Z", "+00:00")
        )

        duration = timedelta(
            minutes=duration_minutes
        )

        busy_intervals = []

        for busy in busy_periods:
            busy_start = datetime.fromisoformat(
                busy["start"].replace("Z", "+00:00")
            )

            busy_end = datetime.fromisoformat(
                busy["end"].replace("Z", "+00:00")
            )

            busy_intervals.append(
                (busy_start, busy_end)
            )

        busy_intervals.sort(
            key=lambda item: item[0]
        )

        free_slots = []

        cursor = window_start

        for busy_start, busy_end in busy_intervals:

            if busy_start - cursor >= duration:
                free_slots.append({
                    "start": cursor.isoformat(),
                    "end": busy_start.isoformat(),
                })

            if busy_end > cursor:
                cursor = busy_end

        if window_end - cursor >= duration:
            free_slots.append({
                "start": cursor.isoformat(),
                "end": window_end.isoformat(),
            })

        return {
            "success": True,
            "duration_minutes": duration_minutes,
            "free_slots": free_slots,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
    location: str = "",
) -> dict:
    """
    Create a calendar event.

    Later this tool will be protected by the Policy Engine.
    """

    print("[TOOL] create_calendar_event called")

    try:
        service = get_calendar_service()

        event_body = {
            "summary": title,

            "description": description,

            "location": location,

            "start": {
                "dateTime": start_time,
            },

            "end": {
                "dateTime": end_time,
            },
        }

        event = await asyncio.to_thread(
            lambda: service.events()
            .insert(
                calendarId="primary",
                body=event_body,
            )
            .execute()
        )

        return {
            "success": True,
            "event": clean_event(event),
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def update_calendar_event(
    event_id: str,
    title: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    description: str | None = None,
    location: str | None = None,
) -> dict:
    """
    Update an existing calendar event.
    """

    print("[TOOL] update_calendar_event called")

    try:
        service = get_calendar_service()

        event = await asyncio.to_thread(
            lambda: service.events()
            .get(
                calendarId="primary",
                eventId=event_id,
            )
            .execute()
        )

        if title is not None:
            event["summary"] = title

        if description is not None:
            event["description"] = description

        if location is not None:
            event["location"] = location

        if start_time is not None:
            event["start"] = {
                "dateTime": start_time
            }

        if end_time is not None:
            event["end"] = {
                "dateTime": end_time
            }

        updated_event = await asyncio.to_thread(
            lambda: service.events()
            .update(
                calendarId="primary",
                eventId=event_id,
                body=event,
            )
            .execute()
        )

        return {
            "success": True,
            "event": clean_event(updated_event),
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def delete_calendar_event(
    event_id: str,
) -> dict:
    """
    Delete an existing calendar event.

    Later this tool will require explicit approval.
    """

    print("[TOOL] delete_calendar_event called")

    try:
        service = get_calendar_service()

        await asyncio.to_thread(
            lambda: service.events()
            .delete(
                calendarId="primary",
                eventId=event_id,
            )
            .execute()
        )

        return {
            "success": True,
            "message": "Calendar event deleted.",
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


def clean_event(event: dict) -> dict:
    """Convert Google Calendar event data into clean structured data."""

    start = event.get("start", {})
    end = event.get("end", {})

    return {
        "event_id": event.get("id"),

        "title": event.get(
            "summary",
            "Untitled event",
        ),

        "start": start.get(
            "dateTime",
            start.get("date"),
        ),

        "end": end.get(
            "dateTime",
            end.get("date"),
        ),

        "description": event.get(
            "description"
        ),

        "location": event.get(
            "location"
        ),

        "status": event.get(
            "status"
        ),
    }