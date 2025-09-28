import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def generate_graphs(df, location, output_dir):
    print(f"\nProcessing graphs for {location}")
    flavors = df["tcp_flavor"].unique()

    # Combined Throughput over Time
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

    ax1.set_title(f"Throughput Comparison for {location}", fontsize=16)
    ax1.set_xlabel("Time (s)", fontsize=12)
    ax1.set_ylabel("Throughput (Mbps)", fontsize=12)
    ax1.legend()
    ax1.grid(True)
    plt.tight_layout()
    filename1 = os.path.join(
        output_dir, f"{location}_throughput_comparison.png")
    plt.savefig(filename1)
    plt.close(fig1)
    print(f"Saved: {filename1}")

    # Combined CWND over Time
    fig2, ax2 = plt.subplots(figsize=(12, 7))

    for flavor in flavors:
        flavor_df = df[df["tcp_flavor"] == flavor]
        ax2.plot(
            flavor_df["time_iter"],
            flavor_df["cwnd_size_kb"],
            marker="o",
            linestyle="-",
            label=flavor,
        )

    ax2.set_title(f"CWND Size Comparison for {location}", fontsize=16)
    ax2.set_xlabel("Time (s)", fontsize=12)
    ax2.set_ylabel("Congestion Window Size (KB)", fontsize=12)
    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()
    filename2 = os.path.join(output_dir, f"{location}_cwnd_comparison.png")
    plt.savefig(filename2)
    plt.close(fig2)
    print(f"Saved: {filename2}")

    # per flavor graphs
    for flavor in flavors:
        flavor_df = df[df["tcp_flavor"] == flavor]

        # Throughput & Delay over Time
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
            f"Throughput & RTT for {flavor.upper()} in {location}", fontsize=16
        )
        fig3.tight_layout()
        filename3 = os.path.join(
            output_dir, f"{location}_{flavor}_throughput_rtt.png"
        )
        plt.savefig(filename3)
        plt.close(fig3)
        print(f"Saved: {filename3}")

        # Throughput & CWND over Time
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
            flavor_df["cwnd_size_kb"],
            color="tab:green",
            marker="x",
            linestyle="--",
        )
        ax4_cwnd.set_ylabel("CWND (KB)", fontsize=12, color="tab:green")
        ax4_thr.set_title(
            f"Throughput & CWND for {flavor.upper()} in {location}", fontsize=16
        )
        fig4.tight_layout()
        filename4 = os.path.join(
            output_dir, f"{location}_{flavor}_throughput_cwnd.png"
        )
        plt.savefig(filename4)
        plt.close(fig4)
        print(f"Saved: {filename4}")

        # RTT & CWND over Time
        fig5, ax5_rtt = plt.subplots(figsize=(12, 7))
        ax5_cwnd = ax5_rtt.twinx()
        ax5_rtt.set_xlabel("Time (s)", fontsize=12)
        ax5_rtt.plot(
            flavor_df["time_iter"],
            flavor_df["rtt_ms"],
            color="tab:red",
            marker="o",
        )
        ax5_rtt.set_ylabel("RTT (ms)", fontsize=12, color="tab:red")
        ax5_cwnd.plot(
            flavor_df["time_iter"],
            flavor_df["cwnd_size_kb"],
            color="tab:green",
            marker="x",
            linestyle="--",
        )
        ax5_cwnd.set_ylabel("CWND (KB)", fontsize=12, color="tab:green")
        ax5_rtt.set_title(
            f"RTT & CWND for {flavor.upper()} in {location}", fontsize=16
        )
        fig5.tight_layout()
        filename5 = os.path.join(
            output_dir, f"{location}_{flavor}_rtt_cwnd.png"
        )
        plt.savefig(filename5)
        plt.close(fig5)
        print(f"Saved: {filename5}")


