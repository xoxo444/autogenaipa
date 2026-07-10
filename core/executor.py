import asyncio

from core.state import SharedState
from core.task import Task, TaskStatus
from core.capability_registry import CapabilityRegistry


class DAGExecutor:

    MAX_RETRIES = 2

    def __init__(
        self,
        registry: CapabilityRegistry,
    ):
        self.registry = registry

    async def execute(
        self,
        state: SharedState,
    ) -> SharedState:

        print("\n[EXECUTOR] Starting workflow execution...\n")

        while not state.workflow_finished():

            ready_tasks = state.get_ready_tasks()

            if not ready_tasks:

                unfinished = [
                    task
                    for task in state.tasks.values()
                    if task.status
                    not in {
                        TaskStatus.COMPLETED,
                        TaskStatus.FAILED,
                    }
                ]

                if unfinished:

                    print(
                        "[EXECUTOR] Workflow stalled."
                    )

                break

            print(
                "[EXECUTOR] Ready tasks:",
                [t.id for t in ready_tasks],
            )

            await asyncio.gather(

                *[
                    self._execute_task(
                        task,
                        state,
                    )
                    for task in ready_tasks
                ]

            )

        print("\n[EXECUTOR] Workflow finished.\n")

        return state

    async def _execute_task(
        self,
        task: Task,
        state: SharedState,
    ):

        agent = self.registry.get_agent(
            task.assigned_agent
        )

        if agent is None:

            task.mark_failed(
                "Agent not found."
            )

            return

        dependency_context = (
            self._build_dependency_context(
                task,
                state,
            )
        )

        task.mark_running()

        retries = 0

        while retries <= self.MAX_RETRIES:

            try:

                print(
                    f"[EXECUTOR] Running {task.id}"
                )

                prompt = f"""
Overall Goal

{state.user_goal}

Current Task

{task.description}

Dependency Context

{dependency_context}

Instructions

Complete ONLY this task.

Use tools whenever required.

Return concise but complete information.
"""

                result = await agent.run(
                    task=prompt
                )

                final_result = (
                    result.messages[-1].content
                )

                task.mark_completed(
                    final_result
                )

                state.add_context(
                    task.id,
                    final_result,
                )

                state.add_evidence(
                    source=task.assigned_agent,
                    content=final_result,
                    task_id=task.id,
                )

                print(
                    f"[EXECUTOR] Completed {task.id}"
                )

                return

            except Exception as error:

                retries += 1

                print(
                    f"[EXECUTOR] Retry {retries}/{self.MAX_RETRIES}"
                )

                if retries > self.MAX_RETRIES:

                    task.mark_failed(
                        str(error)
                    )

                    print(
                        f"[EXECUTOR] Failed {task.id}"
                    )

                    return

    def _build_dependency_context(
        self,
        task: Task,
        state: SharedState,
    ):

        if not task.dependencies:

            return "None"

        sections = []

        for dependency in task.dependencies:

            dep_task = state.get_task(
                dependency
            )

            if dep_task:

                sections.append(
                    f"""
Task

{dep_task.description}

Result

{dep_task.result}
"""
                )

        return "\n".join(sections)