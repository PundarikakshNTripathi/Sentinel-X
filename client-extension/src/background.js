let ws = new WebSocket("ws://localhost:8080/ws/monitor");

ws.onmessage = (event) => {
    let data = JSON.parse(event.data);
    if (data.action === "LOCK_SCREEN") {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.scripting.executeScript({
                target: {tabId: tabs.id},
                func: injectBlastShield
            });
        });
    }
};

function injectBlastShield() {
    let shield = document.createElement("div");
    shield.style.position = "fixed";
    shield.style.top = "0";
    shield.style.left = "0";
    shield.style.width = "100vw";
    shield.style.height = "100vh";
    shield.style.backgroundColor = "rgba(255, 0, 0, 0.85)";
    shield.style.backdropFilter = "blur(10px)";
    shield.style.zIndex = "999999";
    shield.style.display = "flex";
    shield.style.justifyContent = "center";
    shield.style.alignItems = "center";
    shield.style.color = "white";
    shield.style.fontSize = "40px";
    shield.style.fontWeight = "bold";
    shield.style.fontFamily = "sans-serif";
    shield.innerText = "CRITICAL THREAT BLOCKED BY SENTINEL-X";
    document.body.appendChild(shield);
}