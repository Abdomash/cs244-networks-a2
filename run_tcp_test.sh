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
TEST_DURATION=60 # in seconds
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
	echo "--- Testing $flavor"

	# Set TCP flavor
	echo "Setting System TCP flavor to $flavor"
	sysctl -w net.ipv4.tcp_congestion_control=$flavor

	# Create flavor directory
	echo "Creating directory for $flavor results"
	mkdir -p "$flavor"
	IPERF_LOG="$flavor/iperf3.json"

	# Reset log files
	echo "" >"$IPERF_LOG"

	SECONDS=0

	# Run Iperf3
	echo "Starting iperf3 test for $TEST_DURATION seconds..."
	iperf3 -c "$SERVER_IP" \
		-t "$TEST_DURATION" \
		-b 0 \
		-B "$CLIENT_IP" \
		-i "$SAMPLE_INTERVAL" \
		-O 4 \
		-J >"$IPERF_LOG" &
	IPERF_PID=$!

	# Wait for iperf3
	wait "$IPERF_PID"
	echo "iperf3 done."
	echo "Test took $SECONDS seconds"

	# Avoid flooding network with tests
	sleep 3
done

echo
echo "--- Experiment finished ---"
echo "All tests are done."
echo "Results in $OUTPUT_DIR."

# Reset original TCP flavor
echo "Restoring original TCP flavor to $ORIG_FLAVOR"
sysctl -w net.ipv4.tcp_congestion_control=$ORIG_FLAVOR >/dev/null