def generate_lan_vs_wlan_graphs(lan_df, wlan_df, location, output_dir):
    if lan_df.empty or wlan_df.empty:
        return

    flavors = set(lan_df["tcp_flavor"].unique()).intersection(
        set(wlan_df["tcp_flavor"].unique())
    )
    if not flavors:
        return

    for flavor in flavors:
        lan_flavor_df = lan_df[lan_df["tcp_flavor"] == flavor]
        wlan_flavor_df = wlan_df[wlan_df["tcp_flavor"] == flavor]

        # Throughput Comparison
        plt.style.use("seaborn-v0_8-notebook")
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(
            lan_flavor_df["time_iter"],
            lan_flavor_df["throughput_mbps"],
            marker="o",
            linestyle="-",
            label="LAN",
        )
        ax.plot(
            wlan_flavor_df["time_iter"],
            wlan_flavor_df["throughput_mbps"],
            marker="o",
            linestyle="-",
            label="WLAN",
        )
        ax.set_title(
            f"Throughput LAN vs WLAN for {flavor.upper()} in {location}",
            fontsize=16,
        )
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("Throughput (Mbps)", fontsize=12)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        filename = os.path.join(
            output_dir, f"{location}_{flavor}_lan_vs_wlan_throughput.png"
        )
        plt.savefig(filename)
        plt.close(fig)
        print(f"Saved: {filename}")

        # RTT Comparison
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(
            lan_flavor_df["time_iter"],
            lan_flavor_df["rtt_ms"],
            marker="o",
            linestyle="-",
            label="LAN",
        )
        ax.plot(
            wlan_flavor_df["time_iter"],
            wlan_flavor_df["rtt_ms"],
            marker="o",
            linestyle="-",
            label="WLAN",
        )
        ax.set_title(
            f"RTT LAN vs WLAN for {flavor.upper()} in {location}", fontsize=16,
        )
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("RTT (ms)", fontsize=12)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        filename = os.path.join(
            output_dir, f"{location}_{flavor}_lan_vs_wlan_rtt.png"
        )
        plt.savefig(filename)
        plt.close(fig)
        print(f"Saved: {filename}")

        # CWND Comparison
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(
            lan_flavor_df["time_iter"],
            lan_flavor_df["cwnd_size_kb"],
            marker="o",
            linestyle="-",
            label="LAN",
        )
        ax.plot(
            wlan_flavor_df["time_iter"],
            wlan_flavor_df["cwnd_size_kb"],
            marker="o",
            linestyle="-",
            label="WLAN",
        )
        ax.set_title(
            f"CWND LAN vs WLAN for {flavor.upper()} in {location}",
            fontsize=16,
        )
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("CWND (KB)", fontsize=12)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        filename = os.path.join(
            output_dir, f"{location}_{flavor}_lan_vs_wlan_cwnd.png"
        )
        plt.savefig(filename)
        plt.close(fig)
        print(f"Saved: {filename}")


