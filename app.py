import asyncio
import os

from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.weather_agent import create_weather_agent
from agents.gmail_agent import create_gmail_agent
from agents.calendar_agent import create_calendar_agent

from core.registry_setup import build_registry
from core.planner import DynamicPlanner
from core.executor import DAGExecutor
from core.assistant import PersonalAssistant

load_dotenv()

def create_model_client():

    return OpenAIChatCompletionClient(

        model="openai/gpt-oss-20b",

        api_key=os.getenv("GROQ_API_KEY"),

        base_url="https://api.groq.com/openai/v1",

        model_info={

            "vision": False,

            "function_calling": True,

            "json_output": True,

            "structured_output": True,

            "family": "openai",

        },
    )


def print_banner():

    print("\n" + "=" * 65)
    print("        MULTI-AGENT PERSONAL ASSISTANT")
    print("=" * 65)
    print("Available Specialists")
    print(" • Weather")
    print(" • Gmail")
    print(" • Calendar")
    print("\nPlanner : Enabled")
    print("Executor: Enabled")
    print("Assistant Layer: Enabled")
    print("=" * 65)
    print("Type 'exit' to quit.")
    print("=" * 65)


async def build_system():

    model_client = create_model_client()

    weather_agent = create_weather_agent(
        model_client
    )

    gmail_agent = create_gmail_agent(
        model_client
    )

    calendar_agent = create_calendar_agent(
        model_client
    )

    registry = build_registry(
        weather_agent=weather_agent,
        gmail_agent=gmail_agent,
        calendar_agent=calendar_agent,
    )

    planner = DynamicPlanner(
        model_client=model_client,
        registry=registry,
    )

    executor = DAGExecutor(
        registry=registry,
    )

    assistant = PersonalAssistant(
        planner=planner,
        executor=executor,
        model_client=model_client,
    )

    return model_client, assistant


async def main():

    model_client, assistant = await build_system()

    print_banner()

    try:

        while True:

            user_query = input("\nYou: ").strip()

            if not user_query:
                continue

            if user_query.lower() == "exit":
                break

            try:

                answer = await assistant.chat(
                    user_query
                )

                print("\nAssistant:\n")
                print(answer)

            except Exception as error:

                print("\n[APPLICATION ERROR]")
                print(error)

    finally:

        await model_client.close()

        print("\nGoodbye!")


if __name__ == "__main__":
    asyncio.run(main())