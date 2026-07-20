from autogen_ext.tools.mcp import (
    McpWorkbench,
    StdioServerParams,
)


ALLOWED_DIRECTORY = r"E:\assistant_files"


def create_filesystem_workbench():

    server_params = StdioServerParams(
        command="npx.cmd",

        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            ALLOWED_DIRECTORY,
        ],

        read_timeout_seconds=60.0,
    )

    return McpWorkbench(
        server_params=server_params
    )