#!/bin/bash

# --- Configuration ---

# Ensure run as 'sudo'
if [[ $EUID -ne 0 ]]; then
	echo "Run with 'sudo'"
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

# Output directory
OUTPUT_DIR="results/$TEST_DESCRIPTION"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR" || exit 1

# Config
TEST_DURATION=30 # in seconds
SAMPLE_INTERVAL=1  # in seconds

# TCP flavors
TCP_FLAVORS=("bbr" "cubic" "reno" "vegas")
ORIG_FLAVOR=$(sysctl -n net.ipv4.tcp_congestion_control)

echo "Starting TCP test..."
echo "NIC: $NIC_NAME"
echo "Results will be in $OUTPUT_DIR/"

# Get IP of the given NIC_NAME
CLIENT_IP=$(ip -4 addr show "$NIC_NAME" | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
if [ -z "$CLIENT_IP" ]; then
	echo "No IPv4 is valid '$NIC_NAME'."
	exit 1
fi

echo "Client IP: $CLIENT_IP"
echo "Server IP: $SERVER_IP"

for flavor in "${TCP_FLAVORS[@]}"; do
	echo
	echo "--- Testing flavor: $flavor on interface: $NIC_NAME"

	# Set TCP flavor
	echo "Setting TCP flavor to $flavor"
	sysctl -w net.ipv4.tcp_congestion_control=$flavor

	mkdir -p "$flavor"

	IPERF_LOG="$flavor/iperf3.json"
	PING_LOG="$flavor/ping.log"
	CWND_LOG="$flavor/cwnd.log"

	# Reset log files (in case of retries)
	echo "" >"$IPERF_LOG"
	echo "" >"$PING_LOG"
	echo "time_sec,cwnd_bytes" >"$CWND_LOG"

	# Run Iperf3
	echo "Starting iperf3 test for $TEST_DURATION seconds..."
	iperf3 -c "$SERVER_IP" \
		-t "$TEST_DURATION" \
		-b 0 \
		-B "$CLIENT_IP" \
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
			CWND=$(ss -ti "dst $SERVER_IP:5201" | grep -m 1 -oP 'cwnd:\K\d+')
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

	# Avoid flooding network with tests
	sleep 3
done

echo
echo "--- Experiment finished ---"
echo "All tests are complete. Results are in $OUTPUT_DIR."

# Reset original TCP flavor
echo "Restoring original TCP flavor to $ORIG_FLAVOR"
sysctl -w net.ipv4.tcp_congestion_control=$ORIG_FLAVOR >/dev/null
