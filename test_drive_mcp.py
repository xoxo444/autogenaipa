import asyncio

from mcp_clients.drive_mcp import create_drive_workbench


async def main():

    workbench = create_drive_workbench()

    async with workbench:

        result = await workbench.call_tool(
            "list_recent_files",
            {
                "pageSize": 5,
                "orderBy": "recency",
            },
        )

        print("\nRESULT:\n")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())