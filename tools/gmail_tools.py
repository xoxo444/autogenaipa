import mimetypes
import os
import asyncio
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from auth.google_auth import get_google_credentials

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


def get_gmail_service():
    creds = get_google_credentials(
        scopes=GMAIL_SCOPES,
        token_file="gmail_token.json",
    )

    return build(
        "gmail",
        "v1",
        credentials=creds,
    )


def get_header(headers: list, header_name: str):
    for header in headers:
        if header.get("name", "").lower() == header_name.lower():
            return header.get("value")

    return None


def extract_body(payload: dict) -> str:
    """
    Extract plain text from a Gmail message payload.
    Handles simple and multipart emails.
    """

    body_data = payload.get("body", {}).get("data")

    if body_data:
        return base64.urlsafe_b64decode(
            body_data
        ).decode(
            "utf-8",
            errors="ignore",
        )

    for part in payload.get("parts", []):

        if part.get("mimeType") == "text/plain":

            data = part.get(
                "body",
                {},
            ).get("data")

            if data:
                return base64.urlsafe_b64decode(
                    data
                ).decode(
                    "utf-8",
                    errors="ignore",
                )

        nested_body = extract_body(part)

        if nested_body:
            return nested_body

    return ""


def clean_message_metadata(message_details: dict) -> dict:

    payload = message_details.get("payload", {})
    headers = payload.get("headers", [])

    return {
        "message_id": message_details.get("id"),

        "thread_id": message_details.get("threadId"),

        "from": get_header(
            headers,
            "From",
        ),

        "to": get_header(
            headers,
            "To",
        ),

        "subject": get_header(
            headers,
            "Subject",
        ),

        "date": get_header(
            headers,
            "Date",
        ),

        "snippet": message_details.get(
            "snippet",
            "",
        ),

        "labels": message_details.get(
            "labelIds",
            [],
        ),
    }


