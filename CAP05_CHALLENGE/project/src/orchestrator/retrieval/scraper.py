from abc import ABC, abstractmethod
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from util import logger


class Scraper(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> dict[str, Any]:
        pass

    async def parse(self, body):
        """Parses all the text from the html."""

        soup = BeautifulSoup(body, "html.parser")
        raw_text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\n{3,}|\s{2,}", "\n", raw_text)
        return text


class ScraperRemote(Scraper):
    def __init__(self, host: str = "http://lb-scraper/scrape/?url=") -> None:
        self.host = host

    async def fetch(self, url: str) -> dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            query_url = self.host + url
            async with session.post(query_url) as response:
                if response.status == 200:
                    body = await response.json()
                    text = await self.parse(body["html"])
                    if text:
                        return {"url": url, "text": text}
            return {"url": url, "text": None}


class ScraperLocal(Scraper):
    async def fetch(self, url):
        try:
            # Configurar cliente con límites más grandes para encabezados y mayor timeout
            timeout = aiohttp.ClientTimeout(total=10)  # Reducir el timeout para evitar demoras excesivas
            
            # Opciones para manejar encabezados grandes
            conn = aiohttp.TCPConnector(force_close=True)
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
            
            async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
                try:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            html = await response.text()
                            text = await self.parse(html)
                            return {"url": url, "text": text}
                except aiohttp.ClientResponseError as e:
                    logger.warning(f"Error en respuesta al acceder a {url}: {str(e)}")
                except aiohttp.ClientConnectorError as e:
                    logger.warning(f"Error de conexión al acceder a {url}: {str(e)}")
                except aiohttp.ClientPayloadError as e:
                    logger.warning(f"Error de payload al acceder a {url}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Error desconocido al acceder a {url}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error general al procesar {url}: {str(e)}")
        
        # Si llegamos aquí es porque hubo algún error
        return {"url": url, "text": f"No se pudo acceder a {url}"}
