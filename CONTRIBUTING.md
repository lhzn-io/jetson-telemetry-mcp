# Contributing to Jetson Telemetry MCP

First off, thank you for considering contributing to the Jetson Telemetry MCP server!

This repository aims to be the standard way to expose **native, read-only hardware observability** (thermals, power rails, clocks) on NVIDIA Jetson edge devices (Orin, Thor, etc.) to AI agents using the Model Context Protocol (MCP).

## Core Philosophy

1. **Read-Only Strictly Enforced**: This server must never include tools that mutate system state, write to disks, or issue state-changing commands. It is purely for observation and telemetry.
2. **Jetson-Native**: Tools should leverage Jetson-specific hardware interfaces (like `sysfs` paths for INA3221, `tegrastats`, `nvpmodel`). Generic Linux tools (like `df` or `top`) should largely be avoided unless directly related to hardware acceleration contexts.
3. **No External Dependencies**: We try to keep the Python image as slim as possible, utilizing standard libraries where we can, aside from `mcp` and `FastMCP`.

## Development Setup

Testing this MCP server properly requires physical Jetson hardware, as many of the `sysfs` endpoints and binaries (`tegrastats`, `jetson_clocks`) are exclusive to L4T (Linux for Tegra).

1. Clone the repository directly on your Jetson device.
2. Make your tool additions or modifications in `server.py`.
3. Use Docker to build and run the test container, ensuring you mount the required host paths as read-only.
   ```bash
   docker build -t jetson-telemetry-mcp:local .
   docker run --rm -p 8765:8765 \
       -v /sys:/sys:ro \
       -v /usr/bin/tegrastats:/usr/bin/tegrastats:ro \
       -v /var/lib/nvpmodel/status:/var/lib/nvpmodel/status:ro \
       -v /usr/bin/jetson_clocks:/usr/bin/jetson_clocks:ro \
       jetson-telemetry-mcp:local
   ```
4. Update `SKILL.md` to document the new tools and provide usage guidelines for LLM agents.

## Submitting Changes

1. Fork the repository and create your feature branch from `main`.
2. Ensure you use [Conventional Commits](https://www.conventionalcommits.org/)-style commit messages (e.g., `feat: add NVDLA engine usage tool`, `fix: handle missing pwm-fan nodes gracefully`).
3. Open a Pull Request with a clear description of the new telemetry being exposed and the Jetson models you verified it on.