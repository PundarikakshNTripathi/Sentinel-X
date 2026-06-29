package main

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

type Message struct {
	Image string `json:"image"`
}

func handleConnection(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err!= nil {
		log.Println("Upgrade error:", err)
		return
	}
	defer ws.Close()

	for {
		var msg Message
		err := ws.ReadJSON(&msg)
		if err!= nil {
			break
		}

		// Forward to Python FastAPI
		payload, _ := json.Marshal(map[string]string{"image_base64": msg.Image})
		resp, err := http.Post("http://engine:8000/analyze", "application/json", bytes.NewBuffer(payload))
		
		if err == nil {
			var result map[string]string
			json.NewDecoder(resp.Body).Decode(&result)
			resp.Body.Close()

			if result["status"] == "CRITICAL" {
				ws.WriteJSON(map[string]string{"action": "LOCK_SCREEN"})
			}
		}
	}
}

func main() {
	http.HandleFunc("/ws/monitor", handleConnection)
	log.Println("Gateway running on :8080")
	http.ListenAndServe(":8080", nil)
}