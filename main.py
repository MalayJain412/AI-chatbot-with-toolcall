from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_openai import AzureChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate

from tools import (
    web_search,
    get_malay_info,
    send_email,
    save_email_details,
    save_meeting_tool,
    schedule_meeting_tool,
    get_google_sheet_tool
)
import config
import logging

from system_prompt import system_prompt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------
app = FastAPI()
logger.info("FastAPI app initialized")

# ------------------------- NEW -------------------------------------
# Allow all origins (any host/port) — for development only
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # or ["POST", "OPTIONS"]
    allow_headers=["*"],
)
# ------------------------- NEW -------------------------------------
class ChatRequest(BaseModel):
    message: str

# ---------------------------------------------------------
# System Prompt
# ---------------------------------------------------------
SYSTEM_PROMPT = system_prompt

prompt = ChatPromptTemplate.from_messages([
    ("system",SYSTEM_PROMPT),
    ("human","{input}")
])


# ---------------------------------------------------------
# AzureOpenAI LLm
# ---------------------------------------------------------
logger.info("Initializing Azure OpenAI LLM")
llm = AzureChatOpenAI(
    openai_api_version = config.AZURE_API_VERSION,
    azure_deployment = config.AZURE_DEPLOYMENT,
    azure_endpoint = config.AZURE_OPENAI_ENDPOINT,
    api_key = config.AZURE_OPENAI_API_KEY,
    temperature = 0.8
)
logger.info("LLM initialized successfully")


# ---------------------------------------------------------
# Tools
# ---------------------------------------------------------
logger.info("Loading tools")
tools = [
    web_search,
    get_malay_info,
    send_email,
    save_email_details,
    save_meeting_tool,
    schedule_meeting_tool,
    get_google_sheet_tool
]
logger.info(f"Loaded {len(tools)} tools")

# ---------------------------------------------------------
# Memory
# ---------------------------------------------------------
logger.info("Initializing conversation memory")
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
logger.info("Memory initialized")

# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------
logger.info("Initializing LangChain agent")
agent = initialize_agent(
    tools = tools,
    llm = llm,
    agent = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose = True,
    memory = memory,
    handle_parsing_errors = True
)
logger.info("Agent initialized successfully")

# ---------------------------------------------------------
# Endpoint
# ---------------------------------------------------------
@app.post("/chat")
async def chat(req: ChatRequest):

    logger.info(f"Received chat request: {req.message}")

    logger.info("Initializing agent run...")
    response = agent.run(req.message)

    logger.info("Agent run completed successfully")
    logger.info(f"Response: {response}")

    return {"reply": response}