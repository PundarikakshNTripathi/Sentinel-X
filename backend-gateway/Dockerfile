# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download || true
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o gateway .

# Final stage
FROM gcr.io/distroless/static-debian12
WORKDIR /
COPY --from=builder /app/gateway /gateway
USER nonroot:nonroot
ENTRYPOINT ["/gateway"]
