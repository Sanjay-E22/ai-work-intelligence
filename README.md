# AI Work Intelligence Platform

An AI-powered document intelligence and task management application that converts unstructured work documents into actionable tasks, summaries, priorities, and dependency-aware execution statuses.

Built with **Python, FastAPI, Streamlit, MySQL, SQLAlchemy, and Ollama**.

## Overview

Teams often receive project requirements, meeting notes, reports, and work instructions in PDF or text files. Extracting actionable work from these documents manually takes time and makes task tracking difficult.

The AI Work Intelligence Platform automates this process.

Users upload a PDF or TXT document. The application extracts its content, generates a summary, identifies tasks, calculates task priorities, evaluates dependencies, and stores the results in MySQL. Users can then manage the extracted tasks through a Streamlit dashboard.

## Features

### Document intelligence
- Upload PDF and TXT documents.
- Extract text from uploaded files.
- Generate AI-powered document summaries.
- Extract actionable tasks from document content.
- Identify task descriptions, assignees, deadlines, and dependencies.

### Task management
- Automatically calculate task priority based on deadlines.
- Identify tasks blocked by incomplete dependencies.
- View extracted tasks.
- Filter tasks by priority and execution status.
- Update task assignees, deadlines, priorities, and statuses.
- Delete tasks.

### Background processing
- Submit documents for asynchronous processing using FastAPI BackgroundTasks.
- Track processing jobs.
- View job status and errors.

### Data persistence
- Store documents, jobs, and extracted tasks in MySQL.
- Use SQLAlchemy for database operations.
- Retrieve previously processed documents and tasks.

### Dashboard
- Streamlit dashboard for interacting with the application.
- Overview of documents and task statistics.
- Document upload and job tracking.
- Document summary viewing.
- Task filtering and management.

## Architecture

```mermaid
flowchart TD
    A[User] --> B[Streamlit Dashboard]
    B --> C[FastAPI REST API]
    C --> D[Document Processing]
    D --> E[PDF / TXT Parser]
    E --> F[AI Workflow]
    F --> G[Ollama LLM]
    F --> H[Task Extraction]
    H --> I[Priority Calculation]
    H --> J[Dependency Management]
    I --> K[MySQL Database]
    J --> K
    D --> K
    C --> L[Background Job Processing]
    L --> D
```

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.11 |
| Backend | FastAPI |
| Frontend | Streamlit |
| AI inference | Ollama |
| Language model | Mistral |
| Database | MySQL |
| ORM | SQLAlchemy |
| Data validation | Pydantic |
| PDF processing | PyMuPDF |
| API testing | FastAPI Swagger UI |
| Automated testing | Pytest |

## Project Structure

```text
ai-work-intelligence/
│
├── app/
│   ├── ai/
│   │   ├── agents/
│   │   │   ├── dependency_manager.py
│   │   │   ├── extractor.py
│   │   │   ├── prioritizer.py
│   │   │   └── summarizer.py
│   │   ├── ollama_client.py
│   │   └── workflow.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── documents.py
│   │       ├── jobs.py
│   │       └── tasks.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── db/
│   │   ├── models/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── workers/
│   └── main.py
│
├── frontend/
│   └── streamlit_app.py
│
├── tests/
│
├── storage/
├── create_tables.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
└── Docker configuration files (optional)
```

## Prerequisites

Install the following before running the application:

- Python 3.11
- MySQL 8 or compatible MySQL server
- Ollama
- Git

Pull the Mistral model:

```bash
ollama pull mistral
```

Make sure Ollama is running before starting the backend.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sanjay-E22/ai-work-intelligence.git
cd ai-work-intelligence
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Configure your MySQL connection and Ollama settings.

Example:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/ai_work_intelligence
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

Use your own database username, password, and database name. Never commit your actual `.env` file.

### 5. Create database tables

```bash
python create_tables.py
```

Ensure the configured MySQL database exists and the connection works.

## Running the Application

Start the FastAPI backend:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

In a second terminal, activate the same virtual environment and start Streamlit:

```bash
streamlit run frontend/streamlit_app.py
```

Dashboard:

```text
http://localhost:8501
```

## API Endpoints

The main API routes include:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/documents/process` | Process a document synchronously |
| POST | `/documents/submit` | Submit a document for background processing |
| GET | `/documents/` | Retrieve documents |
| GET | `/documents/{document_id}` | Retrieve a document |
| GET | `/jobs/{job_id}` | Check background job status |
| GET | `/tasks/` | Retrieve and filter tasks |
| GET | `/tasks/{task_id}` | Retrieve a task |
| PATCH | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

For request parameters, response schemas, and interactive testing, open `/docs` while the backend is running.

## Background Processing

The application uses FastAPI BackgroundTasks to process submitted documents without making the upload request wait for the full AI workflow.

The processing flow is:

1. Receive and validate the uploaded file.
2. Create a background job record.
3. Store the file temporarily.
4. Process the document through the AI workflow.
5. Save the document and extracted tasks.
6. Update the job status to completed or failed.
7. Remove the temporary upload file.

**Note:** FastAPI BackgroundTasks is suitable for this prototype, but it is not a durable distributed job queue. A production deployment handling critical workloads should use a persistent worker system.

## Running Tests

Run all tests from the project root:

```bash
pytest -v
```

Run a specific test module:

```bash
pytest tests/test_task_normalizer.py -v
```

## Configuration and Security

- Keep credentials in local environment variables.
- Do not commit `.env` files.
- Do not upload private company documents or confidential business data.
- Configure appropriate file-size and file-type validation.
- Use a secure database password.
- Add authentication and authorization before exposing the application publicly.

## Current Limitations

- Background jobs are processed within the FastAPI application process.
- Ollama must be available to perform AI inference.
- AI-extracted tasks and dates may require human review.
- Authentication and role-based access control are not yet implemented.
- Docker deployment is planned but not yet part of the verified local setup.

## Future Improvements

- Durable background job processing.
- Authentication and role-based access control.
- Improved task dependency resolution.
- More robust deadline extraction and validation.
- Production deployment with Docker.
- Cloud-based deployment.
- Improved monitoring and observability.

## Author

**Sanjay Elangovan**

- GitHub: https://github.com/Sanjay-E22
- LinkedIn: https://linkedin.com/in/sanjay-e-76a89a271

---
<img width="941" height="458" alt="image" src="https://github.com/user-attachments/assets/6b015514-ed57-458a-86f1-bafc356cc06a" />

<img width="938" height="457" alt="image" src="https://github.com/user-attachments/assets/4ade810f-7f8f-43ec-aa1e-93d523bc4a05" />

<img width="912" height="457" alt="image" src="https://github.com/user-attachments/assets/39d03b78-54ae-4e53-90fa-e9546a20a304" />

<img width="909" height="450" alt="image" src="https://github.com/user-attachments/assets/812a82d6-0efc-448a-abdc-43ac3e5c06cb" />


*An AI-powered application for transforming work documents into structured, actionable intelligence.*
