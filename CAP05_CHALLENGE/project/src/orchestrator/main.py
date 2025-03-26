from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from sse_starlette.sse import EventSourceResponse
from util import logger
from fastapi.middleware.cors import CORSMiddleware
import asyncio

import prompt
import openai
from retrieval import Retriever
from retrieval.search import GoogleAPI
from retrieval.cache import RedisVectorCache
from retrieval.scraper import ScraperLocal, ScraperRemote
from retrieval.embeddings import OpenAIEmbeddings, RemoteEmbeddings
from retrieval.splitter import LangChainSplitter

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def stream_chat(prompt: str):
    try:
        for chunk in openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")  # type: ignore
            if content is not None:
                yield content
    except Exception as e:
        logger.error(f"Error in stream_chat: {e}")
        yield f"[Error: {str(e)}]"


async def event_generator(query) -> AsyncGenerator[dict, None]:
    try:
        redis = RedisVectorCache(host="cache", port=6379)
        embeddings = OpenAIEmbeddings()
        google = GoogleAPI()
        scraper = ScraperLocal()
        splitter = LangChainSplitter(chunk_size=400, chunk_overlap=50, length_function=len)

        try:
            redis.init_index(vector_dimension=embeddings.vector_dimension)
            logger.info(f"Created index with vector dimensions {embeddings.vector_dimension}")
        except Exception as e:
            logger.info(f"Index already exists: {e}")

        retriever = Retriever(
            cache=redis,
            searcher=google,
            scraper=scraper,
            embeddings=embeddings,
            splitter=splitter,
        )
        
        async for event in retriever.get_context(query=query, cache_treshold=0.85, k=10):
            yield event
            if event["event"] == "context":
                final_prompt = prompt.rag.format(context=event["data"], question=query)

                yield {"event": "prompt", "data": final_prompt}

                for text in stream_chat(prompt=final_prompt):
                    yield {"event": "token", "data": text}
    except Exception as e:
        logger.error(f"Error in event_generator: {str(e)}")
        yield {"event": "error", "data": f"Backend error: {str(e)}"}


@app.get("/streamingSearch")
async def main(query: str) -> EventSourceResponse:
    # Eliminados los parámetros ping_interval y retry_timeout porque la versión instalada
    # de sse_starlette no los soporta
    return EventSourceResponse(event_generator(query))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
