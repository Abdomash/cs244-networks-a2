#!/bin/bash

# CLI args
if [ "$#" -ne 3 ]; then
	echo "Usage: $0 <ip-address> <network-card-name> <description>"
	echo "Example: sudo $0 192.168.1.100 eth0 baseline_test"
	exit 1
fi

SERVER_IP=$1
NIC_NAME=$2
TEST_DESCRIPTION=$3

# Output file name
OUTPUT_CSV="tcp_test_${NIC_NAME}_${TEST_DESCRIPTION}.csv"

# Config
TEST_DURATION=30

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
echo "Client IP: $BIND_IP."

# Iterate through each algorithm
for algo in "${TCP_FLAVORS[@]}"; do
	echo
	echo "--- Testing algorithm: $algo on interface: $NIC_NAME"

	# Set the system-wide TCP congestion control algorithm
	echo "Setting TCP flavor to $algo"
	sysctl -w net.ipv4.tcp_congestion_control=$algo

	# Run the iperf3 test
	echo "Running iperf3 test for $TEST_DURATION seconds..."
	iperf_result=$(iperf3 -c "$SERVER_IP" -t "$TEST_DURATION" -B "$BIND_IP" -J -O 5)

	if [ $? -ne 0 ]; then
		echo "Error: iperf3 test failed for $algo on $NIC_NAME."
		throughput_mbps=-1
	else
		throughput_mbps=$(echo "$iperf_result" | jq '.end.sum_received.bits_per_second / 1000000')
	fi

	# Run ping for 10 seconds and calculate mean RTT
	echo "Running ping test to measure RTT..."
	ping_result=$(ping -I "$NIC_NAME" -c 10 "$SERVER_IP")
	mean_rtt_ms=$(echo "$ping_result" | tail -1 | awk -F '/' '{print $5}')

	# Parse iperf output
	timestamp=$(date --iso-8601=seconds)

	# Append the results
	echo "$timestamp,$algo,$NIC_NAME,$TEST_DESCRIPTION,$SERVER_IP,$TEST_DURATION,$throughput_mbps,$mean_rtt_ms" >>"$OUTPUT_CSV"

	echo "Test complete. Throughput: ${throughput_mbps} Mbps, Mean RTT: ${mean_rtt_ms} ms"

	# Avoid flooding network with tests
	sleep 3
done

echo
echo "--- Experiment finished ---"
echo "All tests are complete. Results are logged in '$OUTPUT_CSV'."

# Reset original TCP flavor
echo "Restoring original TCP flavor to $ORIGINAL_ALGO"
sysctl -w net.ipv4.tcp_congestion_control=$ORIGINAL_ALGO >/dev/null
