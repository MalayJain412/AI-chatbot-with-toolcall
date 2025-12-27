from fastapi import FastAPI
from pydantic import BaseModel

from langchain_openai import AzureChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate

from tools import web_search, get_malay_info, send_email, save_email_details, save_meeting_details, schedule_meeting
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

class ChatRequest(BaseModel):
    message: str

# ---------------------------------------------------------
# System Prompt
# ---------------------------------------------------------
SYSTEM_PROMPT = """
You are a helpful AI assistant.

You have access to tools.
Use a tool when it will improve your answer.
Never mention the tool names to the user.

Guidelines:
- Prefer get_malay_info for questions about Malay, Malay Jain or related entity if the result is not found then go for websearch
- Use web_search only for general web questions
- Be concise and clear
- Summarize tool results in natural language

When a user asks you to send an email:

When user asks to send an email:
1. First call save_email_details with the full user request text
2. Then call send_email to actually send it
3. Confirm success politely
4. Do not mention tool names

If no tool is needed, answer directly.
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
tools = [web_search, get_malay_info, send_email, save_email_details, save_meeting_details, schedule_meeting]
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