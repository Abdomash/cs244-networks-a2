import os
import re
import sys
import csv
import json
import argparse


def parse_ping_log(file_path):
    """
    Parses a ping.log file to extract RTT

    Returns A list of rtts
    """

    ping_data = []

    # Regex to find 'time=XX.X ms'
    ping_regex = re.compile(r"time=([\d\.]+)\s*ms")
    try:
        with open(file_path, "r") as f:
            for line in f:
                match = ping_regex.search(line)
                if match:
                    rtt = float(match.group(1))
                    ping_data.append(rtt)
    except (IOError, ValueError) as e:
        print(f"Warning: Could not parse ping {file_path}. Error: {e}")
        return []
    return ping_data


def parse_cwnd_log(file_path):
    """
    Parses a cwnd.log file to extract the congestion window size.

    Returns A list of integers representing the cwnd_size in bytes.
    """
    cwnd_data = []
    try:
        with open(file_path, "r") as f:
            next(f, None)  # Skip header
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    # The second column is the cwnd_bytes
                    cwnd_data.append(int(parts[1]))
    except (IOError, ValueError, IndexError) as e:
        print(f"Warning: Could not parse cwnd {file_path}. Error: {e}")
        return []
    return cwnd_data


def parse_iperf_json(file_path):
    """
    Parses an iperf3.json file to extract throughput/interval.

    Returns A list of floats representing throughput in bits/second.
    """
    throughput_data = []
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            intervals = data.get("intervals", [])
            for interval in intervals:
                sum_data = interval.get("sum", {})
                bits_per_second = sum_data.get("bits_per_second")
                if bits_per_second is not None:
                    throughput_data.append(bits_per_second)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse iperf {file_path}. Error: {e}")
        return []
    return throughput_data


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate TCP test results into a single CSV file.")
    parser.add_argument('-o', '--output', type=str,
                        default="combined_results.csv",
                        help="Output CSV file name (default: combined_results.csv)",
                        )
    parser.add_argument('-d', '--directory', type=str, default="results",
                        help="Root directory containing the test results (default: results)",
                        )
    args = parser.parse_args()

    output_filepath = args.output
    root_dir = args.directory

    if not os.path.isdir(root_dir):
        print(f"Error: Root directory '{root_dir}' not found.")
        sys.exit(1)

    all_results = []
    print(f"Starting data aggregation '{root_dir}'...")

    # Walk through the directory: results/TEST_NAME/TCP_FLAVOR
    for test_name in sorted(os.listdir(root_dir)):
        test_path = os.path.join(root_dir, test_name)
        if not os.path.isdir(test_path):
            continue

        print(f"\nProcessing Test: {test_name}")
        for tcp_flavor in sorted(os.listdir(test_path)):
            flavor_path = os.path.join(test_path, tcp_flavor)
            if not os.path.isdir(flavor_path):
                continue

            print(f"Processing {tcp_flavor}...")

            # Define file paths
            ping_file = os.path.join(flavor_path, "ping.log")
            cwnd_file = os.path.join(flavor_path, "cwnd.log")
            iperf_file = os.path.join(flavor_path, "iperf3.json")

            # Check if all required files exist
            if not all(os.path.exists(f) for f in [ping_file, cwnd_file, iperf_file]):
                print("Warning: Missing one or more data files. Skipping.")
                continue

            # Parse all the data files
            ping_data = parse_ping_log(ping_file)
            cwnd_data = parse_cwnd_log(cwnd_file)
            throughput_data = parse_iperf_json(iperf_file)

            # Align data lengths (truncate to the shortest)
            min_len = min(len(ping_data), len(cwnd_data), len(throughput_data))
            if min_len == 0:
                print(
                    "Warning: One or more data files are empty. Skipping.")
                continue

            # Combine the data for this run
            for i in range(min_len):
                all_results.append(
                    {
                        "test_name": test_name,
                        "tcp_flavor": tcp_flavor,
                        "time_iter": i,
                        "bits_per_second": throughput_data[i],
                        "rtt_ms": ping_data[i],
                        "cwnd_size_bytes": cwnd_data[i],
                    }
                )

    if not all_results:
        print("Warning: No results were processed. No output CSV will not be created.")
        return

    print(f"\nWriting {len(all_results)} total rows to '{output_filepath}'...")
    header = [
        "test_name",
        "tcp_flavor",
        "time_iter",
        "bits_per_second",
        "rtt_ms",
        "cwnd_size_bytes",
    ]
    try:
        with open(output_filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(all_results)
        print("Done. Aggregation complete.")
    except IOError as e:
        print(f"Error: Could not write to output file {
              output_filepath}. Error: {e}")


if __name__ == "__main__":
    main()
