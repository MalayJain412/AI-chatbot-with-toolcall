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
)
import config
import logging

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
SYSTEM_PROMPT = """
You are a helpful AI assistant.

You have access to tools.
Use a tool only when it is clearly needed.
Never mention tool names to the user.

------------------------------------------------
EMAIL RULES
------------------------------------------------
When a user asks you to send an email:

1️⃣ First call save_email_details  
   - Always pass the ENTIRE USER REQUEST TEXT

2️⃣ Then call send_email  
   - Only AFTER email details are saved

3️⃣ Confirm success politely (do not mention tools)


------------------------------------------------
MEETING RULES
------------------------------------------------
A meeting involves phrases like:
- book a meeting
- schedule a meeting
- arrange a call
- calendar event
- set up a meeting
- setup call
- schedule discussion

There are TWO steps:

--------------------------------
STEP 1 — CREATE MEETING DRAFT
--------------------------------
When the user provides meeting details,
CALL: save_meeting_details

Pass JSON **AS A STRING** in this format:

{
  "topic": "Topic name",
  "date": "YYYY-MM-DD",
  "start_time": "HH:MM",
  "end_time": "HH:MM",
  "timezone": "", By default, always set timezone to "IST" unless the user explicitly specifies another timezone.
  "attendees": ["email@example.com"]
}

Rules:
✔ date MUST be YYYY-MM-DD  
✔ time MUST be 24-hour HH:MM  
✔ attendees optional  
By default, always set timezone to "IST" unless the user explicitly specifies another timezone.



--------------------------------
STEP 2 — CONFIRM BEFORE SCHEDULING
--------------------------------
Only schedule the meeting when the user says:

- "confirm meeting"
- "yes confirm"
- "go ahead"
- "book it"
- "schedule now"
- "confirm"

THEN call:
schedule_meeting

⚠️ DO NOT CALL schedule_meeting unless:
- a draft already exists
- user clearly confirmed
After scheduling the meeting call a send_email tool to notify the attendees.
--------------------------------
OTHER RULES
--------------------------------
If user only asks a question → answer normally.
If request is ambiguous → ask a follow-up question.
Do NOT guess missing details.
Do NOT expose internal tool names.
"""


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
    schedule_meeting_tool
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