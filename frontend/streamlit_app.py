import os
from typing import Any

import requests
import streamlit as st


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Work Intelligence",
    page_icon="🤖",
    layout="wide",
)

DEFAULT_API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


# ---------------------------------------------------------
# API helpers
# ---------------------------------------------------------

def api_request(
    method: str,
    endpoint: str,
    *,
    params: dict | None = None,
    json: dict | None = None,
    files: dict | None = None,
    timeout: int = 60,
) -> Any:
    """Send an HTTP request to the FastAPI backend."""
    url = f"{st.session_state.api_url.rstrip('/')}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            files=files,
            timeout=timeout,
        )

        if not response.ok:
            try:
                detail = response.json().get("detail", response.text)
            except ValueError:
                detail = response.text

            raise RuntimeError(
                f"API returned {response.status_code}: {detail}"
            )

        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Cannot connect to FastAPI. Make sure the backend is running."
        ) from exc

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "The request timed out. The AI model may still be processing."
        ) from exc


def show_error(error: Exception) -> None:
    st.error(str(error))


def get_summary_text(document: dict) -> str:
    """Handle both nested and plain-text summary response formats."""
    summary = document.get("summary")

    if isinstance(summary, dict):
        return summary.get("summary", "")

    if isinstance(summary, str):
        return summary

    return ""


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

if "last_job_id" not in st.session_state:
    st.session_state.last_job_id = None


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("🤖 AI Work Intelligence")
st.sidebar.caption("Document intelligence and task management")

st.sidebar.text_input(
    "FastAPI Base URL",
    key="api_url",
    help="Example: http://127.0.0.1:8000",
)

if st.sidebar.button("Check backend connection", use_container_width=True):
    try:
        health = api_request("GET", "/health", timeout=10)
        st.sidebar.success(f"Backend connected: {health}")
    except Exception as exc:
        st.sidebar.error(str(exc))

st.sidebar.divider()
st.sidebar.caption("Powered by FastAPI, Ollama and MySQL")


# ---------------------------------------------------------
# Header and navigation
# ---------------------------------------------------------

st.title("AI Work Intelligence Platform")
st.write(
    "Upload work documents, extract actionable tasks, "
    "and manage task priorities and execution status."
)

overview_tab, upload_tab, documents_tab, tasks_tab = st.tabs(
    ["Overview", "Upload", "Documents", "Tasks"]
)


# ---------------------------------------------------------
# Overview
# ---------------------------------------------------------

