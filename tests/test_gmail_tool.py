import asyncio

from tools.gmail_tools import (
    get_recent_emails,
    search_emails,
    get_unread_emails,
    get_important_emails,
)


async def main():

    print("\n--- RECENT EMAILS ---")
    result = await get_recent_emails(5)
    print(result)

    print("\n--- SEARCH EMAILS ---")
    result = await search_emails(
        query="interview",
        max_results=5,
    )
    print(result)

    print("\n--- UNREAD EMAILS ---")
    result = await get_unread_emails(5)
    print(result)

    print("\n--- IMPORTANT EMAILS ---")
    result = await get_important_emails(5)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())