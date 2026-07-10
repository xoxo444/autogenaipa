from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:

    last_city: str | None = None

    current_topic: str | None = None

    last_agent: str | None = None

    last_goal: str | None = None

    last_state: Any = None

    last_results: dict = field(
        default_factory=dict
    )

    conversation_history: list[dict] = field(
        default_factory=list
    )

    extracted_entities: dict = field(
        default_factory=dict
    )

    current_email_draft: dict | None = None

    last_email: dict | None = None

    recent_emails: list[dict] = field(
        default_factory=list
    )

    current_calendar_event: dict | None = None

    recent_calendar_events: list[dict] = field(
        default_factory=list
    )

    last_weather_result: dict | None = None

    workflow_active: bool = False