import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import RateLimitError

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ["OPEN_AI_API_KEY"],
    temperature=0,
    max_tokens=200
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.environ["OPEN_AI_API_KEY"]
)

SEM = asyncio.Semaphore(2)

async def safe_llm_call(messages):
    async with SEM:
        while True:
            try:
                return await llm.ainvoke(messages)
            except RateLimitError:
                await asyncio.sleep(1)
