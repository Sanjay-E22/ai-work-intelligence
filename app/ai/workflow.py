
from datetime import date

from app.ai.agents.extractor import TaskExtractor
from app.ai.agents.summarizer import DocumentSummarizer
from app.ai.agents.prioritizer import get_priority
from app.ai.agents.dependency_manager import get_execution_status

from app.schemas.workflow import ProcessedTask, WorkflowResult
from app.utils.file_parser import parse_text, parse_pdf
from app.utils.task_normalizer import prepare_processed_tasks

class DocumentWorkflow:
    """Coordinate document parsing and AI processing."""

    def __init__(
        self,
        extractor: TaskExtractor | None = None,
        summarizer: DocumentSummarizer | None = None,
    ):
        self.extractor = extractor or TaskExtractor()
        self.summarizer = summarizer or DocumentSummarizer()

    def process(
        self,
        content: bytes,
        file_type: str,
        today: date | None = None,
        completed_tasks: set[str] | None = None,
    ) -> WorkflowResult:
        """
        WHY: Process a document and combine all analysis results.
        ARGS:
            content - Uploaded document bytes.
            file_type - Supported file type: txt or pdf.
            today - Reference date for task prioritization.
            completed_tasks - Descriptions of completed tasks.
        RETURN: Combined summary and processed tasks.
        RAISE: ValueError for unsupported or invalid documents;
               processing errors from the AI components may propagate.
        """

        # Step 1: Parse the uploaded document.
        file_type = file_type.lower().strip()

        if file_type == "txt":
            document_text = parse_text(content)
        elif file_type == "pdf":
            document_text = parse_pdf(content)
        else:
            raise ValueError("Unsupported file type. Use txt or pdf.")

        reference_date = today or date.today()
        completed = completed_tasks or set()

        # Step 2: Run independent processing components.
        summary = self.summarizer.summarize(document_text)
        extraction_result = self.extractor.extract(document_text)

        # Step 3: Calculate priority and execution status.
        processed_tasks = []

        # for task in extraction_result.tasks:
        #     priority = get_priority(task.deadline, reference_date)

        #     execution_status = get_execution_status(
        #         task=task,
        #         completed_tasks=completed,
        #     )

        #     processed_task = ProcessedTask(
        #         **task.model_dump(),
        #         priority=priority,
        #         execution_status=execution_status,
        #     )
        processed_tasks = prepare_processed_tasks(
    extracted_tasks=extraction_result.tasks,
    completed_tasks=completed_tasks,
    today=today,
)

            # processed_tasks.append(processed_task)

        # Step 4: Return the combined result.
        return WorkflowResult(
            summary=summary,
            tasks=processed_tasks,
        )
