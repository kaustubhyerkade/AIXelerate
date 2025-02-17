import os
import time
import json
import socket
import requests
import threading
import gzip
import ssl
import yaml
import numpy as np
from kafka import KafkaProducer

# Load Configuration
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

CONFIG = load_config()

# Load Registry
def load_registry():
    if os.path.exists(CONFIG["registry_file"]):
        with open(CONFIG["registry_file"], "r") as f:
            return json.load(f)
    return {}

# Save Registry
def save_registry(registry):
    with open(CONFIG["registry_file"], "w") as f:
        json.dump(registry, f)

# Read Log File with Tracking
def read_logs(file_path, position):
    try:
        with open(file_path, "r") as f:
            f.seek(position)
            lines = f.readlines()
            position = f.tell()
        return lines, position
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return [], position

# Read Logs from Syslog
def read_syslog():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(CONFIG["syslog_socket"])
    
    while True:
        data, _ = sock.recvfrom(4096)
        log = data.decode("utf-8")
        
        # Filter by facility
        if CONFIG["syslog_facility"] in log:
            process_logs([log])

# Compress Logs
def compress_logs(logs):
    return gzip.compress("\n".join(logs).encode())

# TLS Encryption for Logstash
def create_tls_socket():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_verify_locations(CONFIG["tls_cert"])
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_sock = context.wrap_socket(sock, server_hostname=CONFIG["logstash_host"])
    
    return secure_sock

# Send Logs to Kafka
def send_to_kafka(logs):
    if not logs:
        return
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=CONFIG["kafka_broker"],
            security_protocol="SSL" if CONFIG["tls_enabled"] else "PLAINTEXT",
            ssl_cafile=CONFIG["tls_cert"] if CONFIG["tls_enabled"] else None
        )
        for log in logs:
            producer.send(CONFIG["kafka_topic"], log.encode())
        producer.flush()
        print(f"Sent {len(logs)} logs to Kafka topic '{CONFIG['kafka_topic']}'")
    except Exception as e:
        print(f"Kafka Error: {e}")

# Send Alerts for Anomalous Logs
def send_alert(message):
    if CONFIG["alert_type"] == "email":
        requests.post(CONFIG["email_api"], json={"to": CONFIG["alert_email"], "subject": "Log Anomaly", "body": message})
    elif CONFIG["alert_type"] == "slack":
        requests.post(CONFIG["slack_webhook"], json={"text": message})

# Anomaly Detection (Z-score)
def detect_anomalies(logs):
    log_lengths = [len(log) for log in logs]
    if len(log_lengths) < 10:
        return []

    mean = np.mean(log_lengths)
    std_dev = np.std(log_lengths)
    anomalies = [log for log in logs if abs(len(log) - mean) > 2 * std_dev]

    if anomalies:
        send_alert(f"🚨 Detected {len(anomalies)} anomalies in logs!")
    
    return anomalies

# Process Logs
def process_logs(logs):
    if not logs:
        return

    anomalies = detect_anomalies(logs)

    send_to_kafka(logs)
    send_to_logstash(logs)
    send_to_elasticsearch(logs)

# Send Logs to Logstash with TLS
def send_to_logstash(logs):
    if not logs:
        return
    
    data = compress_logs(logs) if CONFIG["use_compression"] else "\n".join(logs).encode()
    
    try:
        if CONFIG["tls_enabled"]:
            sock = create_tls_socket()
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM if CONFIG["logstash_protocol"] == "tcp" else socket.SOCK_DGRAM)
        
        sock.connect((CONFIG["logstash_host"], CONFIG["logstash_port"]))
        sock.sendall(data)
        sock.close()
        print(f"Sent {len(logs)} logs to Logstash")
    except Exception as e:
        print(f"Logstash Error: {e}")

# Send Logs to Elasticsearch with TLS
def send_to_elasticsearch(logs):
    if not logs:
        return
    
    bulk_data = ""
    for log in logs:
        bulk_data += json.dumps({"index": {"_index": CONFIG["elasticsearch_index"]}}) + "\n"
        bulk_data += json.dumps({"message": log.strip()}) + "\n"
    
    headers = {"Content-Type": "application/json"}
    
    for attempt in range(CONFIG["retry_count"]):
        try:
            response = requests.post(CONFIG["elasticsearch_url"], data=bulk_data, headers=headers, verify=CONFIG["tls_cert"] if CONFIG["tls_enabled"] else False)
            if response.status_code == 200:
                print(f"Sent {len(logs)} logs to Elasticsearch")
                return
            else:
                print(f"Elasticsearch Error: {response.text}, Retrying...")
        except Exception as e:
            print(f"Error sending logs to Elasticsearch: {e}, Retrying...")
        time.sleep(CONFIG["retry_delay"])

# Process Each Log File in a Separate Thread
def process_log_file(log_file, registry):
    while True:
        position = registry.get(log_file, 0)
        logs, new_position = read_logs(log_file, position)
        registry[log_file] = new_position

        if logs:
            process_logs(logs)

        save_registry(registry)
        time.sleep(CONFIG["read_interval"])

# Main Function
def main():
    registry = load_registry()
    threads = []

    for log_file in CONFIG["log_files"]:
        t = threading.Thread(target=process_log_file, args=(log_file, registry))
        threads.append(t)
        t.start()

    if CONFIG["syslog_enabled"]:
        t_syslog = threading.Thread(target=read_syslog)
        threads.append(t_syslog)
        t_syslog.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
