import asyncio

from mcp_clients.filesystem_mcp import (
    create_filesystem_workbench,
)

async def main():

    workbench = create_filesystem_workbench()

    async with workbench:

        tools = await workbench.list_tools()

        for tool in tools:
            print(tool)

asyncio.run(main())