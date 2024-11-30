import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.funnel_agent import FunnelAgent
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Funnel1",
    description="AI agent chatbot for blockchain interactions and Twitter integration",
    version="1.0.0"
)

# Initialize agent
agent = FunnelAgent()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    actions: list

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and execute any required actions
    """
    try:
        logger.info(f"Received message: {request.message}")
        response, actions = await agent.process_message(request.message)
        logger.info(f"Actions executed: {actions}")
        return ChatResponse(response=response, actions=actions)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)