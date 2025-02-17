AIXbeat - A lightweight log shipper script that mimics Filebeat’s functionalities.

Core Features:
✅Log Harvesting – Read log files incrementally (like Filebeat's harvester).

✅Registry Management – Track read positions to avoid duplicate logs.

✅Filtering & Processing – Optionally filter logs before sending.

✅Output to ELK – Send logs to Elasticsearch (directly) or Logstash (via TCP/UDP).

✅Rotation Handling – Detect rotated logs and continue processing.

✅Error Handling & Logging – Ensure stability in case of failures.

✅The python script reads logs, keeps track of read positions, and sends data to Logstash or Elasticsearch.

Dependencies:
Python 3.x (Ensure it's installed on AIX)
requests (for Elasticsearch)
socket (for Logstash TCP/UDP)


pip3 install requests
pip3 install requests pyyaml
pip3 install requests pyyaml cryptography
pip3 install requests pyyaml kafka-python numpy

How to Run on AIX - 
Save the script as aix_filebeat.py
Run the script in the background- 

nohup python3 aix_filebeat.py &

-----------------------------------------------------------------------------------------------------------

How It Works
Tracks Log Positions: Saves last read positions in /var/log/aix_filebeat_registry.json.
Reads New Logs: Continuously reads new lines from specified log files.
Sends to Logstash: Sends logs over TCP or UDP to Logstash.
Sends to Elasticsearch: Sends logs directly using Elasticsearch Bulk API.
Handles Log Rotation: If a log is rotated, it detects and starts from the new file.


Features- 
✅ Syslog Support – Reads AIX syslogs from /dev/log and filters by facility.
✅ TLS Encryption – Secure logs with SSL/TLS when sending to Logstash and Elasticsearch.
✅ Configurable Parameters – Easily change via config.json.
✅ Multi-threading – Each log file is handled by a separate thread for better performance.
✅ Compression – Logs are gzip-compressed before transmission (if enabled).
✅ Retry Logic – If Elasticsearch fails, it retries 3 times with a 5-second delay.
✅ Configurable – Uses a JSON config file instead of hardcoding values.
✅ Kafka Integration for real-time log processing.
✅ Anomaly Detection using Z-score.
✅ Slack/Email Alerts on log anomalies.
✅ TLS Encryption for Kafka, Logstash, and Elasticsearch.




------------------------------------------
Kibana Dashboard for AIX Log Visualization
------------------------------------------

Now that we have logs flowing into Elasticsearch, let’s create a Kibana Dashboard for real-time log monitoring.

✅ What This Dashboard Will Show

1️⃣ System Logs Overview – View logs filtered by severity (INFO, WARN, ERROR).

2️⃣ Log Volume Over Time – Identify log spikes and anomalies.

3️⃣ Top Log Sources – See which AIX servers generate the most logs.

4️⃣ Anomaly Detection Insights – Highlight unusual log patterns.


📌 Step 1: Configure Elasticsearch Index Pattern in Kibana

Open Kibana (http://your-kibana-host:5601).
Navigate to Stack Management → Index Patterns.
Click Create Index Pattern and enter:
Pattern: aix-logs-*
Time Field: @timestamp
Click Create Index Pattern.

📌 Step 2: Create the Kibana Dashboard
Go to Kibana → Dashboard and click Create Dashboard.
Now, add the following visualizations:

📊 Visualization 1: Log Volume Over Time
Click Create Visualization → Line Chart.
Choose aix-logs index.
X-Axis: @timestamp (Date Histogram).
Y-Axis: Count.
Save as Log Volume Over Time.

📊 Visualization 2: Logs by Severity
Click Create Visualization → Pie Chart.
Choose aix-logs index.
Slice By: Terms Aggregation on log_level.keyword.
Save as Logs by Severity.

📊 Visualization 3: Top Log Sources
Click Create Visualization → Bar Chart.
Choose aix-logs index.
X-Axis: Terms Aggregation on host.keyword.
Y-Axis: Count.
Save as Top Log Sources.

📊 Visualization 4: Anomaly Detection Logs
Click Create Visualization → Table.
Choose aix-logs index.
Add Filter: log_message contains "anomaly detected".
Save as Anomaly Logs.

📌 Step 3: Add Visualizations to the Dashboard
Open Dashboard and click Edit.
Click Add Panels → Select the four visualizations.
Save as AIX Logs Dashboard.


🔥 Final Result
✅ Real-time Log Monitoring 🚀
✅ Instant Anomaly Detection 📡
