# api.py
"""
FastAPI application for the multi-agent customer support and knowledge system.

This module provides a REST API endpoint for processing customer queries through
an intelligent workflow that routes queries to appropriate agents and returns
personalized responses.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from workflow import IntelligentQueryResolver as Workflow
from knowledge_agent import knowledge_base
from models import FinalResponseOutput
from agno.storage.json import JsonStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    """Request model for chat queries."""

    message: str = Field(
        ..., min_length=1, max_length=1000, description="User query message"
    )
    user_id: str = Field(
        ..., min_length=1, max_length=100, description="Unique user identifier"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str = Field(None, description="Additional error details")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting multi-agent workflow API...")
    yield
    logger.info("Shutting down multi-agent workflow API...")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="Multi-Agent Customer Support API",
    description="Intelligent query resolution system using multiple AI agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_workflow() -> Workflow:
    """
    Dependency to create and return a workflow instance.

    Returns:
        Workflow: Configured workflow instance with JSON storage

    Raises:
        HTTPException: If workflow initialization fails
    """
    try:
        return Workflow(storage=JsonStorage("tmp/workflow_data.json"))
    except Exception as e:
        logger.error(f"Failed to initialize workflow: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to initialize workflow system"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
        },
    )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "multi-agent-api"}


@app.post(
    "/chat",
    response_model=FinalResponseOutput,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def send_query_to_agent(
    request: QueryRequest, workflow: Workflow = Depends(get_workflow)
) -> FinalResponseOutput:
    """
    Process a customer query through the multi-agent workflow.

    Args:
        request: The query request containing message and user_id
        workflow: Injected workflow dependency

    Returns:
        FinalResponseOutput: The processed response from the agent workflow

    Raises:
        HTTPException: For various error conditions (400, 500)
    """
    try:
        logger.info(
            f"Processing query for user {request.user_id}: {request.message[:50]}..."
        )
        # load the knowledge base
        # _ = await knowledge_base.aload(recreate=True)

        # Execute the workflow
        response = workflow.run(query=request.message)

        if not response or not response.content:
            logger.error("Workflow returned empty response")
            raise HTTPException(
                status_code=500, detail="Workflow failed to generate response"
            )

        logger.info(f"Successfully processed query for user {request.user_id}")
        return response.content

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to process query: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
