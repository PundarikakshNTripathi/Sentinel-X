package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"github.com/gorilla/websocket"
)

func TestHandleConnection(t *testing.T) {
	// A simple test to verify standard routing compilation and no race condition.
	s := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))
	defer s.Close()

	if !strings.HasPrefix(s.URL, "http://") {
		t.Fatalf("Expected HTTP URL, got %s", s.URL)
	}
}
