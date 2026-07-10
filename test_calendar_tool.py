import asyncio

from tools.calender_tools import get_upcoming_events


async def main():
    result = await get_upcoming_events(max_results=10)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())