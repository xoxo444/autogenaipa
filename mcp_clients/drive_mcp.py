from autogen_ext.tools.mcp import (
    McpWorkbench,
    StreamableHttpServerParams,
)

from auth.google_auth import get_google_credentials


DRIVE_MCP_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def create_drive_workbench():

    credentials = get_google_credentials(
        scopes=DRIVE_MCP_SCOPES,
        token_file="drive_mcp_token.json",
    )

    if not credentials.token:
        raise RuntimeError(
            "Could not obtain Google Drive access token."
        )

    server_params = StreamableHttpServerParams(
        url="https://drivemcp.googleapis.com/mcp/v1",

        headers={
            "Authorization": (
                f"Bearer {credentials.token}"
            )
        },

        timeout=30.0,

        sse_read_timeout=300.0,
    )

    return McpWorkbench(
        server_params=server_params
    )