def generate_load_vs_noload_graphs(load_df, noload_df, location, output_dir):
    if load_df.empty or noload_df.empty:
        return

    flavors = set(load_df["tcp_flavor"].unique()).intersection(
        set(noload_df["tcp_flavor"].unique())
    )
    if not flavors:
        return

    for flavor in flavors:
        load_flavor_df = load_df[load_df["tcp_flavor"] == flavor]
        noload_flavor_df = noload_df[noload_df["tcp_flavor"] == flavor]

        # Throughput Comparison
        plt.style.use("seaborn-v0_8-notebook")
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(
            load_flavor_df["time_iter"],
            load_flavor_df["throughput_mbps"],
            marker="o",
            linestyle="-",
            label="Load",
        )
        ax.plot(
            noload_flavor_df["time_iter"],
            noload_flavor_df["throughput_mbps"],
            marker="o",
            linestyle="-",
            label="No Load",
        )
        ax.set_title(
            f"Throughput Load vs No Load for {flavor.upper()} in {location}",
            fontsize=16,
        )
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("Throughput (Mbps)", fontsize=12)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        filename = os.path.join(
            output_dir, f"{location}_{flavor}_load_vs_noload_throughput.png"
        )
        plt.savefig(filename)
        plt.close(fig)
        print(f"Saved: {filename}")

        # RTT Comparison
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(
            load_flavor_df["time_iter"],
            load_flavor_df["rtt_ms"],
            marker="o",
            linestyle="-",
            label="Load",
        )
        ax.plot(
            noload_flavor_df["time_iter"],
            noload_flavor_df["rtt_ms"],
            marker="o",
            linestyle="-",
            label="No Load",
        )
        ax.set_title(
            f"RTT Load vs No Load for {flavor.upper()} in {location}",
            fontsize=16,
        )
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("RTT (ms)", fontsize=12)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        filename = os.path.join(
            output_dir, f"{location}_{flavor}_load_vs_noload_rtt.png"
        )
        plt.savefig(filename)
        plt.close(fig)
        print(f"Saved: {filename}")

        # CWND Comparison
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.plot(
            load_flavor_df["time_iter"],
            load_flavor_df["cwnd_size_kb"],
            marker="o",
            linestyle="-",
            label="Load",
        )
        ax.plot(
            noload_flavor_df["time_iter"],
            noload_flavor_df["cwnd_size_kb"],
            marker="o",
            linestyle="-",
            label="No Load",
        )
        ax.set_title(
            f"CWND Load vs No Load for {flavor.upper()} in {location}",
            fontsize=16,
        )
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("CWND (KB)", fontsize=12)
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        filename = os.path.join(
            output_dir, f"{location}_{flavor}_load_vs_noload_cwnd.png"
        )
        plt.savefig(filename)
        plt.close(fig)
        print(f"Saved: {filename}")


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

    # Preprocess data
    df["throughput_mbps"] = df["bits_per_second"] / 1_000_000
    df["cwnd_size_kb"] = df["cwnd_size_bytes"] / 1_000
    df["load"] = df["test_name"].apply(
        lambda x: "noload" not in x.lower()
    )
    df["wlan"] = df["test_name"].apply(
        lambda x: "wlan" in x.lower()
    )
    df["location"] = df["test_name"].apply(
        lambda x: x.split('_')[0] if '_' in x else 'unknown'
    )

    # Get the unique test name and flavors for titles and looping
    location = df["location"].unique()
    for loc in location:
        loc_df = df[df["location"] == loc]

        loc_dir = os.path.join(output_dir, loc)
        os.makedirs(loc_dir, exist_ok=True)

        lan_df = loc_df[(loc_df["wlan"] == False) & (loc_df["load"] == False)]
        if not lan_df.empty:
            print(f"\nGenerating LAN graphs for {loc}...")
            generate_graphs(lan_df, f"{loc}_lan_noload", loc_dir)
        wlan_df = loc_df[(loc_df["wlan"] == True) & (loc_df["load"] == False)]
        if not wlan_df.empty:
            print(f"\nGenerating WLAN graphs for {loc}...")
            generate_graphs(wlan_df, f"{loc}_wlan_noload", loc_dir)
        load_df = loc_df[(loc_df["load"] == True) & (loc_df["wlan"] == True)]
        if not load_df.empty:
            print(f"\nGenerating Load graphs for {loc}...")
            generate_graphs(load_df, f"{loc}_wlan_load", loc_dir)
        noload_df = loc_df[(loc_df["load"] == False) &
                           (loc_df["wlan"] == True)]
        if not noload_df.empty:
            print(f"\nGenerating No Load graphs for {loc}...")
            generate_graphs(noload_df, f"{loc}_wlan_noload", loc_dir)

        generate_lan_vs_wlan_graphs(lan_df, wlan_df, loc, loc_dir)
        generate_load_vs_noload_graphs(load_df, noload_df, loc, loc_dir)

    print("\nAll graphs have been generated and saved successfully.")


if __name__ == "__main__":
    main()
