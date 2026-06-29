# Sentinel-X Demo Guide (60-Second Showcase)

This guide provides a structured 60-second script and methodology for demonstrating Sentinel-X's capabilities, fast Cerebras inference, and architectural impact without executing real malicious payloads.

## Preparation

1. **Extension Loading**: Ensure Sentinel-X is loaded in Chrome (`chrome://extensions/` -> Developer Mode -> Load Unpacked -> select the `client-extension` folder).
2. **Cloud Connectivity**: Confirm the extension is actively connected to the deployed Go Gateway on Render (the background worker console should read "Connected to Sentinel-X Gateway").
3. **Playground Hosting**: Serve the safe phishing replica locally.
   ```bash
   python -m http.server 8081
   ```

## Video Demo Script (60 Seconds)

**[0:00 - 0:10] The Problem & Methodology**
*Visual: Show a split screen of a generic browser and the Sentinel-X architecture diagram.*
"Traditional endpoint security relies on reactive blocklists or post-execution analysis. Sentinel-X introduces a zero-latency, multimodal late-fusion architecture to intercept zero-day threats pre-execution."

**[0:10 - 0:25] Tier 1 & Multimodal Edge Streaming**
*Visual: Open the local phishing playground in Chrome (`http://localhost:8081/tests/playground.html`). Open the Chrome Extension background console to show the WebSocket streaming base64 image data.*
"Our browser extension acts as the edge node. It calculates Shannon entropy via C++ WebAssembly for instant domain filtering. Simultaneously, it captures visual deltas and streams them through a highly concurrent Go TCP multiplexer to our FastAPI engine."

**[0:25 - 0:45] The Cerebras VLM Intercept (The Fast Inference)**
*Visual: Hover over the password field in the phishing playground. Show the Terminal/Log output from the Render backend simultaneously.*
"At the backend, we bypass slow API polling. We stream the visual DOM frames directly to Gemma-4-31b running on Cerebras WSE-3 hardware. Because of Cerebras's massive memory bandwidth, we achieve extreme Time-To-First-Token performance."

**[0:45 - 0:60] Speculative Early-Exit & Impact**
*Visual: The browser instantly locks with the red "CRITICAL THREAT DETECTED" overlay as the backend detects the malicious form endpoint.*
"Instead of waiting for the full LLM response, our async Python interceptor speculatively parses the SSE stream. The exact millisecond the 'CRITICAL' token is generated, we break the loop and fire a WebSocket screen-lock command back to the edge. Sub-500 millisecond visual threat interception, deployed globally."

## End of Demo
Highlight that this architecture prevents credential harvesting before the user can even type their password, changing the paradigm from reactive cleanup to proactive, zero-latency interception.
