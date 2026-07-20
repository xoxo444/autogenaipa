#done
from core.capability_registry import (
    CapabilityRegistry,
    AgentCapability,
)


def build_registry(
    weather_agent,
    gmail_agent,
    calendar_agent,
    drive_agent=None,
    filesystem_agent=None,
):

    registry = CapabilityRegistry()


    registry.register_agent(
        name="weather_agent",

        description=(
            "Handles current weather, forecasts, temperature, "
            "precipitation and rain-related questions."
        ),

        capabilities=[
            AgentCapability(
                name="current_weather",
                description=(
                    "Retrieve current weather conditions "
                    "for a location."
                ),
                examples=[
                    "Weather in Noida",
                    "How hot is Delhi right now?",
                ],
            ),

            AgentCapability(
                name="weather_forecast",
                description=(
                    "Retrieve future weather forecasts "
                    "for a location and date range."
                ),
                examples=[
                    "Forecast for Mumbai",
                    "Weather for the next five days",
                    "What about July 11 and 12?",
                ],
            ),

            AgentCapability(
                name="rain_forecast",
                description=(
                    "Check future rain or precipitation probability."
                ),
                examples=[
                    "Will it rain tomorrow?",
                    "Should I carry an umbrella?",
                ],
            ),
        ],

        agent=weather_agent,
    )


    registry.register_agent(
        name="gmail_agent",

        description=(
            "Searches, reads and analyses Gmail messages, "
            "creates email drafts and sends existing drafts."
        ),

        capabilities=[
            AgentCapability(
                name="recent_emails",
                description=(
                    "Retrieve and inspect recent emails."
                ),
                examples=[
                    "Show my recent emails",
                    "What are my latest emails?",
                ],
            ),

            AgentCapability(
                name="search_email",
                description=(
                    "Search the mailbox for emails matching "
                    "topics, people, subjects or Gmail queries."
                ),
                examples=[
                    "Find my interview email",
                    "Search emails from my mentor",
                ],
            ),

            AgentCapability(
                name="read_email",
                description=(
                    "Read and analyse the content of a selected email."
                ),
                examples=[
                    "Read the first email",
                    "What does that email say?",
                ],
            ),

            AgentCapability(
                name="email_triage",
                description=(
                    "Inspect unread and important email signals."
                ),
                examples=[
                    "Do I have important emails?",
                    "Show unread emails",
                ],
            ),

            AgentCapability(
                name="draft_email",
                description=(
                    "Create an email draft without sending it."
                ),
                examples=[
                    "Draft an email to my mentor",
                    "Compose an email saying I will submit tomorrow",
                ],
            ),

            AgentCapability(
                name="send_email",
                description=(
                    "Send an existing Gmail draft using "
                    "its previously created draft ID."
                ),
                examples=[
                    "Send the draft",
                    "Send it as it is",
                ],
            ),
        ],

        agent=gmail_agent,
    )


    registry.register_agent(
        name="calendar_agent",

        description=(
            "Handles calendar events, date-range inspection, "
            "availability, conflicts and scheduling."
        ),

        capabilities=[
            AgentCapability(
                name="upcoming_events",
                description=(
                    "Retrieve upcoming calendar events."
                ),
                examples=[
                    "What events do I have?",
                    "Show my upcoming meetings",
                ],
            ),

            AgentCapability(
                name="events_in_range",
                description=(
                    "Retrieve calendar events within a specific "
                    "date or time range."
                ),
                examples=[
                    "What events do I have today?",
                    "Show events between July 11 and July 12",
                ],
            ),

            AgentCapability(
                name="availability",
                description=(
                    "Check whether the user is available "
                    "during a time range."
                ),
                examples=[
                    "Am I free tomorrow afternoon?",
                ],
            ),

            AgentCapability(
                name="conflict_detection",
                description=(
                    "Detect scheduling conflicts between events."
                ),
                examples=[
                    "Do I have any conflicting meetings?",
                ],
            ),

            AgentCapability(
                name="free_slot_discovery",
                description=(
                    "Find available scheduling windows."
                ),
                examples=[
                    "Find me a free slot tomorrow",
                ],
            ),

            AgentCapability(
                name="create_event",
                description=(
                    "Create a new calendar event."
                ),
                examples=[
                    "Schedule a meeting tomorrow at 4 PM",
                ],
            ),
        ],

        agent=calendar_agent,
    )


    if drive_agent is not None:

        registry.register_agent(
            name="drive_agent",

            description=(
                "Searches and accesses files stored in "
                "Google Drive through MCP."
            ),

            capabilities=[
                AgentCapability(
                    name="search_drive",
                    description=(
                        "Search Google Drive for files and "
                        "documents matching a request."
                    ),
                    examples=[
                        "Find my internship report in Drive",
                        "Search Drive for my resume",
                    ],
                ),

                AgentCapability(
                    name="find_local_file",
                    description=(
                        "Locate local files by filename, extension, or pattern "
                        "using the Filesystem MCP search tools."
                        ),
                        examples=[
                            "Find resume.pdf",
                            "Locate internship_report.docx",
                            "Find every PDF",
                            "Search for *.txt",
                            ],
                            ),

                AgentCapability(
                    name="list_drive_files",
                    description=(
                        "List and inspect recent files "
                        "available in Google Drive."
                    ),
                    examples=[
                        "Show my recent Drive files",
                    ],
                ),

                AgentCapability(
                    name="read_drive_file",
                    description=(
                        "Read and analyse supported Google Drive files."
                    ),
                    examples=[
                        "Read my internship report from Drive",
                        "Summarize my Drive document",
                    ],
                ),
            ],

            agent=drive_agent,
        )


    if filesystem_agent is not None:

        registry.register_agent(
            name="filesystem_agent",

            description=(
                "Searches, reads, inspects and manages files "
                "inside approved local directories through "
                "Filesystem MCP."
            ),

            capabilities=[
                AgentCapability(
                    name="list_local_files",
                    description=(
                        "List files and directories inside "
                        "approved local filesystem locations."
                    ),
                    examples=[
                        "Show my local files",
                        "What files are in my assistant folder?",
                    ],
                ),

                AgentCapability(
                    name="search_local_files",
                    description=(
                        "Search approved local directories for "
                        "files matching names, patterns or topics."
                    ),
                    examples=[
                        "Find my resume",
                        "Find Python files related to weather",
                        "Search for my internship report",
                    ],
                ),

                AgentCapability(
                    name="read_local_file",
                    description=(
                        "Read and analyse the contents of files "
                        "inside approved local directories."
                    ),
                    examples=[
                        "Read my report",
                        "Summarize this local document",
                        "Explain this Python file",
                    ],
                ),

                AgentCapability(
                    name="local_file_management",
                    description=(
                        "Create directories, write files, edit files, "
                        "and move or rename files when explicitly requested."
                    ),
                    examples=[
                        "Create a notes file",
                        "Rename this file",
                        "Organize these files into a folder",
                    ],
                ),
            ],

            agent=filesystem_agent,
        )


    return registry