# api.py


### Create FastAPI app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from workflow import IntelligentQueryResolver as Workflow
from models import FinalResponseOutput
from agno.storage.json import JsonStorage
import uvicorn


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=FinalResponseOutput)
def send_query_to_agent(message: str, user_id: str):
    # Send the query to the agent workflow
    workflow = Workflow(storage=JsonStorage("tmp/workflow_data.json"))
    response = workflow.run(query=message)
    response_dict = response.content
    return response_dict


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
