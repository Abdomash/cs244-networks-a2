
# --- WLAN ---

# No Load
sudo bash run_tcp_test.sh 185.102.217.170 wlp62s0 romania_wlan_noload
sudo bash run_tcp_test.sh iperf.worldstream.nl wlp62s0 amsterdam_wlan_noload
sudo bash run_tcp_test.sh 213.158.175.240 wlp62s0 cairo_wlan_noload

# Load
sudo bash run_tcp_test.sh 185.102.217.170 wlp62s0 romania_wlan_load
sudo bash run_tcp_test.sh iperf.worldstream.nl wlp62s0 amsterdam_wlan_load
sudo bash run_tcp_test.sh 213.158.175.240 wlp62s0 cairo_wlan_load

# --- LAN ---

# No Load
sudo bash run_tcp_test.sh 185.102.217.170 enp61s0 romania_wlan_noload
sudo bash run_tcp_test.sh iperf.worldstream.nl enp61s0 amsterdam_wlan_noload
sudo bash run_tcp_test.sh 213.158.175.240 enp61s0 cairo_wlan_noload

# Load
sudo bash run_tcp_test.sh 185.102.217.170 enp61s0 romania_wlan_load
sudo bash run_tcp_test.sh iperf.worldstream.nl enp61s0 amsterdam_wlan_load
sudo bash run_tcp_test.sh 213.158.175.240 enp61s0 cairo_wlan_load
