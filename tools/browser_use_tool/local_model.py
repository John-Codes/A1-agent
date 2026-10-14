from browser_use import ChatOllama
from ollama import AsyncClient


class NonThinkingClient(AsyncClient):
    async def chat(self, *args, **kwargs):
        kwargs.setdefault("think", False)
        return await super().chat(*args, **kwargs)


class BrowserChatOllama(ChatOllama):
    def get_client(self):
        return NonThinkingClient(host=self.host, timeout=self.timeout, **(self.client_params or {}))
