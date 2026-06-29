/**
 * Sentinel-X Background Service Worker
 * 
 * Maintains a persistent WebSocket connection to the Go Proxy API Gateway.
 * If a 'CRITICAL' threat token is intercepted by the backend VLM, this script instantly
 * utilizes chrome.scripting to inject a high z-index blocking overlay, locking the tab.
 */
function connectWebSocket() {
  const ws = new WebSocket('wss://sentinel-x-backend-gateway.onrender.com/ws/monitor');
  let captureInterval;

  ws.onopen = () => {
    console.log('Connected to Sentinel-X Gateway');
    
    // Begin continuous multimodal capture at 1 FPS
    captureInterval = setInterval(() => {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs.length > 0) {
          const tabId = tabs[0].id;
          
          // First, extract the DOM
          chrome.scripting.executeScript({
            target: { tabId: tabId },
            func: () => document.documentElement.outerHTML
          }, (results) => {
            if (chrome.runtime.lastError || !results || !results[0]) return;
            const dom = results[0].result;
            
            // Second, capture the visual frame
            chrome.tabs.captureVisibleTab(tabs[0].windowId, { format: 'jpeg', quality: 50 }, (dataUrl) => {
              if (chrome.runtime.lastError) return;
              if (dataUrl && ws.readyState === WebSocket.OPEN) {
                // Send the true multimodal payload
                ws.send(JSON.stringify({ image: dataUrl, dom: dom }));
              }
            });
          });
        }
      });
    }, 1000);
  };

  ws.onmessage = (event) => {
    console.log('Received message:', event.data);
    const data = event.data;
    
    // Support either direct 'CRITICAL' / 'LOCK' string or JSON action payload
    if (data.includes('CRITICAL') || data.includes('LOCK_SCREEN') || data.includes('LOCK')) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs.length > 0) {
          chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            func: injectWarningOverlay
          });
        }
      });
    } else if (data.includes('GATEWAY_ERROR')) {
      console.error("GATEWAY DISCONNECT REASON:", data);
    }
  };

  ws.onclose = () => {
    console.log('Disconnected. Reconnecting in 5 seconds...');
    clearInterval(captureInterval);
    setTimeout(connectWebSocket, 5000);
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket Error:', error);
  };
}

function injectWarningOverlay() {
  if (document.getElementById('sentinel-warning-overlay')) return;
  
  const overlay = document.createElement('div');
  overlay.id = 'sentinel-warning-overlay';
  overlay.style.position = 'fixed';
  overlay.style.top = '0';
  overlay.style.left = '0';
  overlay.style.width = '100vw';
  overlay.style.height = '100vh';
  overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.9)';
  overlay.style.color = 'white';
  overlay.style.zIndex = '999999';
  overlay.style.display = 'flex';
  overlay.style.flexDirection = 'column';
  overlay.style.justifyContent = 'center';
  overlay.style.alignItems = 'center';
  overlay.style.fontFamily = 'system-ui, sans-serif';
  
  const heading = document.createElement('h1');
  heading.innerText = '⚠️ CRITICAL THREAT DETECTED';
  heading.style.fontSize = '4rem';
  heading.style.fontWeight = 'bold';
  heading.style.marginBottom = '20px';
  
  const subtext = document.createElement('p');
  subtext.innerText = 'Sentinel-X has intercepted a malicious action. This session has been locked.';
  subtext.style.fontSize = '1.5rem';
  
  overlay.appendChild(heading);
  overlay.appendChild(subtext);
  document.body.appendChild(overlay);
}

connectWebSocket();