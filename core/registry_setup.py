from core.capability_registry import (
    CapabilityRegistry,
    AgentCapability,
)


def build_registry(
    weather_agent,
    gmail_agent,
    calendar_agent,
):

    registry = CapabilityRegistry()


    registry.register_agent(
        name="weather_agent",

        description=(
            "Handles weather conditions, forecasts, "
            "temperature and rain-related questions."
        ),

        capabilities=[
            AgentCapability(
                name="current_weather",
                description=(
                    "Retrieve current weather conditions "
                    "for a location."
                ),
                examples=[
                    "Weather in Noida",
                    "How hot is Delhi right now?",
                ],
            ),

            AgentCapability(
                name="weather_forecast",
                description=(
                    "Retrieve future weather forecasts."
                ),
                examples=[
                    "Forecast for Mumbai",
                    "Weather for the next five days",
                ],
            ),

            AgentCapability(
                name="rain_forecast",
                description=(
                    "Check future rain probability."
                ),
                examples=[
                    "Will it rain tomorrow?",
                ],
            ),
        ],

        agent=weather_agent,
    )


    registry.register_agent(
        name="gmail_agent",

        description=(
            "Searches, reads and analyses Gmail messages "
            "and creates email drafts."
        ),

        capabilities=[
            AgentCapability(
                name="recent_emails",
                description="Retrieve recent emails.",
            ),

            AgentCapability(
                name="search_email",
                description=(
                    "Search the mailbox for emails matching "
                    "topics, people or Gmail search queries."
                ),
            ),

            AgentCapability(
                name="read_email",
                description=(
                    "Read and analyse the content of an email."
                ),
            ),

            AgentCapability(
                name="email_triage",
                description=(
                    "Inspect unread and important email signals."
                ),
            ),

            AgentCapability(
                name="draft_email",
                description=(
                    "Create an email draft without sending it."
                ),
            ),
        ],

        agent=gmail_agent,
    )


    registry.register_agent(
        name="calendar_agent",

        description=(
            "Handles calendar inspection, availability, "
            "conflicts and scheduling."
        ),

        capabilities=[
            AgentCapability(
                name="upcoming_events",
                description=(
                    "Retrieve upcoming calendar events."
                ),
            ),

            AgentCapability(
                name="events_in_range",
                description=(
                    "Retrieve events within a time range."
                ),
            ),

            AgentCapability(
                name="availability",
                description=(
                    "Check whether the user is available "
                    "during a time range."
                ),
            ),

            AgentCapability(
                name="conflict_detection",
                description=(
                    "Detect scheduling conflicts."
                ),
            ),

            AgentCapability(
                name="free_slot_discovery",
                description=(
                    "Find available scheduling windows."
                ),
            ),

            AgentCapability(
                name="create_event",
                description=(
                    "Create a calendar event."
                ),
            ),
        ],

        agent=calendar_agent,
    )


    return registry