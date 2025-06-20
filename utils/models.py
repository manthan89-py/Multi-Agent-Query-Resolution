# utils/models.py
"""
Pydantic models for the multi-agent workflow system.

This module defines the data structures used throughout the workflow,
including agent responses, workflow tracking, and final outputs.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class AgentWorkflow(BaseModel):
    """
    Represents the workflow details for an agent, including its name
    and the tools it has invoked during task execution.
    """

    agent_name: str = Field(
        description="The unique identifier or name of the agent involved in the workflow.",
    )
    tool_calls: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "A dictionary representing all tool invocations made by the agent. "
            "Each key corresponds to the tool name or identifier, and the value "
            "contains the specific parameters or metadata used during the call."
        ),
    )

    @field_validator("agent_name")
    def validate_agent_name(cls, v):
        """Validate agent name is not empty after stripping."""
        if not v.strip():
            raise ValueError("Agent name cannot be empty")
        return v.strip()


class AgentResponseOutput(BaseModel):
    """
    Captures the output of an individual agent including the textual response
    and the corresponding workflow that generated it.
    """

    response: str = Field(
        description="The generated response or message from the agent.",
    )
    agent_workflow: AgentWorkflow = Field(
        description="The detailed workflow, including tool usage, that led to this response.",
    )

    @field_validator("response")
    def validate_response(cls, v):
        """Validate response is not empty after stripping."""
        if not v.strip():
            raise ValueError("Response cannot be empty")
        return v.strip()


class FinalResponseOutput(BaseModel):
    """
    Aggregates a team-level response, typically involving orchestration across multiple agents.
    """

    response: str = Field(
        description="The collective or final response from the team of agents.",
    )
    source_agent_response: str = Field(
        description="The raw response generated by the originating agent within the workflow.",
    )
    agent_workflow: AgentWorkflow = Field(
        ...,
        description="The originating agent's workflow including its name and tool calls.",
    )

    @field_validator("response", "source_agent_response")
    def validate_responses(cls, v):
        """Validate responses are not empty after stripping."""
        if not v.strip():
            raise ValueError("Response fields cannot be empty")
        return v.strip()


class PersonalityLayerResponse(BaseModel):
    """
    Represents the final response from the personality layer agent,
    which adds the final conversational touch to the workflow output.
    """

    response: str = Field(
        description="The final output from the personality AI agent with conversational tone.",
    )

    @field_validator("response")
    def validate_response(cls, v):
        """Validate response is not empty after stripping."""
        if not v.strip():
            raise ValueError("Personality response cannot be empty")
        return v.strip()


class QueryRequest(BaseModel):
    """Request model for chat queries."""

    message: str = Field(description="User query message")
    user_id: str = Field(description="Unique user identifier")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str = Field(None, description="Additional error details")
