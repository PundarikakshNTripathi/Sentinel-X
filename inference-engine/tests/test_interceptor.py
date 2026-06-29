import pytest
import asyncio
from src.interceptor import StreamInterceptor, ThreatDetectedException

class MockDelta:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.delta = MockDelta(content)

class MockChunk:
    def __init__(self, content):
        self.choices = [MockChoice(content)] if content is not None else []

class MockAsyncResponse:
    def __init__(self, chunks):
        self.chunks = chunks
    
    async def __aiter__(self):
        for chunk in self.chunks:
            yield chunk

class MockCompletions:
    async def create(self, **kwargs):
        prompt = kwargs['messages'][1]['content']
        if "bad" in prompt:
            return MockAsyncResponse([
                MockChunk('{"threat_level": "'),
                MockChunk('CRITICAL'),
                MockChunk('", "reasoning": "bad"}')
            ])
        else:
            return MockAsyncResponse([
                MockChunk('{"threat_level": "SAFE", "reasoning": "ok"}')
            ])

class MockChat:
    def __init__(self):
        self.completions = MockCompletions()

class MockClient:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.chat = MockChat()

@pytest.fixture
def mock_cerebras(monkeypatch):
    import src.interceptor
    monkeypatch.setattr(src.interceptor, "AsyncCerebras", MockClient)

@pytest.mark.asyncio
async def test_analyze_stream_safe(mock_cerebras):
    interceptor = StreamInterceptor()
    result = await interceptor.analyze_stream("good prompt")
    assert result == "SAFE"

@pytest.mark.asyncio
async def test_analyze_stream_critical(mock_cerebras):
    interceptor = StreamInterceptor()
    with pytest.raises(ThreatDetectedException, match="Threat detected in stream!"):
        await interceptor.analyze_stream("bad prompt")
