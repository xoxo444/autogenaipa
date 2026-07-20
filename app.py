import asyncio
import os
import traceback

from dotenv import load_dotenv

from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.weather_agent import create_weather_agent
from agents.gmail_agent import create_gmail_agent
from agents.calendar_agent import create_calendar_agent
from agents.filesystem_agent import create_filesystem_agent

from core.registry_setup import build_registry
from core.planner import DynamicPlanner
from core.executor import DAGExecutor
from core.conversation_manager import ConversationManager
from core.assistant import PersonalAssistant

from memory.memory_manager import MemoryManager

from mcp_clients.filesystem_mcp import create_filesystem_workbench

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
    print(" • Filesystem MCP")
    print("\nPlanner : Enabled")
    print("Executor: Enabled")
    print("Assistant Layer: Enabled")
    print("MCP Layer: Enabled")
    print("=" * 65)
    print("Type 'exit' to quit.")
    print("=" * 65)


async def build_system(filesystem_workbench):

    print("STEP 1 - Model Client")
    model_client = create_model_client()

    print("STEP 2 - Weather Agent")
    weather_agent = create_weather_agent(model_client)

    print("STEP 3 - Gmail Agent")
    gmail_agent = create_gmail_agent(model_client)

    print("STEP 4 - Calendar Agent")
    calendar_agent = create_calendar_agent(model_client)

    print("STEP 5 - Filesystem Agent")
    filesystem_agent = create_filesystem_agent(
        model_client=model_client,
        filesystem_workbench=filesystem_workbench,
    )

    print("STEP 6 - Registry")
    registry = build_registry(
        weather_agent=weather_agent,
        gmail_agent=gmail_agent,
        calendar_agent=calendar_agent,
        drive_agent=None,
        filesystem_agent=filesystem_agent,
    )

    print("STEP 7 - Planner")
    planner = DynamicPlanner(
        model_client=model_client,
        registry=registry,
    )

    print("STEP 8 - Executor")
    executor = DAGExecutor(
        registry=registry,
    )

    print("STEP 9 - Conversation Manager")
    conversation_manager = ConversationManager()

    print("STEP 10 - Memory Manager")
    memory_manager = MemoryManager()

    print("STEP 11 - Personal Assistant")
    assistant = PersonalAssistant(
        planner=planner,
        executor=executor,
        conversation_manager=conversation_manager,
        memory_manager=memory_manager,
        model_client=model_client,
    )

    print("STEP 12 - Build Complete")

    return model_client, assistant


async def run_assistant(assistant):

    print("STEP 13 - Starting Chat")
    print_banner()

    while True:

        try:

            user_query = input("\nYou: ").strip()

            if not user_query:
                continue

            if user_query.lower() == "exit":
                break

            print("\n===== CALLING assistant.chat() =====")

            answer = await assistant.chat(user_query)

            print("\n===== assistant.chat() RETURNED =====")

            print("\nAssistant:\n")
            print(answer)

        except BaseException as e:

            print("\n========== FULL ERROR ==========")

            traceback.print_exc()

            print("\nException Type:", type(e))
            print("Exception:", e)

            print("\n===============================\n")


async def main():

    print("STEP 0 - Creating Filesystem Workbench")

    filesystem_workbench = create_filesystem_workbench()

    async with filesystem_workbench:

        model_client = None

        try:

            print("STEP A - Building System")

            model_client, assistant = await build_system(
                filesystem_workbench
            )

            print("STEP B - Running Assistant")

            await run_assistant(assistant)

        except BaseException:

            print("\n========== MAIN ERROR ==========")
            traceback.print_exc()
            print("===============================\n")

        finally:

            print("STEP C - Closing Model Client")

            if model_client is not None:
                await model_client.close()

    print("\nGoodbye!")


if __name__ == "__main__":
    asyncio.run(main())