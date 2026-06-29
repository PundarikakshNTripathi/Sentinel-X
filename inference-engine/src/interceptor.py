"""
StreamInterceptor handles the speculative early-exit logic by streaming responses
from the Cerebras Inference API. By enforcing a strict JSON schema and reading SSE chunks,
we can break the connection and immediately raise a threat the millisecond the "CRITICAL"
token is generated, vastly reducing TTFT (Time-To-First-Token) latency.
"""
import os
import asyncio
from dotenv import load_dotenv
from cerebras.cloud.sdk import AsyncCerebras

class ThreatDetectedException(Exception):
    pass

class StreamInterceptor:
    def __init__(self):
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(dotenv_path=env_path)
        api_key = os.getenv("CEREBRAS_API_KEY")
        self.client = AsyncCerebras(api_key=api_key)

    async def analyze_stream(self, base64_image: str, dom_content: str = ""):
        schema = {
            "type": "object",
            "properties": {
                "threat_level": {"type": "string", "enum": ["SAFE", "SUSPICIOUS", "CRITICAL"]},
                "reasoning": {"type": "string"}
            },
            "required": ["threat_level", "reasoning"],
            "additionalProperties": False
        }
        
        # Truncate DOM to prevent token overflow while preserving structure
        truncated_dom = dom_content[:2000] if dom_content else "No DOM provided."
        
        prompt = [
            {"type": "text", "text": f"Analyze this frame delta and its underlying HTML DOM structure. If you see phishing markers like malicious external endpoints or clone discrepancies, flag it as CRITICAL. HTML DOM Context: {truncated_dom}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
        
        response = await self.client.chat.completions.create(
            model="gemma-4-31b",
            messages=[
                {"role": "system", "content": "Analyze the input and determine the threat level."},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ThreatAnalysis",
                    "schema": schema,
                    "strict": True
                }
            }
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                if "CRITICAL" in content:
                    raise ThreatDetectedException("Threat detected in stream!")
        
        return "SAFE"