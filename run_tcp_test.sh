#!/bin/bash

# --- Configuration ---

# ensure run on 'sudo'
if [[ $EUID -ne 0 ]]; then
	echo "Run with 'sudo'!"
	exit 1
fi

# CLI args
if [ "$#" -ne 3 ]; then
	echo "Usage: <server-ip> <network-card> <description>"
	echo "Example: sudo $0 192.168.1.100 eth0 baseline_test"
	exit 1
fi

SERVER_IP=$1
NIC_NAME=$2
TEST_DESCRIPTION=$3

# Output file name
OUTPUT_CSV="tcp_test_${NIC_NAME}_${TEST_DESCRIPTION}.csv"

# Config
TEST_DURATION=30 # in seconds
SAMPLE_INTERVAL=1  # in seconds

# TCP flavors
TCP_FLAVORS=("bbr" "cubic" "reno" "vegas")
ORIGINAL_ALGO=$(sysctl -n net.ipv4.tcp_congestion_control)

echo "Starting TCP test..."
echo "NIC: $NIC_NAME"
echo "Results filepath: $OUTPUT_CSV"

# Write csv header
echo "timestamp,algorithm,interface,server_ip,description,duration_sec,throughput_mbps,mean_rtt_ms" > "$OUTPUT_CSV"

# Get IP of the given NIC_NAME
BIND_IP=$(ip -4 addr show "$NIC_NAME" | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
if [ -z "$BIND_IP" ]; then
	echo "No IPv4 is valid '$NIC_NAME'."
	exit 1
fi

echo "Client IP: $BIND_IP."

# temp files for logs
IPERF_LOG=$(mktemp)
PING_LOG=$(mktemp)
CWND_LOG=$(mktemp)

# Iterate
for algo in "${TCP_FLAVORS[@]}"; do
	echo
	echo "--- Testing flavor: $algo on interface: $NIC_NAME"

	# Set TCP flavor
	echo "Setting TCP flavor to $algo"
	sysctl -w net.ipv4.tcp_congestion_control=$algo

	# Run Iperf3
	echo "Starting iperf3 test for $TEST_DURATION seconds..."
	iperf3 -c "$SERVER_IP" \
		-t "$TEST_DURATION" \
		-B "$BIND_IP" \
		-i "$SAMPLE_INTERVAL" \
		-J >"$IPERF_LOG" &
	IPERF_PID=$!

	# Start ping
	echo "Starting ping to measure RTT..."
	ping -I "$NIC_NAME" \
		-i "$SAMPLE_INTERVAL" \
		"$SERVER_IP" >"$PING_LOG" &
	PING_PID=$!

	# Start a loop to poll CWND
	echo "Starting CWND monitoring..."
	(
		# Wait until iperf connects first
		sleep 3

		for ((i = 0; i < TEST_DURATION; i++)); do
			CWND=$(ss -ti "dst $SERVER_IP" | grep -oP 'cwnd:\K\d+')
			echo "$i,$CWND" >>"$CWND_LOG"
			sleep "$SAMPLE_INTERVAL"
		done
	) &
	CWND_PID=$!

	# Wait for iperf3
	wait "$IPERF_PID"
	echo "iperf3 done."

	# Kill ping and CWND PIDs
	kill "$PING_PID" "$CWND_PID" 2>/dev/null
	echo "ping and CWND done."

	# --- Process and Save Data ---
	echo "Saving data for '$algo'..."

	# Get throughput from iperf logs
	iperf_data=$(
		jq -r '.intervals[].sum | "\(.start) \(.bits_per_second / 1e6)"' "$IPERF_LOG"
	)

	# Get RTT from ping logs
	ping_data=$(grep "time=" "$PING_LOG" | awk -F'time=' '{print $2}' | cut -d' ' -f1)

	# Get CWND from cwnd logs
	cwnd_data=$(cut -d',' -f2 "$CWND_LOG")

	# Combine the data and write to CSV
	paste <(echo "$iperf_data") <(echo "$ping_data") <(echo "$cwnd_data") |
		while read -r iperf_line rtt cwnd; do
			# Parse the iperf line
			time_sec=$(echo "$iperf_line" | awk '{print $1}')
			throughput_mbps=$(echo "$iperf_line" | awk '{print $2}')

			# Use current timestamp for this batch
			timestamp=$(date --iso-8601=seconds)

			# Write to CSV
			echo "$timestamp,$algo,$NIC_NAME,$SERVER_IP,$TEST_DESCRIPTION,${time_sec%.*},$throughput_mbps,$rtt,$cwnd" >>"$OUTPUT_CSV"
		done

	# Clean up logs for the next run
	> "$IPERF_LOG"
	> "$PING_LOG"
	> "$CWND_LOG"

	echo "Data for '$algo' saved."

	# Avoid flooding network with tests
	sleep 3
done

echo
echo "--- Experiment finished ---"
echo "All tests are complete. Results are logged in '$OUTPUT_CSV'."

# Reset original TCP flavor
echo "Restoring original TCP flavor to $ORIGINAL_ALGO"
sysctl -w net.ipv4.tcp_congestion_control=$ORIGINAL_ALGO >/dev/null

# Remove temp files
rm "$IPERF_LOG" "$PING_LOG" "$CWND_LOG"
