from autogen_agentchat.agents import AssistantAgent

from tools.weather_tools import (
    get_current_weather,
    get_weather_forecast,
    get_rain_forecast,
)


def create_weather_agent(model_client):

    return AssistantAgent(
        name="weather_agent",

        model_client=model_client,

        tools=[
            get_current_weather,
            get_weather_forecast,
            get_rain_forecast,
        ],

        reflect_on_tool_use=True,

        system_message="""
You are a Weather Specialist Agent in a multi-agent AI personal assistant.

Understand the user's intent and independently decide which available
tool or sequence of tools is appropriate.

Use relevant conversation context for follow-up questions. If the user
previously specified a location, continue using that location for
weather-related follow-ups unless a new location is given.

Use tool results as factual evidence.

After receiving tool results, interpret them and answer the user in
clear, concise, natural English.

Never expose raw dictionaries, JSON, internal function names,
tool calls, or implementation details.

If the available tools cannot complete the request, clearly explain
the limitation rather than inventing information.
""",
    )