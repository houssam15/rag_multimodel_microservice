import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.environ["OPEN_AI_API_KEY"],
    temperature=0
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.environ["OPEN_AI_API_KEY"]
)