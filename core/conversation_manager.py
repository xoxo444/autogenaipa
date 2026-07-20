from core.session import SessionState

class ConversationManager:

    FOLLOW_UP_PHRASES = {
        "send it",
        "send that",
        "send the draft",
        "send as it is",
        "yes send",
        "read it",
        "read that",
        "read the first one",
        "read the second one",
        "first one",
        "second one",
        "that one",
        "this one",
        "what about",
        "what bout",
        "how about",
        "tomorrow",
        "and tomorrow",
        "today",
        "there",
        "again",
        "same",
        "attach it",
        "attach that",
        "summarize it",
        "summarize that",
        "compare them",
        "open it",
        "open that",
        "email it",
        "email that",
        "use that",
        }

    WEATHER_WORDS = {
        "weather",
        "rain",
        "raining",
        "umbrella",
        "forecast",
        "temperature",
        "humidity",
        "wind",
        "hot",
        "cold",
    }

    GMAIL_WORDS = {
        "email",
        "emails",
        "mail",
        "mails",
        "inbox",
        "draft",
        "send",
        "reply",
        "subject",
        "sender",
        "unread",
    }

    CALENDAR_WORDS = {
        "calendar",
        "event",
        "events",
        "meeting",
        "meetings",
        "appointment",
        "schedule",
        "scheduled",
    }

    FILESYSTEM_WORDS = {
    "file",
    "files",
    "folder",
    "directory",
    "document",
    "documents",
    "read",
    "summarize",
    "summary",
    "compare",
    "local",
    "filesystem",
    "pdf",
    "txt",
    "docx",
    "python",
    "project",
}


    def __init__(self):

        self.session = SessionState()

        self.current_topic = None

    def update_user_message(
        self,
        message: str,
    ):

        self.session.conversation_history.append(
            {
                "role": "user",
                "content": message,
            }
        )

        self._detect_topic(message)


    def update_assistant_message(
        self,
        message: str,
    ):

        self.session.conversation_history.append(
            {
                "role": "assistant",
                "content": str(message),
            }
        )


    def _detect_topic(
        self,
        message: str,

        
    ):

        text = message.lower()

        words = set(text.split())


        if words.intersection(
            self.WEATHER_WORDS
        ):

            self.current_topic = "weather"

            return


        if words.intersection(
            self.GMAIL_WORDS
        ):

            self.current_topic = "gmail"

            return


        if words.intersection(
            self.CALENDAR_WORDS
        ):

            self.current_topic = "calendar"

            return
        
        if words.intersection(
            self.FILESYSTEM_WORDS
            ):
            self.current_topic = "filesystem"
            
            return


    def is_follow_up(
        self,
        message: str,
    ) -> bool:

        text = message.lower().strip()


        #follow-up phrases
        for phrase in self.FOLLOW_UP_PHRASES:

            if phrase in text:

                return True


        reference_words = {
             "it",
             "that",
             "them",
             "those",
             "there",
             "this",
             "these",
             "one",
             "ones",
             }

        words = set(text.split())

        if words.intersection(
            reference_words
        ):

            return True

        month_names = {
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        }

        if (
            self.current_topic is not None
            and words.intersection(month_names)
        ):

            return True


        return False


    def remember_city(
        self,
        city: str,
    ):

        self.session.last_city = city


    def get_last_city(self):

        return self.session.last_city


    def get_current_topic(self):

        return self.current_topic


    def get_history(
        self,
        limit: int = 10,
    ):

        return self.session.conversation_history[
            -limit:
        ]


    def get_history_text(
        self,
        limit: int = 10,
    ) -> str:

        history = self.get_history(
            limit=limit
        )

        lines = []

        for message in history:

            role = message.get(
                "role",
                "unknown",
            )

            content = message.get(
                "content",
                "",
            )

            lines.append(
                f"{role}: {content}"
            )

        return "\n".join(lines)