async def get_recent_emails(
    max_results: int = 10
) -> dict:
    """
    Retrieve the user's most recent Gmail messages.
    """

    print("[TOOL] get_recent_emails called")

    try:
        service = get_gmail_service()

        response = await asyncio.to_thread(
            lambda: service.users()
            .messages()
            .list(
                userId="me",
                maxResults=max_results,
            )
            .execute()
        )

        messages = response.get("messages", [])

        emails = []

        for message in messages:

            details = await asyncio.to_thread(
                lambda message_id=message["id"]:
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="metadata",
                    metadataHeaders=[
                        "From",
                        "To",
                        "Subject",
                        "Date",
                    ],
                )
                .execute()
            )

            emails.append(
                clean_message_metadata(details)
            )

        return {
            "success": True,
            "email_count": len(emails),
            "emails": emails,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def search_emails(
    query: str,
    max_results: int = 10,
) -> dict:
    """
    Search Gmail using a Gmail search query.

    Examples:
    interview
    from:example@gmail.com
    subject:internship
    newer_than:7d
    has:attachment
    """

    print(f"[TOOL] search_emails called: {query}")

    try:
        service = get_gmail_service()

        response = await asyncio.to_thread(
            lambda: service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=max_results,
            )
            .execute()
        )

        messages = response.get("messages", [])

        emails = []

        for message in messages:

            details = await asyncio.to_thread(
                lambda message_id=message["id"]:
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="metadata",
                    metadataHeaders=[
                        "From",
                        "To",
                        "Subject",
                        "Date",
                    ],
                )
                .execute()
            )

            emails.append(
                clean_message_metadata(details)
            )

        return {
            "success": True,
            "query": query,
            "email_count": len(emails),
            "emails": emails,
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def read_email(
    message_id: str
) -> dict:
    """
    Read the complete contents of a Gmail message
    using its message ID.
    """

    print(f"[TOOL] read_email called: {message_id}")

    try:
        service = get_gmail_service()

        details = await asyncio.to_thread(
            lambda: service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )

        payload = details.get("payload", {})
        headers = payload.get("headers", [])

        return {
            "success": True,

            "message_id": details.get("id"),

            "thread_id": details.get("threadId"),

            "from": get_header(
                headers,
                "From",
            ),

            "to": get_header(
                headers,
                "To",
            ),

            "subject": get_header(
                headers,
                "Subject",
            ),

            "date": get_header(
                headers,
                "Date",
            ),

            "body": extract_body(payload),
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }


async def get_unread_emails(
    max_results: int = 10
) -> dict:
    """
    Retrieve unread Gmail messages.
    """

    print("[TOOL] get_unread_emails called")

    return await search_emails(
        query="is:unread",
        max_results=max_results,
    )


async def get_important_emails(
    max_results: int = 10
) -> dict:
    """
    Retrieve messages marked important in Gmail.
    """

    print("[TOOL] get_important_emails called")

    return await search_emails(
        query="is:important",
        max_results=max_results,
    )


async def create_email_draft(
    to: str,
    subject: str,
    body: str,
    attachments: list[str] | None = None,
) -> dict:
    """
    Create a Gmail draft.

    If attachments are supplied,
    attach them automatically.
    """

    print("[TOOL] create_email_draft called")

    try:

        service = get_gmail_service()

        print("Attachments:", attachments)

        if attachments:

            message = MIMEMultipart()

            message["to"] = to
            message["subject"] = subject

            message.attach(
                MIMEText(body, "plain")
            )

            for attachment_path in attachments:

                print("Attaching:", attachment_path)

                content_type, encoding = mimetypes.guess_type(
                    attachment_path
                )

                if content_type is None:
                    content_type = "application/octet-stream"

                main_type, sub_type = content_type.split("/", 1)

                with open(
                    attachment_path,
                    "rb",
                ) as file:

                    attachment = MIMEBase(
                        main_type,
                        sub_type,
                    )

                    attachment.set_payload(
                        file.read()
                    )

                encoders.encode_base64(
                    attachment
                )

                attachment.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(attachment_path)}"',
                )

                message.attach(
                    attachment
                )

        #email without attachments
        else:

            message = MIMEText(body)

            message["to"] = to
            message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        draft = await asyncio.to_thread(
            lambda: service.users()
            .drafts()
            .create(
                userId="me",
                body={
                    "message": {
                        "raw": raw_message
                    }
                },
            )
            .execute()
        )

        return {
            "success": True,
            "action": "draft_created",
            "draft_id": draft.get("id"),
            "recipient": to,
            "subject": subject,
            "attachments": attachments if attachments else [],
            "message": "Draft created successfully.",
        }

    except Exception as error:

        import traceback

        traceback.print_exc()

        return {
            "success": False,
            "error": str(error),
        }

async def send_email(
    to: str,
    subject: str,
    body: str,
    attachments: list[str] | None = None,
) -> dict:
    """
    Create and immediately send an email.
    """

    print("[TOOL] send_email called")

    try:

        service = get_gmail_service()

        if attachments:

            message = MIMEMultipart()

            message["to"] = to
            message["subject"] = subject

            message.attach(
                MIMEText(body, "plain")
            )

            for attachment_path in attachments:

                content_type, _ = mimetypes.guess_type(
                    attachment_path
                )

                if content_type is None:
                    content_type = "application/octet-stream"

                main_type, sub_type = content_type.split("/", 1)

                with open(attachment_path, "rb") as file:

                    attachment = MIMEBase(
                        main_type,
                        sub_type,
                    )

                    attachment.set_payload(file.read())

                encoders.encode_base64(
                    attachment
                )

                attachment.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(attachment_path)}"',
                )

                message.attach(
                    attachment
                )

        else:

            message = MIMEText(body)

            message["to"] = to
            message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        sent = await asyncio.to_thread(
            lambda: service.users()
            .messages()
            .send(
                userId="me",
                body={
                    "raw": raw_message
                },
            )
            .execute()
        )

        return {
            "success": True,
            "action": "email_sent",
            "message_id": sent.get("id"),
            "thread_id": sent.get("threadId"),
            "recipient": to,
            "subject": subject,
            "attachments": attachments or [],
            "message": "Email sent successfully.",
        }

    except Exception as error:

        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "error": str(error),
        }