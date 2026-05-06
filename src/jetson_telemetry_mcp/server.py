import glob
import json
import os
import subprocess

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Create the FastMCP server
mcp = FastMCP(
    "jetson-telemetry", 
    dependencies=["mcp"],
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False)
)

@mcp.tool()
async def tegrastats_snapshot() -> str:
    """Read a single snapshot from tegrastats."""
    try:
        result = subprocess.run(
            ["timeout", "2", "tegrastats"],
            capture_output=True,
            text=True,
            check=False
        )
        lines = result.stdout.strip().split("\n")
        if lines:
            return json.dumps({"raw": lines[0]})
        return json.dumps({"error": "No output"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def thermal_zones() -> str:
    """Read thermal zones from sysfs."""
    try:
        zones = {}
        for path in glob.glob("/sys/devices/virtual/thermal/thermal_zone*"):
            try:
                with open(f"{path}/type", "r") as f:
                    tz_type = f.read().strip()
                with open(f"{path}/temp", "r") as f:
                    tz_temp = int(f.read().strip()) / 1000.0
                zones[tz_type] = tz_temp
            except OSError:
                pass
        return json.dumps(zones)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def power_mode() -> str:
    """Read the active nvpmodel power mode."""
    try:
        if os.path.exists("/var/lib/nvpmodel/status"):
            with open("/var/lib/nvpmodel/status", "r") as f:
                mode_str = f.read().strip()
                return json.dumps({"raw": f"NV Power Mode: {mode_str}"})
        else:
            return json.dumps({"error": "/var/lib/nvpmodel/status not found. Mount it into the container."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def clocks_status() -> str:
    """Read the active jetson_clocks status."""
    try:
        result = subprocess.run(["jetson_clocks", "--show"], capture_output=True, text=True, check=False)
        return json.dumps({"raw": result.stdout.strip()})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def power_rails() -> str:
    """Read INA3221 power monitors for VDD_IN, VDD_CPU, VDD_GPU, VDD_SOC etc."""
    try:
        results = {}
        hwmon_paths = glob.glob("/sys/bus/i2c/drivers/ina3221/*/hwmon/hwmon*")
        for hwmon in hwmon_paths:
            for i in range(1, 4):
                label_path = f"{hwmon}/in{i}_label"
                in_path = f"{hwmon}/in{i}_input"
                curr_path = f"{hwmon}/curr{i}_input"
                if os.path.exists(label_path) and os.path.exists(in_path) and os.path.exists(curr_path):
                    with open(label_path, "r") as f:
                        rail_name = f.read().strip()
                    with open(in_path, "r") as f:
                        voltage_mv = int(f.read().strip())
                    with open(curr_path, "r") as f:
                        current_ma = int(f.read().strip())
                    power_mw = (voltage_mv * current_ma) // 1000
                    results[rail_name] = {
                        "voltage_mv": voltage_mv,
                        "current_ma": current_ma,
                        "power_mw": power_mw
                    }
        return json.dumps(results) if results else json.dumps({"error": "No INA3221 sensors found or readable."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def fan_status() -> str:
    """Read PWM fan target and current speed."""
    try:
        results = {}
        target_path = "/sys/devices/pwm-fan/target_pwm"
        if os.path.exists(target_path):
            with open(target_path, "r") as f:
                results["target_pwm"] = int(f.read().strip())
        
        hwmon_paths = glob.glob("/sys/class/hwmon/hwmon*/fan*_input")
        for path in hwmon_paths:
            try:
                with open(path, "r") as f:
                    results["fan_rpm"] = int(f.read().strip())
            except OSError:
                pass
        return json.dumps(results) if results else json.dumps({"error": "Fan nodes unavailable."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def board_identity() -> str:
    """Read hardware model and device tree info (identifies exact Jetson model)."""
    try:
        results = {}
        if os.path.exists("/proc/device-tree/model"):
            with open("/proc/device-tree/model", "r") as f:
                results["model"] = f.read().strip("\x00")
        if os.path.exists("/proc/device-tree/serial-number"):
            with open("/proc/device-tree/serial-number", "r") as f:
                results["serial"] = f.read().strip("\x00")
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def jetpack_version() -> str:
    """Read the Jetpack version sequence and L4T release info from /etc/nv_tegra_release."""
    try:
        release_path = "/etc/nv_tegra_release"
        if os.path.exists(release_path):
            with open(release_path, "r") as f:
                return json.dumps({"raw": f.read().strip()})
        else:
            return json.dumps({"error": f"{release_path} not found. Ensure it is mounted into the container."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.prompt()
def jetson_telemetry_instructions() -> str:
    """Get the usage guidelines and capabilities for the Jetson telemetry MCP server."""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(base_dir, "..", "..", "..", "assets", "SKILL.md")
        
        if os.path.exists(assets_path):
            with open(assets_path, "r") as f:
                return f.read()
        elif os.path.exists("/app/assets/SKILL.md"):
            with open("/app/assets/SKILL.md", "r") as f:
                return f.read()
        else:
            return "Note: SKILL.md asset not found. You have access to Jetson sysfs telemetry tools like thermal_zones, power_rails, fan_status, and board_identity."
    except Exception as e:
        return f"Error loading instructions: {e}"

def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "sse":
        port = int(os.getenv("PORT", "8765"))
        host = os.getenv("HOST", "0.0.0.0")
        print(f"Starting FastMCP on {host}:{port}")
        mcp.settings.port = port
        mcp.settings.host = host
        mcp.run(transport="sse")
    else:
        mcp.run()

if __name__ == "__main__":
    main()
