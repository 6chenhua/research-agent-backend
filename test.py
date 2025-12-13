from app.integrations.llm_client import LLMClient
import asyncio

llm = LLMClient()
res = asyncio.run(llm.chat([
    {"role": "user", "content": "hello"}
]))
print(res)