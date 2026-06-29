"""
FastAPI WebSocket entry point. Receives encoded base64 frames from the Go Proxy.
Implements an OpenCV-based Gaussian Structural Similarity Index Measure (SSIM)
to discard duplicate or highly similar frames, reducing overhead for the downstream VLM.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import base64
import cv2
import numpy as np
from src.interceptor import StreamInterceptor, ThreatDetectedException

app = FastAPI()
interceptor = StreamInterceptor()

def calculate_ssim(img1, img2):
    if img1.shape != img2.shape:
        return 0.0
    
    C1 = 6.5025
    C2 = 58.5225
    I1 = img1.astype(np.float32)
    I2 = img2.astype(np.float32)
    
    I2_2 = I2 * I2
    I1_2 = I1 * I1
    I1_I2 = I1 * I2
    
    mu1 = cv2.GaussianBlur(I1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(I2, (11, 11), 1.5)
    
    mu1_2 = mu1 * mu1
    mu2_2 = mu2 * mu2
    mu1_mu2 = mu1 * mu2
    
    sigma1_2 = cv2.GaussianBlur(I1_2, (11, 11), 1.5)
    sigma1_2 -= mu1_2
    
    sigma2_2 = cv2.GaussianBlur(I2_2, (11, 11), 1.5)
    sigma2_2 -= mu2_2
    
    sigma12 = cv2.GaussianBlur(I1_I2, (11, 11), 1.5)
    sigma12 -= mu1_mu2
    
    t1 = 2 * mu1_mu2 + C1
    t2 = 2 * sigma12 + C2
    t3 = t1 * t2
    
    t1 = mu1_2 + mu2_2 + C1
    t2 = sigma1_2 + sigma2_2 + C2
    t1 = t1 * t2
    
    ssim_map = t3 / t1
    return np.mean(ssim_map)

@app.websocket("/ws/monitor")
async def monitor_websocket(websocket: WebSocket):
    await websocket.accept()
    prev_image = None
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Now expecting a JSON payload from the extension containing both image and DOM
            import json
            try:
                payload = json.loads(data)
                encoded = payload.get("image", "")
                dom_content = payload.get("dom", "")
                
                header, encoded = encoded.split(",", 1) if "," in encoded else ("", encoded)
                if not encoded:
                    continue
                    
                img_bytes = base64.b64decode(encoded)
                np_arr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
                
                if img is None:
                    continue
                    
                if prev_image is not None:
                    if img.shape == prev_image.shape:
                        ssim_val = calculate_ssim(prev_image, img)
                        # Compute structural difference
                        if (1.0 - ssim_val) > 0.05:
                            try:
                                await interceptor.analyze_stream(encoded, dom_content)
                            except ThreatDetectedException:
                                await websocket.send_text("LOCK")
                                break
                
                prev_image = img
            except Exception as e:
                print(f"Error processing frame: {e}")

    except WebSocketDisconnect:
        pass