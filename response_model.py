from pydantic import BaseModel, Field


class AgentWorkflow(BaseModel):
    agent_name: str = Field(description="Name of the agent")
    tool_calls: dict = Field(description="Tool calls for the agent")


class ResponseOutput(BaseModel):
    reponse: str = Field(description="Response from the agent")
    source_agent_response: str = Field(description="Response from the source agent")
    agent_workflow: AgentWorkflow = Field(description="Agent workflow")
