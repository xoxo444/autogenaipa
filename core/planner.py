#done
import json
from typing import Any

from autogen_core.models import UserMessage

from core.task import Task
from core.state import SharedState
from core.capability_registry import CapabilityRegistry


class DynamicPlanner:

    MAX_RETRIES = 2

    def __init__(
        self,
        model_client,
        registry: CapabilityRegistry,
    ):
        self.model_client = model_client
        self.registry = registry


    async def create_plan(
        self,
        user_goal: str,
        conversation_context: str = "",
        session_context: str = "",
        memory_context=""
    ) -> SharedState:

        print("[PLANNER] Creating execution plan...")

        capability_context = (
            self.registry.get_planner_context()
        )

        prompt = f"""
You are the planning engine of a multi-agent AI personal assistant.

Your job is to convert the user's request into the smallest valid
executable task plan.

CURRENT USER REQUEST:
{user_goal}


RECENT CONVERSATION:
{conversation_context if conversation_context else "No previous conversation context available."}


CURRENT SESSION MEMORY:
{session_context if session_context else "No stored session objects available."}


AVAILABLE AGENTS AND CAPABILITIES:
{capability_context}

LONG TERM MEMORY:
{memory_context if memory_context else "No relevant memories found."}


PLANNING RULES:

1. Understand the current request using the recent conversation
   and session memory when relevant.

2. Never ask the user to repeat information that already exists
   in the conversation or session memory.

3. Resolve references such as:
   - send it
   - read it
   - that email
   - the first one
   - tomorrow
   - what about July 11
   - delete that event
   using the most recent relevant context.

4. If CURRENT SESSION MEMORY contains an existing email draft and
   the user asks to send it, create a Gmail task that sends that
   existing draft.

5. If the conversation is currently about weather and the user asks
   a follow-up about another date, continue the weather topic unless
   the user explicitly changes the topic.

6. If the conversation is currently about Gmail and the user refers
   to "it", "that email", "the first one", or similar references,
   use the relevant email context.

7. If the conversation is currently about Calendar and the user refers
   to an event indirectly, use the relevant calendar context.

8. Break the request into only the tasks actually required.

9. Assign every task to exactly one available specialist agent.

10. The assigned_agent value must exactly match an agent name from
    AVAILABLE AGENTS AND CAPABILITIES.

11. Never invent agents or capabilities.

12. Each task must have a unique snake_case task ID.

13. Dependencies must contain task IDs, not agent names.

14. Add a dependency only when one task genuinely requires information
    produced by another task.

15. Independent tasks must have empty dependencies so they can execute
    concurrently.

16. Preserve all useful details in task descriptions.

For example, if the user provides:

recipient
subject
email body
city
date
time
event title

include those details in the relevant task description.

17. Never reduce a detailed user request to a vague description.

Bad:
"Handle the email."

Good:
"Create an email draft to abc@example.com with subject 'Meeting'
and body 'Can we meet tomorrow at 3 PM?'"

18. Keep the plan minimal.

19. Do not create unnecessary analysis or summarization tasks.

20. Do not execute tasks yourself.

21. Do not answer the user's question.

22. Return valid JSON only.

23. Do not use markdown code fences.

24. Do not include text before or after the JSON.

25. If the user's request can be answered using the LONG TERM MEMORY
or is simply conversational and does not require any specialist
agent, return:

{{
  "goal": "conversation",
  "tasks": []
}}

OUTPUT FORMAT:

{{
    "goal": "concise interpretation of the user's goal",
    "tasks": [
        {{
            "id": "unique_snake_case_task_id",
            "description": "complete executable instruction with all known context",
            "assigned_agent": "exact_registered_agent_name",
            "dependencies": [],
            "requires_approval": false
        }}
    ]
}}


DEPENDENCY EXAMPLE:

User request:

"Find my interview email and check whether I am free at that time."

Correct structure:

Task 1:
Search Gmail for the relevant interview email and extract the
interview date and time.

Task 2:
Check Calendar availability for the interview date and time found
by Task 1.

Task 2 depends on Task 1.


PARALLEL EXAMPLE:

User request:

"Tell me the current weather in Noida and show my upcoming events."

Create:

Task 1:
Get current weather for Noida.

Task 2:
Retrieve upcoming calendar events.

Both tasks have empty dependencies.




FOLLOW-UP EXAMPLE:

Previous context:
An email draft exists with draft ID abc123.

Current user request:
"send it as it is"

Create one task assigned to gmail_agent instructing it to send the
existing draft with ID abc123.

Do not create another draft.
Do not ask for recipient, subject, or body again.


Now create the minimal execution plan for the CURRENT USER REQUEST.
"""

        response = await self.model_client.create(
            messages=[
                UserMessage(
                    content=prompt,
                    source="planner",
                )
            ]
        )

        raw_content = response.content

        plan_data = self._parse_plan(
            raw_content
        )

        self._validate_plan(
            plan_data
        )

        state = self._build_state(
            user_goal=user_goal,
            plan_data=plan_data,
        )

        state.log_event(
            event_type="plan_created",
            details={
                "task_count": len(state.tasks),
                "planner_goal": plan_data.get(
                    "goal",
                    user_goal,
                ),
            },
        )

        print(
            f"[PLANNER] Plan created with "
            f"{len(state.tasks)} task(s)."
        )

        return state


    def _parse_plan(
        self,
        raw_content: Any,
    ) -> dict:

        if isinstance(raw_content, dict):
            return raw_content

        if isinstance(raw_content, list):

            text_parts = []

            for item in raw_content:

                if isinstance(item, str):
                    text_parts.append(item)

                elif isinstance(item, dict):

                    text = item.get("text")

                    if text:
                        text_parts.append(text)

                elif hasattr(item, "text"):

                    text = getattr(
                        item,
                        "text",
                        None,
                    )

                    if text:
                        text_parts.append(text)

            raw_content = "".join(text_parts)

        if not isinstance(raw_content, str):

            raise ValueError(
                "Planner returned an unsupported "
                f"response format: {type(raw_content)}"
            )

        cleaned = raw_content.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]

        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        try:

            return json.loads(cleaned)

        except json.JSONDecodeError as error:

            print("\n[PLANNER RAW OUTPUT]")
            print(raw_content)
            print()

            raise ValueError(
                "Planner returned invalid JSON. "
                f"JSON error: {error}"
            )


    def _validate_plan(
        self,
        plan_data: dict,
    ):

        if not isinstance(plan_data, dict):

            raise ValueError(
                "Planner output must be a JSON object."
            )

        if "tasks" not in plan_data:

            raise ValueError(
                "Plan does not contain a 'tasks' field."
            )

        tasks = plan_data["tasks"]

        if not isinstance(tasks, list):

            raise ValueError(
                "Plan 'tasks' must be a list."
            )

        if not tasks:
            plan_data["goal"] = plan_data.get("goal", "")
            plan_data["tasks"] = []
            return

        task_ids = set()

        for task_data in tasks:

            if not isinstance(task_data, dict):

                raise ValueError(
                    "Every task must be a JSON object."
                )

            required_fields = {
                "id",
                "description",
                "assigned_agent",
            }

            missing_fields = (
                required_fields
                - set(task_data.keys())
            )

            if missing_fields:

                raise ValueError(
                    "Task is missing required fields: "
                    f"{sorted(missing_fields)}"
                )

            task_id = task_data["id"]

            if not isinstance(task_id, str) or not task_id:

                raise ValueError(
                    "Every task requires a valid string ID."
                )

            if task_id in task_ids:

                raise ValueError(
                    f"Duplicate task ID: {task_id}"
                )

            task_ids.add(task_id)

            agent_name = task_data[
                "assigned_agent"
            ]

            if not self.registry.has_agent(
                agent_name
            ):

                raise ValueError(
                    "Planner selected unknown agent: "
                    f"{agent_name}"
                )

            dependencies = task_data.get(
                "dependencies",
                [],
            )

            if not isinstance(dependencies, list):

                raise ValueError(
                    f"Dependencies for '{task_id}' "
                    "must be a list."
                )

        for task_data in tasks:

            task_id = task_data["id"]

            dependencies = task_data.get(
                "dependencies",
                [],
            )

            for dependency in dependencies:

                if dependency not in task_ids:

                    raise ValueError(
                        f"Task '{task_id}' depends on "
                        f"unknown task '{dependency}'."
                    )

                if dependency == task_id:

                    raise ValueError(
                        f"Task '{task_id}' cannot "
                        "depend on itself."
                    )

        self._detect_cycles(tasks)


    def _detect_cycles(
        self,
        tasks: list[dict],
    ):

        graph = {
            task["id"]: task.get(
                "dependencies",
                [],
            )
            for task in tasks
        }

        visiting = set()
        visited = set()

        def visit(task_id: str):

            if task_id in visiting:

                raise ValueError(
                    "Circular dependency detected "
                    f"at task '{task_id}'."
                )

            if task_id in visited:
                return

            visiting.add(task_id)

            for dependency in graph[task_id]:
                visit(dependency)

            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in graph:
            visit(task_id)


    def _build_state(
        self,
        user_goal: str,
        plan_data: dict,
    ) -> SharedState:

        state = SharedState(
            user_goal=user_goal
        )

        for task_data in plan_data["tasks"]:

            task = Task(
                id=task_data["id"],

                description=task_data[
                    "description"
                ],

                assigned_agent=task_data[
                    "assigned_agent"
                ],

                dependencies=task_data.get(
                    "dependencies",
                    [],
                ),

                requires_approval=task_data.get(
                    "requires_approval",
                    False,
                ),
            )

            state.add_task(task)

        return state