from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import WorkflowRequest, WorkflowResponse
from app.agent.executor import execute_workflow


app = FastAPI(
    title="Agentic Workflow Automation Engine",
    description="AI-powered workflow automation engine for decomposing business processes into executable tool-based tasks.",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only. Later we will restrict this to React frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Agentic Workflow Automation Engine API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "version": "0.1.0"
    }


@app.post("/api/workflows/run", response_model=WorkflowResponse)
def run_workflow(request: WorkflowRequest):
    result = execute_workflow(request.process_description)
    return result