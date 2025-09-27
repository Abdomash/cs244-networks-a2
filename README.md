# Network Performance Using Different TCP Congestion Control Algorithms

* Abdulrahman Alshahrani
* CS 244 Networks - Assignment 2
* 28 Sep 2025

## Overview

This project investigates the performance of different TCP congestion control algorithms (Reno, Cubic, BBR, and Vegas) under various network conditions using iperf3 for performance measurement. The experiment is conducted by running a series of tests from my device various public servers that support iperf3 benchmarks.

## Methodology

Each test is basically comprised of the following steps:
- Setting the chosen TCP flavor (Reno, Cubic, BBR, or Vegas).
- Run the following processes concurrently for a chosen amount of time:
    1. Run iperf3 to measure throughput.
    2. Run ping to measure latency.
    3. Run `ss -ti` to get CWND sizes.
- Store their logs.

## Requirements

- Python 3.x
- iperf3
- Bash shell
- Matplotlib
- Pandas


## How to Run

1. **Running the Tests**

**Note**: You need to run this script with `sudo` to be able to change the TCP flavors.
    
    ```bash
    sudo bash run_tcp_tests.sh <server_ip> <network_card_name> <test_name>
    ```
    
    - `<server_ip>`: The IP address of the iperf3 server (e.g., `iperf.scottlinux.com`).
    - `<network_card_name>`: The name of your network interface (e.g., `eth0`).
    - `<test_name>`: A name for the test to identify the output files (e.g., `amsterdam_wlan_noload`).

2. **Parsing the Results**
    
    After running the tests, you can parse their results using:
    
    ```bash
    python3 parse_results.py -o <output> -d <directory_name>
    ```
    
    - `<output>`: The name of the output file to save the parsed results (default is `combined_results.csv`).
    - `<directory_name>`: The directory where the test results are stored (default is `results`).

    This will generate a single CSV file combining all the results for easier analysis.

3. **Generating Plots**
    
    To generate plots from the parsed results, use:
    
    ```bash
    python3 generate_graphs.py -i <input_file> -o <output_directory>
    ```
    
    - `<input_file>`: The CSV file containing the parsed results (default is `combined_results.csv`).
    - `<output_directory>`: The directory to save the generated plots (default is `plots`).

