import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def generate_graphs(df, test_name, output_dir):
    df = df[df["test_name"] == test_name]
    flavors = df["tcp_flavor"].unique()

    # Graph 1: Combined Throughput over Time
    plt.style.use("seaborn-v0_8-notebook")
    fig1, ax1 = plt.subplots(figsize=(12, 7))

    for flavor in flavors:
        flavor_df = df[df["tcp_flavor"] == flavor]
        ax1.plot(
            flavor_df["time_iter"],
            flavor_df["throughput_mbps"],
            marker="o",
            linestyle="-",
            label=flavor,
        )

    ax1.set_title(f"Throughput Comparison for {test_name}", fontsize=16)
    ax1.set_xlabel("Time (s)", fontsize=12)
    ax1.set_ylabel("Throughput (Mbps)", fontsize=12)
    ax1.legend()
    ax1.grid(True)
    plt.tight_layout()
    filename1 = os.path.join(
        output_dir, f"{test_name}_throughput_comparison.png")
    plt.savefig(filename1)
    plt.close(fig1)
    print(f"Saved: {filename1}")

    # --- Graph 2: Combined CWND over Time ---
    fig2, ax2 = plt.subplots(figsize=(12, 7))

    for flavor in flavors:
        flavor_df = df[df["tcp_flavor"] == flavor]
        ax2.plot(
            flavor_df["time_iter"],
            flavor_df["cwnd_size_bytes"],
            marker="o",
            linestyle="-",
            label=flavor,
        )

    ax2.set_title(f"CWND Size Comparison for {test_name}", fontsize=16)
    ax2.set_xlabel("Time (s)", fontsize=12)
    ax2.set_ylabel("Congestion Window Size (Bytes)", fontsize=12)
    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()
    filename2 = os.path.join(output_dir, f"{test_name}_cwnd_comparison.png")
    plt.savefig(filename2)
    plt.close(fig2)
    print(f"Saved: {filename2}")

    # --- Graphs 3, 4, 5: Per-flavor analysis ---
    for flavor in flavors:
        flavor_df = df[df["tcp_flavor"] == flavor]

        # --- Graph 3: Throughput & Delay over Time (per flavor) ---
        fig3, ax3_thr = plt.subplots(figsize=(12, 7))
        ax3_rtt = ax3_thr.twinx()
        ax3_thr.set_xlabel("Time (s)", fontsize=12)
        ax3_thr.plot(
            flavor_df["time_iter"],
            flavor_df["throughput_mbps"],
            color="tab:blue",
            marker="o",
        )
        ax3_thr.set_ylabel("Throughput (Mbps)", fontsize=12, color="tab:blue")
        ax3_rtt.plot(
            flavor_df["time_iter"],
            flavor_df["rtt_ms"],
            color="tab:red",
            marker="x",
            linestyle="--",
        )
        ax3_rtt.set_ylabel("RTT (ms)", fontsize=12, color="tab:red")
        ax3_thr.set_title(
            f"Throughput & RTT for {flavor.upper()} in {test_name}", fontsize=16
        )
        fig3.tight_layout()
        filename3 = os.path.join(
            output_dir, f"{test_name}_{flavor}_throughput_rtt.png"
        )
        plt.savefig(filename3)
        plt.close(fig3)
        print(f"Saved: {filename3}")

        # --- Graph 4: Throughput & CWND over Time (per flavor) ---
        fig4, ax4_thr = plt.subplots(figsize=(12, 7))
        ax4_cwnd = ax4_thr.twinx()
        ax4_thr.set_xlabel("Time (s)", fontsize=12)
        ax4_thr.plot(
            flavor_df["time_iter"],
            flavor_df["throughput_mbps"],
            color="tab:blue",
            marker="o",
        )
        ax4_thr.set_ylabel("Throughput (Mbps)", fontsize=12, color="tab:blue")
        ax4_cwnd.plot(
            flavor_df["time_iter"],
            flavor_df["cwnd_size_bytes"],
            color="tab:green",
            marker="x",
            linestyle="--",
        )
        ax4_cwnd.set_ylabel("CWND (Bytes)", fontsize=12, color="tab:green")
        ax4_thr.set_title(
            f"Throughput & CWND for {flavor.upper()} in {test_name}", fontsize=16
        )
        fig4.tight_layout()
        filename4 = os.path.join(
            output_dir, f"{test_name}_{flavor}_throughput_cwnd.png"
        )
        plt.savefig(filename4)
        plt.close(fig4)
        print(f"Saved: {filename4}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate graphs from TCP flavors CSV data.")
    parser.add_argument(
        '-i', '--input',
        type=str,
        default="combined_results.csv",
        help="Input CSV file name (default: combined_results.csv)",
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default="graphs",
        help="Output directory for graphs (default: graphs)",
    )
    args = parser.parse_args()
    input_file = args.input
    output_dir = args.output_dir

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_file)
    df["throughput_mbps"] = df["bits_per_second"] / 1_000_000

    # Get the unique test name and flavors for titles and looping
    test_names = df["test_name"].unique()
    for test_name in test_names:
        print(f"\nProcessing graphs for test: {test_name}")
        generate_graphs(df, test_name, output_dir)

    print("\nAll graphs have been generated and saved successfully.")


if __name__ == "__main__":
    main()
