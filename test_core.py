from tools.core.task import Task
from tools.core.state import SharedState
state = SharedState(
    user_goal="Prepare me for my upcoming interview"
)

task_1 = Task(
    id="find_email",
    description="Find the interview invitation email",
    assigned_agent="gmail_agent",
)

task_2 = Task(
    id="extract_details",
    description="Extract company, role, date and time",
    assigned_agent="gmail_agent",
    dependencies=["find_email"],
)

task_3 = Task(
    id="research_company",
    description="Research the company and role",
    assigned_agent="research_agent",
    dependencies=["extract_details"],
)

task_4 = Task(
    id="check_calendar",
    description="Check calendar availability before the interview",
    assigned_agent="calendar_agent",
    dependencies=["extract_details"],
)

state.add_task(task_1)
state.add_task(task_2)
state.add_task(task_3)
state.add_task(task_4)
print("\nFIRST READY TASKS:")

for task in state.get_ready_tasks():
    print(task.id)

task_1.mark_completed(
    {"email_id": "example_123"}
)
print("\nAFTER EMAIL TASK COMPLETES:")

for task in state.get_ready_tasks():
    print(task.id)

task_2.mark_completed({
    "company": "Example Company",
    "role": "AI Intern",
    "interview_date": "2026-07-15",
})
print("\nAFTER DETAILS ARE EXTRACTED:")

for task in state.get_ready_tasks():
    print(task.id)


print("\nSTATE SUMMARY:")

print(state.summary())
