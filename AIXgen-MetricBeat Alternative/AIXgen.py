import subprocess
import json
import time
import psutil
import socket
import requests
import logging
import syslog

# Load Configuration
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return {}

config = load_config()

# Configurable Parameters
ES_HOST = config.get("ES_HOST", "http://your-elasticsearch-server:9200")
INDEX_NAME = config.get("INDEX_NAME", "aix-metrics")
SLACK_WEBHOOK_URL = config.get("SLACK_WEBHOOK_URL", "")
LOG_FILE = config.get("LOG_FILE", "/var/log/aix_metricbeat.log")
JSON_OUTPUT_FILE = config.get("JSON_OUTPUT_FILE", "/var/log/aix_metricbeat.json")
COLLECTION_INTERVAL = config.get("COLLECTION_INTERVAL", 10)
ALERT_THRESHOLDS = config.get("ALERT_THRESHOLDS", {"cpu": 90, "memory": 90, "disk": 90})

# Logging Configuration
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to run shell commands
def run_command(command):
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command} | Error: {e}")
        syslog.syslog(syslog.LOG_ERR, f"Metricbeat Error: {e}")
        return None

# CPU Usage
def get_cpu_usage():
    output = run_command("vmstat 1 2 | tail -1")
    return {"user": float(output.split()[12]), "system": float(output.split()[13]), "idle": float(output.split()[14])} if output else {}

# Memory Usage
def get_memory_usage():
    output = run_command("svmon -G | grep memory")
    return {"total_mb": int(output.split()[1]) // 256, "used_mb": int(output.split()[2]) // 256} if output else {}

# Swap Usage
def get_swap_usage():
    output = run_command("lsps -s")
    return {"total_mb": int(output.split()[1][:-1]), "used_percent": float(output.split()[2][:-1])} if output else {}

# Disk Usage
def get_disk_usage():
    output = run_command("df -m | tail -n +2")
    return [{"filesystem": fields[0], "usage_percent": int(fields[4][:-1])} for fields in (line.split() for line in output.split("\n"))] if output else []

# Network Stats
def get_network_stats():
    output = run_command("netstat -i")
    return [{"interface": fields[0], "errors": int(fields[3]) + int(fields[7])} for fields in (line.split() for line in output.split("\n")[1:]) if len(fields) >= 6] if output else []

# Load Average
def get_load_average():
    output = run_command("uptime")
    return {"1min": float(output.split()[-3].replace(",", ""))} if output else {}

# Running Processes
def get_process_stats():
    return [{"pid": p.pid, "name": p.name(), "cpu_percent": p.cpu_percent(), "memory_percent": p.memory_percent()} for p in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])]

# Collect all metrics
def collect_metrics():
    return {
        "hostname": socket.gethostname(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": get_cpu_usage(),
        "memory": get_memory_usage(),
        "swap": get_swap_usage(),
        "disk": get_disk_usage(),
        "network": get_network_stats(),
        "load_average": get_load_average(),
        "processes": get_process_stats()
    }

# Send Data to Elasticsearch
def send_to_elasticsearch(metrics):
    try:
        response = requests.post(f"{ES_HOST}/{INDEX_NAME}/_doc", json=metrics, headers={"Content-Type": "application/json"})
        logging.info(f"Sent to Elasticsearch: {response.status_code} | {response.text}")
    except requests.RequestException as e:
        logging.error(f"Failed to send to Elasticsearch: {e}")

# Write Metrics to JSON File
def write_metrics_to_file(metrics):
    try:
        with open(JSON_OUTPUT_FILE, "w") as f:
            json.dump(metrics, f, indent=4)
        logging.info("Metrics written to JSON file.")
    except Exception as e:
        logging.error(f"Error writing to file: {e}")

# Send Slack Alerts
def send_slack_alert(message):
    if SLACK_WEBHOOK_URL:
        try:
            requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        except requests.RequestException as e:
            logging.error(f"Failed to send Slack alert: {e}")

# Check Alerts
def check_alerts(metrics):
    alerts = []

    if metrics["cpu"].get("user", 0) > ALERT_THRESHOLDS["cpu"]:
        alerts.append("⚠️ High CPU usage detected!")

    if (metrics["memory"].get("used_mb", 0) / max(metrics["memory"].get("total_mb", 1), 1)) * 100 > ALERT_THRESHOLDS["memory"]:
        alerts.append("⚠️ High memory usage detected!")

    for disk in metrics["disk"]:
        if disk["usage_percent"] > ALERT_THRESHOLDS["disk"]:
            alerts.append(f"⚠️ High disk usage on {disk['filesystem']}!")

    for alert in alerts:
        logging.warning(alert)
        syslog.syslog(syslog.LOG_WARNING, alert)
        send_slack_alert(alert)

# Main Loop
def main():
    while True:
        config = load_config()  # Reload config dynamically
        metrics = collect_metrics()
        write_metrics_to_file(metrics)
        send_to_elasticsearch(metrics)
        check_alerts(metrics)
        time.sleep(COLLECTION_INTERVAL)

if __name__ == "__main__":
    main()
