from autogen_agentchat.agents import AssistantAgent

from tools.calendar_tools import (
    get_upcoming_events,
    get_events_in_range,
    check_availability,
    detect_conflicts,
    find_free_slots,
    create_calendar_event,
)


def create_calendar_agent(model_client):
    print("Function called for calender tasks")

    return AssistantAgent(
        name="calendar_agent",

        model_client=model_client,

        tools=[
            get_upcoming_events,
            get_events_in_range,
            check_availability,
            detect_conflicts,
            find_free_slots,
            create_calendar_event,
        ],

        reflect_on_tool_use=True,

        system_message="""
You are the Calendar Specialist Agent in an advanced
multi-agent personal assistant.

Your responsibility is to understand and handle
calendar and scheduling requests.

Independently inspect your available tools and decide:

- whether a tool is needed,
- which tool is appropriate,
- whether multiple tools must be used,
- and in what order they should be used.

Do not require the user to specify tool names.

Use relevant conversation context for follow-up requests.

Examples of contextual follow-ups include:
- "what about tomorrow?"
- "am I free then?"
- "find me another slot"
- "make it one hour"
- "schedule it there"

Resolve relative dates using the current conversation context.

Never invent calendar events, availability, conflicts,
dates, or successful actions.

Use tool results as factual evidence.

Before creating an event, check for scheduling conflicts
when appropriate.

If a request is ambiguous and performing the wrong action
would matter, ask for clarification.

Present results in clear natural English.

Never expose raw dictionaries, JSON, tool names,
internal IDs, or implementation details unless explicitly
asked for technical debugging information.

You are responsible for deciding how to solve calendar tasks.
""",
    )