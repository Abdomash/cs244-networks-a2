import os
import re
import sys
import csv
import json
import argparse


def parse_iperf_json(file_path):
    """
    Parses an iperf3.json file to extract throughput, RTT, and CWND data.

    Returns A tuple of 3 lists of floats representing throughput (bps), RTT (ms), and CWND (bytes).
    """
    throughput_data = []
    rtt_data = []
    cwnd_data = []
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            intervals = data.get("intervals", [])
            for interval in intervals:
                sum_data = interval.get("sum", {})
                streams_data = interval.get("streams", [])[0]
                rtt_ms = streams_data.get("rtt") / 1000.0
                if rtt_ms is not None:
                    rtt_data.append(rtt_ms)

                cwnd = streams_data.get("snd_cwnd")
                if cwnd is not None:
                    cwnd_data.append(cwnd)

                bits_per_second = sum_data.get("bits_per_second")
                if bits_per_second is not None:
                    throughput_data.append(bits_per_second)

    except (IOError, json.JSONDecodeError) as e:
        print(f"Warning: Could not parse iperf {file_path}. Error: {e}")
        return []
    return throughput_data, rtt_data, cwnd_data


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
            iperf_file = os.path.join(flavor_path, "iperf3.json")

            # Check if all required files exist
            if not os.path.exists(iperf_file):
                print("Warning: Missing iperf3.json file. Skipping.")
                continue

            # Parse all the data files
            throughput_data, rtt_data, cwnd_data = parse_iperf_json(iperf_file)

            if len(throughput_data) == 0:
                print(
                    "Warning: One or more data files are empty. Skipping.")
                continue

            # Combine the data for this run
            for i in range(len(throughput_data)):
                all_results.append(
                    {
                        "test_name": test_name,
                        "tcp_flavor": tcp_flavor,
                        "time_iter": i,
                        "bits_per_second": throughput_data[i],
                        "rtt_ms": rtt_data[i],
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
