# Custom Skills & Capabilities

This file tracks the autonomous skills, techniques, or specific runbooks the agent has developed and utilized during the development of Sentinel-X.

## 1. Distroless Containerization (Go)
- **Context:** Security-first deployment for the Go backend gateway.
- **Action:** Utilize `golang:1.22-alpine` for the build stage to compile statically linked binaries (`CGO_ENABLED=0`).
- **Target:** Deploy on `gcr.io/distroless/static-debian12` for the final stage, eliminating shell environments and package managers from the production artifact.

## 2. Optimized Python Builds (uv)
- **Context:** High-performance, deterministic dependency resolution for the Python inference engine.
- **Action:** Employ a multi-stage build using `uv` to construct a `.venv` (with bytecode compilation) in a builder stage.
- **Target:** Produce a lean `python:3.12-slim` runtime image copying only the `.venv` and source code, running as a non-root user.
