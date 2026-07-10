from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    WAITING_APPROVAL = "waiting_approval"


@dataclass
class Task:
    id: str
    description: str

    assigned_agent: Optional[str] = None

    dependencies: list[str] = field(default_factory=list)

    status: TaskStatus = TaskStatus.PENDING

    result: Any = None
    error: Optional[str] = None

    retry_count: int = 0
    max_retries: int = 2

    requires_approval: bool = False

    metadata: dict = field(default_factory=dict)


    def is_ready(self, completed_task_ids: set[str]) -> bool:
        """
        Check whether all task dependencies are complete.
        """

        return all(
            dependency in completed_task_ids
            for dependency in self.dependencies
        )


    def mark_running(self):
        self.status = TaskStatus.RUNNING


    def mark_completed(self, result: Any):
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.error = None


    def mark_failed(self, error: str):
        self.status = TaskStatus.FAILED
        self.error = error
        self.retry_count += 1


    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries