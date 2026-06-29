# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod ./
# COPY go.sum ./ # Uncomment when go.sum exists

# Download dependencies
RUN go mod download || true # ignore if go.mod is empty or has no deps yet

# Copy the rest of the source code
COPY . .

# Build the Go application statically
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o gateway .

# Final stage: Distroless
FROM gcr.io/distroless/static-debian12

WORKDIR /

# Copy the binary from the builder stage
COPY --from=builder /app/gateway /gateway

# Use nonroot user for security
USER nonroot:nonroot

# Run the gateway
ENTRYPOINT ["/gateway"]
