# Jetson Telemetry MCP

An MCP (Model Context Protocol) server exposing NVIDIA Jetson telemetry endpoints. Specifically built to work seamlessly with LLMs inside systems like ZeroClaw or natively supporting the MCP specification. 

This read-only MCP server exposes system diagnostic data from the Jetson Tegra system (such as an AGX Orin) over an SSE transport, enabling large language models to seamlessly monitor hardware health, including:

- 🌡️ **Thermal Zones** (CPU, GPU, SOC, etc.)
- ⚡ **Power Rails** (Voltages, Current, Power consumption)
- 💡 **Power Modes**
- 🌀 **Fan Status**

## Installation & Usage

You can build and deploy the container on your local Jetson platform using Docker.

```bash
docker build -t jetson-telemetry-mcp .
```

To run with appropriate privileges to read sysfs mappings on the host Jetson:

```bash
docker run -d \
  --name jetson-telemetry \
  -v /sys:/sys:ro \
  -v /etc/nvpmodel.conf:/etc/nvpmodel.conf:ro \
  -v /var/lib/nvpmodel:/var/lib/nvpmodel:ro \
  -p 8765:8765 \
  jetson-telemetry-mcp
```
