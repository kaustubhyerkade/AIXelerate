AIXgen - A Python script to implement a custom Metricbeat-like agent for IBM AIX, collecting system metrics and formatting them for Elasticsearch ingestion. It includes:

CPU Usage
Memory Usage
Disk Usage
Network Stats
Process Stats
Filesystem Stats
Load Average

This script gathers metrics using AIX-specific commands like vmstat, lsps, svmon, and netstat. 
It then formats the data as JSON for Elasticsearch ingestion. You can extend it by integrating it with Filebeat or Logstash for shipping logs to an ELK stack.

dependencies- 
pip install psutil
pip install psutil requests

nohup python aix_metricbeat.py &

Check Elasticsearch Ingestion - 

curl -X GET "http://your-elasticsearch-server:9200/aix-metrics/_search?pretty"

-------------------------------------------------------------------------------------------------------------------------------------------------------------------

Features - 

✅ All key system metrics (CPU, memory, swap, disk, network, load, processes)

✅ Integration with Elasticsearch (direct ingestion)

✅ Alerting readiness (thresholds for CPU, memory, and disk usage)

✅ Security enhancements (error handling, logging)

✅ IBM AIX Compatibility – Uses AIX-specific commands (vmstat, svmon, netstat, etc.)

✅ Elasticsearch Integration – Direct ingestion via REST API

✅ Filebeat Support – Writes JSON logs to /var/log/aix_metricbeat.json

✅ Logging & Error Handling – Logs errors and execution to /var/log/aix_metricbeat.log

✅ Threshold-Based Alerts – Detects high CPU, memory, and disk usage

✅ Daemon Mode (runs as a persistent background process)

✅ Lightweight & Efficient – Uses Python subprocess & psutil

✅ Modify values easily without changing the script

✅ Automatically reloads config on every run



