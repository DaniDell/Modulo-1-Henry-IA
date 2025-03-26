import asyncio 
from abc import ABC, abstractmethod
import json
import aiohttp
from retrieval.cache import VECTOR_DIMENSION

import openai


class Embeddings(ABC):
    """Abstraction of embeddings client."""

    @abstractmethod
    async def run(self, chunks: list[str]) -> list[list[float]]:
        pass


class RemoteEmbeddings(Embeddings):
    """Instanciates a client that implements _embeddings service."""

    vector_dimension = 384

    async def run(self, chunks: list[str]) -> list[list[float]]:
        url = f"http://embeddings/encode"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"text": chunks})
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    r = await response.json()
                    return r["embedding"]
        return [[]]


class OpenAIEmbeddings(Embeddings):
    """OpenAI embeddings client wrapper"""

    vector_dimension = VECTOR_DIMENSION

    async def run(
        self, chunks: list[str], model="text-embedding-ada-002"
    ) -> list[list[float]]:
        # Ejecutar la llamada síncrona en un hilo separado
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: openai.Embedding.create(input=chunks, model=model)
        )
        vectors = map(lambda x: x["embedding"], response["data"])  # type: ignore
        return list(vectors)
