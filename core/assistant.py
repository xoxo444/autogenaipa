from dataclasses import dataclass
import re

from autogen_core.models import UserMessage

from core.planner import DynamicPlanner
from core.executor import DAGExecutor
from core.conversation_manager import ConversationManager


@dataclass
class ConversationTurn:
    role: str
    message: str


class PersonalAssistant:

    def __init__(
        self,
        planner: DynamicPlanner,
        executor: DAGExecutor,
        model_client,
    ):
        self.planner = planner
        self.executor = executor
        self.model_client = model_client

        self.memory = ConversationManager()


    async def chat(
        self,
        user_message: str,
    ) -> str:

        original_user_message = user_message

        cities = [
            "noida",
            "delhi",
            "mumbai",
            "bangalore",
            "hyderabad",
            "pune",
            "kolkata",
            "chennai",
        ]

        for city in cities:

            if city in user_message.lower():

                self.memory.remember_city(
                    city.title()
                )

                break


        if self.memory.is_follow_up(
            user_message
        ):

            city = self.memory.get_last_city()

            current_topic = (
                self.memory.get_current_topic()
            )

            if city and current_topic == "weather":

                lowered = user_message.lower()

                if city.lower() not in lowered:

                    user_message = (
                        f"{user_message} in {city}"
                    )


        conversation_context = (
            self.memory.get_history_text(
                limit=10
            )
        )

        session_context = (
            self._build_session_context()
        )


        state = await self.planner.create_plan(
            user_goal=user_message,
            conversation_context=conversation_context,
            session_context=session_context,
        )


        state = await self.executor.execute(
            state
        )


        completed = state.get_completed_results()


        if len(completed) == 1:

            answer = next(
                iter(completed.values())
            )

            answer = str(answer)

        else:

            answer = await self._synthesize(
                state
            )


        self._update_session_from_results(
            state=state,
            answer=answer,
            user_message=original_user_message,
        )


        self.memory.update_user_message(
            original_user_message
        )

        self.memory.update_assistant_message(
            answer
        )


        return answer


    def _build_session_context(
        self,
    ) -> str:

        session = self.memory.session

        context = []


        if session.last_city:

            context.append(
                f"Last known city: {session.last_city}"
            )


        current_topic = (
            self.memory.get_current_topic()
        )

        if current_topic:

            context.append(
                f"Current conversation topic: {current_topic}"
            )


        if session.current_email_draft:

            draft = session.current_email_draft

            context.append(
                "Current email draft:"
            )

            context.append(
                f"Draft ID: {draft.get('draft_id')}"
            )

            if draft.get("recipient"):

                context.append(
                    f"Recipient: {draft.get('recipient')}"
                )

            if draft.get("subject"):

                context.append(
                    f"Subject: {draft.get('subject')}"
                )

            if draft.get("body"):

                context.append(
                    f"Body: {draft.get('body')}"
                )


        if session.last_email:

            context.append(
                f"Last referenced email: "
                f"{session.last_email}"
            )


        if session.current_calendar_event:

            context.append(
                f"Current calendar event: "
                f"{session.current_calendar_event}"
            )


        if not context:

            return "No stored session context."


        return "\n".join(context)


    def _update_session_from_results(
        self,
        state,
        answer: str,
        user_message: str,
    ):

        session = self.memory.session

        session.last_goal = user_message
        session.last_state = state
        session.last_results = (
            state.get_completed_results()
        )


        for task in state.tasks.values():

            if task.status.value != "completed":
                continue


            result_text = str(
                task.result
            )


            if task.assigned_agent == "weather_agent":

                session.last_weather_result = {
                    "result": result_text
                }


            if task.assigned_agent == "gmail_agent":

                self._capture_gmail_memory(
                    result_text=result_text,
                    user_message=user_message,
                )


            if task.assigned_agent == "calendar_agent":

                session.current_calendar_event = {
                    "last_result": result_text
                }


    def _capture_gmail_memory(
        self,
        result_text: str,
        user_message: str,
    ):

        session = self.memory.session


        draft_patterns = [
            r"Draft ID:\s*([A-Za-z0-9_-]+)",
            r"draft_id['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]+)",
            r"draft id\s*[:=]?\s*([A-Za-z0-9_-]+)",
        ]


        draft_id = None


        for pattern in draft_patterns:

            match = re.search(
                pattern,
                result_text,
                re.IGNORECASE,
            )

            if match:

                draft_id = match.group(1)

                break


        if draft_id:

            email_match = re.search(
                r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
                user_message,
            )


            subject_match = re.search(
                r"subject\s+(.+?)(?:\s+(?:and|n)\s+body|\s+body|$)",
                user_message,
                re.IGNORECASE,
            )


            body_match = re.search(
                r"(?:body|message)\s+(.+)$",
                user_message,
                re.IGNORECASE,
            )


            session.current_email_draft = {
                "draft_id": draft_id,

                "recipient": (
                    email_match.group(0)
                    if email_match
                    else None
                ),

                "subject": (
                    subject_match.group(1).strip()
                    if subject_match
                    else None
                ),

                "body": (
                    body_match.group(1).strip()
                    if body_match
                    else None
                ),
            }


        lowered = result_text.lower()

        if (
            "draft sent successfully" in lowered
            or "email sent successfully" in lowered
            or "successfully sent" in lowered
        ):

            session.current_email_draft = None


    async def _synthesize(
        self,
        state,
    ) -> str:

        results = []


        for task in state.tasks.values():

            if task.result:

                results.append(
                    str(task.result)
                )


        prompt = f"""
You are the final response generator for a personal assistant.

USER GOAL:
{state.user_goal}

WORKFLOW RESULTS:
{chr(10).join(results)}

Write one clear and natural final response.

Rules:

- Answer the user's actual question directly.
- Preserve useful details from the results.
- If email results contain multiple emails, list useful details.
- If calendar results contain multiple events, list useful details.
- Combine results naturally when multiple tasks were executed.
- Never mention tasks, agents, workflows, tools, or internal implementation.
- Never expose raw JSON or Python dictionaries.
"""


        response = await self.model_client.create(
            messages=[
                UserMessage(
                    content=prompt,
                    source="assistant",
                )
            ]
        )


        content = response.content


        if isinstance(content, str):
            return content


        return str(content)