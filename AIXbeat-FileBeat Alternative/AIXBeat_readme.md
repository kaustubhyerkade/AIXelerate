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
