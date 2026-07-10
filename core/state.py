from typing import Any

from core.task import Task, TaskStatus


class SharedState:
    """
    Central workflow state shared by the Planner and Executor.
    """

    def __init__(self, user_goal: str):
        self.user_goal = user_goal

        self.tasks: dict[str, Task] = {}

        self.context: dict[str, Any] = {}

        self.evidence: list[dict] = []

        self.event_log: list[dict] = []


    def add_task(self, task: Task):
        """
        Add a task to the workflow.
        """

        if task.id in self.tasks:
            raise ValueError(
                f"Task '{task.id}' already exists."
            )

        self.tasks[task.id] = task


    def get_task(self, task_id: str):
        """
        Retrieve a task using its ID.
        """

        return self.tasks.get(task_id)


    def get_ready_tasks(self) -> list[Task]:
        """
        Return pending tasks whose dependencies
        have all completed successfully.
        """

        ready_tasks = []

        for task in self.tasks.values():

            if task.status != TaskStatus.PENDING:
                continue

            dependencies_complete = all(
                self.tasks[dependency_id].status
                == TaskStatus.COMPLETED

                for dependency_id
                in task.dependencies
            )

            if dependencies_complete:
                ready_tasks.append(task)

        return ready_tasks


    def add_context(
        self,
        key: str,
        value: Any,
    ):
        """
        Store workflow context or task results.
        """

        self.context[key] = value


    def get_context(
        self,
        key: str,
        default=None,
    ):
        return self.context.get(
            key,
            default,
        )


    def add_evidence(
        self,
        source: str,
        content: Any,
        task_id: str | None = None,
    ):
        """
        Store evidence produced by agents.
        """

        self.evidence.append({
            "source": source,
            "task_id": task_id,
            "content": content,
        })


    def log_event(
        self,
        event_type: str,
        details: dict,
    ):
        """
        Record workflow execution events.
        """

        self.event_log.append({
            "event_type": event_type,
            "details": details,
        })


    def workflow_finished(self) -> bool:
        """
        True when every task has reached
        a terminal state.
        """

        if not self.tasks:
            return False

        terminal_states = {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
        }

        return all(
            task.status in terminal_states
            for task in self.tasks.values()
        )


    def workflow_complete(self) -> bool:
        """
        True only when every task completed successfully.
        """

        if not self.tasks:
            return False

        return all(
            task.status == TaskStatus.COMPLETED
            for task in self.tasks.values()
        )


    def get_completed_results(self) -> dict:
        """
        Return results of successfully completed tasks.
        """

        return {
            task_id: task.result

            for task_id, task
            in self.tasks.items()

            if task.status == TaskStatus.COMPLETED
        }


    def get_failed_tasks(self) -> list[Task]:
        """
        Return all failed tasks.
        """

        return [
            task
            for task in self.tasks.values()
            if task.status == TaskStatus.FAILED
        ]