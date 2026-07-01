from agents.candidate_agent import CandidateAgent
from agents.job_agent import JobAgent
from agents.document_agent import DocumentAgent
from fastapi import FastAPI
from mcp import Context


def main():
    print("Hello from recruitment-ai-system!")

    # Initialize agents
    candidate_agent = CandidateAgent()
    job_agent = JobAgent()
    document_agent = DocumentAgent()

    # Add data
    candidate_agent.add_candidate("candidate_1", {"name": "John Doe", "skills": ["Python", "AI"]})
    job_agent.add_job("job_1", {"title": "AI Engineer", "description": "Develop AI models."})

    # Share context
    document_agent.set_context("candidate_1", candidate_agent.get_candidate("candidate_1"))
    document_agent.set_context("job_1", job_agent.get_job("job_1"))

    # Execute tasks
    candidate_agent.execute()
    job_agent.execute()
    document_agent.execute()


# Initialize FastAPI app
app = FastAPI()

# Initialize MCP context
agent_context = Context()

# Add initial agents to the context
agent_context['candidate_agent'] = {
    'name': 'Candidate Agent',
    'status': 'idle',
    'tasks': []
}
agent_context['job_agent'] = {
    'name': 'Job Agent',
    'status': 'idle',
    'tasks': []
}

# Define FastAPI endpoints
@app.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    agent = agent_context.get(agent_id)
    if agent:
        return {"agent_id": agent_id, "data": agent}
    return {"error": "Agent not found"}

@app.post("/agents/{agent_id}/task")
def assign_task(agent_id: str, task: str):
    agent = agent_context.get(agent_id)
    if agent:
        agent['tasks'].append(task)
        agent['status'] = 'busy'
        return {"message": f"Task '{task}' assigned to {agent['name']}"}
    return {"error": "Agent not found"}

@app.put("/agents/{agent_id}/status")
def update_status(agent_id: str, status: str):
    agent = agent_context.get(agent_id)
    if agent:
        agent['status'] = status
        return {"message": f"Status of {agent['name']} updated to '{status}'"}
    return {"error": "Agent not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    main()
