import asyncio
import os

from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.gmail_agent import create_gmail_agent


load_dotenv()


async def main():

    model_client = OpenAIChatCompletionClient(
        model="gemini-2.5-flash-lite",

        api_key=os.getenv(
            "GEMINI_API_KEY"
        ),

        base_url=(
            "https://generativelanguage.googleapis.com/"
            "v1beta/openai/"
        ),

        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": "unknown",
            "structured_output": True,
        },
    )

    gmail_agent = create_gmail_agent(
        model_client
    )

    print("\nGmail Agent running.")
    print("Type 'exit' to stop.\n")

    try:

        while True:

            user_input = input(
                "You: "
            ).strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                break

            try:

                result = await gmail_agent.run(
                    task=user_input
                )

                print("\nGmail Agent:")
                print(
                    result.messages[-1].content
                )
                print()

            except Exception as error:

                print(
                    f"\nError: {error}\n"
                )

    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())