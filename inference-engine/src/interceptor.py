import os
import asyncio
import json
from dotenv import load_dotenv
from cerebras.cloud.sdk import AsyncCerebras

class ThreatDetectedException(Exception):
    pass

class StreamInterceptor:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("CEREBRAS_API_KEY", "mock_key")
        self.client = AsyncCerebras(api_key=api_key)

    async def analyze_stream(self, prompt: str):
        schema = {
            "type": "object",
            "properties": {
                "threat_level": {"type": "string", "enum": ["SAFE", "SUSPICIOUS", "CRITICAL"]},
                "reasoning": {"type": "string"}
            },
            "required": ["threat_level", "reasoning"],
            "additionalProperties": False
        }
        
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Analyze the input and determine the threat level."},
                {"role": "user", "content": prompt}
            ],
            model="llama3.1-8b",
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
