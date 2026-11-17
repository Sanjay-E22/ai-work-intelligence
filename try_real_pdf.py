
from pathlib import Path
from datetime import date

from app.ai.workflow import DocumentWorkflow


# Change this to the location of your actual PDF.
pdf_path = Path(r"C:/Users/sanja/ai-work-intelligence/Task 1.pdf")
print("path readed")
if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

# Read the PDF as binary data.
pdf_content = pdf_path.read_bytes()
print("pdf content finished")
# Create the workflow.
workflow = DocumentWorkflow()

# Process the actual PDF.
result = workflow.process(
    content=pdf_content,
    file_type="pdf",
    today=date.today(),
)

# Display the results.
print("\n========== DOCUMENT SUMMARY ==========")
print(result.summary.summary)

print("\n========== KEY POINTS ==========")
for point in result.summary.key_points:
    print("-", point)

print("\n========== EXTRACTED TASKS ==========")
for index, task in enumerate(result.tasks, start=1):
    print(f"\nTask {index}: {task.description}")
    print("Assignee:", task.assignee)
    print("Deadline:", task.deadline)
    print("Dependencies:", task.dependencies)
    print("Priority:", task.priority)
    print("Execution Status:", task.execution_status)
