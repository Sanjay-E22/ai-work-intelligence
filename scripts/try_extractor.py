from app.ai.agents.extractor import TaskExtractor

extractor = TaskExtractor()

document = """
The API integration is delayed.
Sanjay must complete database migration by Friday.
The testing team is waiting for the updated API endpoint.
"""

result = extractor.extract(document)

for task in result.tasks:
    print("Task:", task.description)
    print("Assignee:", task.assignee)
    print("Deadline:", task.deadline)
    print("Dependencies:", task.dependencies)
    print("-" * 30)