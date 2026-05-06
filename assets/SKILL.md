---
name: jetson-telemetry
description: >
  Report on the health of NVIDIA Jetson hardware (Orin/Thor) — thermals, power rails,
  clocks, memory, and board identity.
capabilities:
  - system_health
  - thermal_report
  - power_report
  - performance_report
---

# Skill: Jetson Telemetry

Report on the health and status of NVIDIA Jetson hardware.
All health and info commands are invoked using the MCP tools exposed by the `jetson-telemetry-mcp` service.

## Core Capabilities
- **Board Identity**: Use `board_identity` to determine the exact hardware model and serial number. Use `jetpack_version` to identify the Jetpack and L4T release sequence.
- **Health Report**: Use `tegrastats_snapshot` to get a snapshot of CPU load, GPU load, RAM usage, and overarching statistics.
- **Thermals**: Use `thermal_zones` for detailed CPU, GPU, and SoC temperatures. Use `fan_status` to observe PWM fan targets and current RPM.
- **Power**: Use `power_mode` to check the current NVPM mode. Use `power_rails` to read instantaneous wattage, voltage, and current on specific board channels (VDD_IN, VDD_CPU, VDD_GPU) via the INA3221 sensors.
- **Performance**: Use `clocks_status` to map out the current operating frequencies of the CPU, GPU, and EMC.

## Usage Guidelines for Agents
1. **Combine Data**: When asked for a "full health check", pull `tegrastats_snapshot`, `thermal_zones`, and `power_rails` for a complete picture.
2. **Warn on Extremes**: Flag any temperatures above 80°C or anomalous power draw states.
3. **Understand Context**: Jetson devices operate with shared memory (Unified Memory Architecture). GPU memory and CPU RAM are the same physical pool. When reporting on memory via `tegrastats`, explain it as a unified resource.