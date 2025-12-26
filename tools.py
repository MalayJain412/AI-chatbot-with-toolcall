from langchain.tools import tool
import requests
import logging

logger = logging.getLogger(__name__)

@tool
def web_search(query: str) -> str:
    """General web search. 
    DO NOT use this tool for Malay or Malay Jain related questions 
    unless get_malay_info fails.
    """
    logger.info(f"Performing web search for query: {query}")
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        logger.info(f"Making request to URL: {url}")
        res = requests.get(url, timeout=10)
        logger.info(f"Received response with status code: {res.status_code}")
        result = res.text
        logger.info(f"Search completed successfully, result length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        return f"Search failed: {str(e)}"

@tool
def get_malay_info(dummy: str) ->str:
    """USE THIS TOOL FIRST when the user asks about Malay or Malay Jain.
    This tool returns the official verified profile.
    Do NOT use web_search for Malay Jain unless this tool returns nothing.
    The input is ignored.
    """
    logger.info("Retrieving Malay information from malay.txt")
    try:
        with open("malay.txt", "r", encoding = "utf-8") as file:
            content = file.read()
            logger.info(f"Successfully read malay.txt, content length: {len(content)}")
            return content
    except Exception as e:
        logger.error(f"Failed to read malay.txt: {str(e)}")
        return f"Malay info not available: {str(e)}"

from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)


@tool
def get_user_email_id(query: str) -> str:
    """Use this tool when the user asks for the email / mail id of a user.
    Supported users:
    - Malay Jain / Malay
    - Aniket / Aniket Kumar / Aniket Mishra / Aniket Kumar Mishra

    Return ONLY the email address string, nothing else.
    """

    logger.info(f"Resolving email from query: {query}")

    q = query.lower()

    if "malay" in q:
        return "malayjain1234@gmail.com"

    if "aniket" in q:
        return "anni990@gmail.com"

    return "Email not found"
