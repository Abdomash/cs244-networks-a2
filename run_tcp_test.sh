#!/bin/bash

# CLI args
if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <interface> <description>"
	echo "Example: sudo $0 eth0 baseline_test"
	exit 1
fi

# Output file name
NIC_NAME=$1
TEST_DESCRIPTION=$2
OUTPUT_CSV="tcp_test_${NIC_NAME}_${TEST_DESCRIPTION}.csv"

# Config
SERVER_IP="192.168.1.100"
TEST_DURATION=30

# TCP flavors
TCP_FLAVORS=("bbr" "cubic" "reno" "vegas")
ORIGINAL_ALGO=$(sysctl -n net.ipv4.tcp_congestion_control)

echo "Starting TCP test..."
echo "NIC: $NIC_NAME"
echo "Results filepath: $OUTPUT_CSV"

# Write csv header
echo "timestamp,algorithm,interface,server_ip,duration_sec,throughput_mbps,mean_rtt_ms" > "$OUTPUT_CSV"

# Get IP of the given NIC_NAME
BIND_IP=$(ip -4 addr show "$NIC_NAME" | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
echo "Client IP: $BIND_IP."

# Iterate through each algorithm
for algo in "${TCP_FLAVORS[@]}"; do
	echo "--- Testing algorithm: $algo on interface: $NIC_NAME"

	# Set the system-wide TCP congestion control algorithm
	echo "Setting TCP flavor to $algo"
	sysctl -w net.ipv4.tcp_congestion_control=$algo

	# Run the iperf3 test
	echo "Running iperf3 test for $TEST_DURATION seconds..."
	iperf_result=$(iperf3 -c "$SERVER_IP" -t "$TEST_DURATION" -B "$BIND_IP" -J -O 5)

	# make the results '-1' if iperf3 failed
	if [ $? -ne 0 ]; then
		echo "Error: iperf3 test failed for $algo on $NIC_NAME."
		timestamp=$(date --iso-8601=seconds)
		echo "$timestamp,$algo,$NIC_NAME,$TEST_DESCRIPTION,$SERVER_IP,$TEST_DURATION,-1,-1" >>"$OUTPUT_CSV"
		continue
	fi

	# Parse iperf output
	throughput_mbps=$(echo "$iperf_result" | jq '.end.sum_received.bits_per_second / 1000000')
	mean_rtt_ms=$(echo "$iperf_result" | jq '.end.sum_sent.mean_rtt / 1000')
	timestamp=$(date --iso-8601=seconds)

	# Append the results
	echo "$timestamp,$algo,$NIC_NAME,$TEST_DESCRIPTION,$SERVER_IP,$TEST_DURATION,$throughput_mbps,$mean_rtt_ms" >>"$OUTPUT_CSV"

	echo "Test complete. Throughput: ${throughput_mbps} Mbps, Mean RTT: ${mean_rtt_ms} ms"

	# Avoid flooding network with tests
	sleep 3
done

# --- Cleanup ---
echo
echo "--- Experiment finished ---"
echo "All tests are complete. Results are logged in '$OUTPUT_CSV'."

# Reset original TCP flavor
echo "Restoring original TCP flavor to $ORIGINAL_ALGO"
sysctl -w net.ipv4.tcp_congestion_control=$ORIGINAL_ALGO >/dev/null
