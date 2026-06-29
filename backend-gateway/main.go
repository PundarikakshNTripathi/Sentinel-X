// Package main implements a highly concurrent TCP WebSocket multiplexer.
// It intercepts edge connections from the browser extension and proxies them
// directly into the Python Inference Engine, offloading connection management overhead.
package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

func handleConnection(w http.ResponseWriter, r *http.Request) {
	clientConn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("Upgrade error:", err)
		return
	}
	defer clientConn.Close()

	// Connect to Python FastAPI WebSocket
	engineUrl := os.Getenv("ENGINE_WS_URL")
	if engineUrl == "" {
		engineUrl = "ws://engine:8000/ws/monitor" // Local docker fallback
	}

	engineConn, _, err := websocket.DefaultDialer.Dial(engineUrl, nil)
	if err != nil {
		log.Println("Engine dial error:", err)
		return
	}
	defer engineConn.Close()

	errc := make(chan error, 2)

	// Proxy client -> engine
	go func() {
		for {
			mt, message, err := clientConn.ReadMessage()
			if err != nil {
				errc <- err
				return
			}
			err = engineConn.WriteMessage(mt, message)
			if err != nil {
				errc <- err
				return
			}
		}
	}()

	// Proxy engine -> client
	go func() {
		for {
			mt, message, err := engineConn.ReadMessage()
			if err != nil {
				errc <- err
				return
			}
			err = clientConn.WriteMessage(mt, message)
			if err != nil {
				errc <- err
				return
			}
		}
	}()

	<-errc
}

func main() {
	http.HandleFunc("/ws/monitor", handleConnection)
	log.Println("Gateway running on :8080")
	http.ListenAndServe(":8080", nil)
}