with overview_tab:
    st.subheader("Project Overview")

    try:
        documents = api_request("GET", "/documents/", timeout=20)
        tasks = api_request("GET", "/tasks/", timeout=20)

        documents = documents if isinstance(documents, list) else []
        tasks = tasks if isinstance(tasks, list) else []

        total_tasks = len(tasks)
        completed_tasks = sum(
            task.get("execution_status") == "completed"
            for task in tasks
        )
        blocked_tasks = sum(
            task.get("execution_status") == "blocked"
            for task in tasks
        )
        in_progress_tasks = sum(
            task.get("execution_status") == "in_progress"
            for task in tasks
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Documents", len(documents))
        col2.metric("Total Tasks", total_tasks)
        col3.metric("Completed", completed_tasks)
        col4.metric("Blocked", blocked_tasks)

        st.divider()

        left, right = st.columns(2)

        with left:
            st.markdown("#### Task Status")

            status_counts = {
                "Ready": sum(
                    task.get("execution_status") == "ready"
                    for task in tasks
                ),
                "In progress": in_progress_tasks,
                "Blocked": blocked_tasks,
                "Completed": completed_tasks,
            }

            st.bar_chart(status_counts)

        with right:
            st.markdown("#### Task Priority")

            priority_counts = {
                priority.title(): sum(
                    task.get("priority") == priority
                    for task in tasks
                )
                for priority in ["urgent", "high", "medium", "low", "unknown"]
            }

            st.bar_chart(priority_counts)

        st.divider()
        st.markdown("#### Recent Documents")

        if documents:
            for document in documents[:5]:
                with st.container(border=True):
                    st.write(f"**{document.get('filename', 'Unnamed document')}**")
                    st.caption(
                        f"Document ID: {document.get('id', 'N/A')} "
                        f"| Status: {document.get('status', 'N/A')}"
                    )
                    summary = get_summary_text(document)
                    if summary:
                        st.write(summary[:300])
        else:
            st.info("No documents found. Upload a document to get started.")

    except Exception as exc:
        show_error(exc)


# ---------------------------------------------------------
# Upload and background job tracking
# ---------------------------------------------------------

with upload_tab:
    st.subheader("Upload a Work Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"],
        help="Maximum file size: 10 MB",
    )

    if uploaded_file:
        st.write(f"Selected file: **{uploaded_file.name}**")
        st.caption(f"Size: {uploaded_file.size / 1024:.2f} KB")

        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File exceeds the 10 MB limit.")
        elif uploaded_file.size == 0:
            st.error("The selected file is empty.")
        elif st.button("Process Document", type="primary"):
            try:
                with st.spinner("Submitting document..."):
                    result = api_request(
                        "POST",
                        "/documents/submit",
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type or "application/octet-stream",
                            )
                        },
                        timeout=60,
                    )

                job_id = result.get("job_id")
                st.session_state.last_job_id = job_id

                st.success("Document submitted successfully.")
                st.write(f"**Job ID:** `{job_id}`")
                st.write(f"**Status:** {result.get('status', 'pending')}")

            except Exception as exc:
                show_error(exc)

    st.divider()
    st.markdown("#### Background Job Status")

    job_id_input = st.text_input(
        "Job ID",
        value=str(st.session_state.last_job_id or ""),
        placeholder="Enter the job ID returned after upload",
    )

    if st.button("Refresh Job Status"):
        if not job_id_input.strip():
            st.warning("Enter a job ID first.")
        else:
            try:
                job = api_request(
                    "GET",
                    f"/jobs/{job_id_input.strip()}",
                    timeout=15,
                )

                status = job.get("status", "unknown")

                if status == "completed":
                    st.success("Document processing completed.")
                elif status == "failed":
                    st.error("Document processing failed.")
                elif status == "processing":
                    st.info("Document is currently processing.")
                else:
                    st.info(f"Current job status: {status}")

                st.json(job)

            except Exception as exc:
                show_error(exc)


# ---------------------------------------------------------
# Documents
# ---------------------------------------------------------

with documents_tab:
    st.subheader("Processed Documents")

    if st.button("Refresh Documents"):
        st.rerun()

    try:
        documents = api_request("GET", "/documents/", timeout=20)
        documents = documents if isinstance(documents, list) else []

        if not documents:
            st.info("No documents have been processed yet.")
        else:
            for document in documents:
                document_id = document.get("id")

                with st.expander(
                    f"{document.get('filename', 'Document')} "
                    f"(ID: {document_id})"
                ):
                    st.write(f"**File type:** {document.get('file_type', 'N/A')}")
                    st.write(f"**Status:** {document.get('status', 'N/A')}")
                    st.write(f"**Created:** {document.get('created_at', 'N/A')}")

                    summary = get_summary_text(document)

                    st.markdown("**Summary**")
                    st.write(summary or "No summary available.")

                    if isinstance(document.get("summary"), dict):
                        key_points = document["summary"].get("key_points", [])

                        if key_points:
                            st.markdown("**Key Points**")
                            for point in key_points:
                                st.write(f"- {point}")

                    if document_id is not None:
                        if st.button(
                            "View document details",
                            key=f"document_{document_id}",
                        ):
                            try:
                                details = api_request(
                                    "GET",
                                    f"/documents/{document_id}",
                                    timeout=20,
                                )
                                st.json(details)
                            except Exception as exc:
                                show_error(exc)

    except Exception as exc:
        show_error(exc)


# ---------------------------------------------------------
# Task management
# ---------------------------------------------------------

with tasks_tab:
    st.subheader("Task Management")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        priority_filter = st.selectbox(
            "Priority",
            ["All", "urgent", "high", "medium", "low", "unknown"],
        )

    with filter_col2:
        status_filter = st.selectbox(
            "Execution Status",
            ["All", "ready", "in_progress", "blocked", "completed"],
        )

    with filter_col3:
        if st.button("Refresh Tasks", use_container_width=True):
            st.rerun()

    params = {}

    if priority_filter != "All":
        params["priority"] = priority_filter

    if status_filter != "All":
        params["execution_status"] = status_filter

    try:
        tasks = api_request(
            "GET",
            "/tasks/",
            params=params,
            timeout=20,
        )
        tasks = tasks if isinstance(tasks, list) else []

        st.caption(f"{len(tasks)} task(s) found")

        if not tasks:
            st.info("No tasks match the selected filters.")

        for task in tasks:
            task_id = task.get("id")

            with st.expander(
                f"Task #{task_id} — {task.get('description', 'No description')[:90]}"
            ):
                st.write(f"**Description:** {task.get('description', '')}")
                st.write(f"**Document ID:** {task.get('document_id', 'N/A')}")
                st.write(f"**Assignee:** {task.get('assignee') or 'Unassigned'}")
                st.write(f"**Deadline:** {task.get('deadline') or 'Not specified'}")
                st.write(f"**Priority:** {task.get('priority', 'unknown')}")
                st.write(
                    f"**Execution status:** "
                    f"{task.get('execution_status', 'unknown')}"
                )

                dependencies = task.get("dependencies") or []

                st.write(
                    "**Dependencies:** "
                    + (", ".join(dependencies) if dependencies else "None")
                )

                st.divider()
                st.markdown("**Edit Task**")

                with st.form(key=f"edit_task_{task_id}"):
                    new_assignee = st.text_input(
                        "Assignee",
                        value=task.get("assignee") or "",
                    )

                    new_deadline = st.text_input(
                        "Deadline",
                        value=task.get("deadline") or "",
                        help="Use YYYY-MM-DD if possible.",
                    )

                    priority_options = [
                        "urgent", "high", "medium", "low", "unknown"
                    ]
                    current_priority = task.get("priority", "unknown")
                    priority_index = (
                        priority_options.index(current_priority)
                        if current_priority in priority_options
                        else priority_options.index("unknown")
                    )

                    new_priority = st.selectbox(
                        "Priority",
                        priority_options,
                        index=priority_index,
                    )

                    status_options = [
                        "ready", "in_progress", "blocked", "completed"
                    ]
                    current_status = task.get("execution_status", "ready")
                    status_index = (
                        status_options.index(current_status)
                        if current_status in status_options
                        else 0
                    )

                    new_status = st.selectbox(
                        "Execution Status",
                        status_options,
                        index=status_index,
                    )

                    save_task = st.form_submit_button(
                        "Save Changes",
                        type="primary",
                    )

                if save_task:
                    updates = {
                        "assignee": new_assignee.strip() or None,
                        "deadline": new_deadline.strip() or None,
                        "priority": new_priority,
                        "execution_status": new_status,
                    }

                    try:
                        api_request(
                            "PATCH",
                            f"/tasks/{task_id}",
                            json=updates,
                            timeout=20,
                        )
                        st.success("Task updated successfully.")
                        st.rerun()
                    except Exception as exc:
                        show_error(exc)

                if st.button(
                    "Delete Task",
                    key=f"delete_task_{task_id}",
                    type="secondary",
                ):
                    try:
                        api_request(
                            "DELETE",
                            f"/tasks/{task_id}",
                            timeout=20,
                        )
                        st.success(f"Task #{task_id} deleted.")
                        st.rerun()
                    except Exception as exc:
                        show_error(exc)

    except Exception as exc:
        show_error(exc)