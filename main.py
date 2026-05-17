import asyncio
import aiohttp
import base64
import re
import socket
import ipaddress
import sys
import random

SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/vless",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2"
]

CLOUDFLARE_IPV4_RANGES = [
    "173.245.0.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
    "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22"
]
cf_networks = [ipaddress.ip_network(ip) for ip in CLOUDFLARE_IPV4_RANGES]

def is_cloudflare(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in cf_networks:
            if ip in net:
                return True
        return False
    except ValueError:
        return False

def fix_base64_padding(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return data

async def fetch_configs(session, url):
    try:
        async with session.get(url, timeout=15) as response:
            text = await response.text()
            try:
                padded_text = fix_base64_padding(text.strip())
                decoded_data = base64.b64decode(padded_text).decode('utf-8')
                return decoded_data.splitlines()
            except Exception:
                return text.splitlines()
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
        return []

async def check_ip_and_filter(config):
    if not config.strip():
        return None

    pattern = r"@(.*?):(\d+)"
    match = re.search(pattern, config)

    if match:
        host = match.group(1)

        try:
            if not is_cloudflare(host):
                return config
            return None
        except ValueError:
            pass 

        try:
            loop = asyncio.get_running_loop()
            info = await loop.getaddrinfo(host, None, family=socket.AF_INET)
            ip = info[0][4][0]

            if not is_cloudflare(ip):
                return config
        except Exception:
            return None

    return None

async def main():
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        print("--- Scraping Started... Please wait ---")
        all_raw_configs = []

        fetch_tasks = [fetch_configs(session, url) for url in SOURCES]
        results = await asyncio.gather(*fetch_tasks)

        for configs in results:
            all_raw_configs.extend(configs)

        print(f"Total found: {len(all_raw_configs)} nodes.")
        print("Filtering True-IP nodes...")

        tasks = [check_ip_and_filter(cfg) for cfg in all_raw_configs]
        filtered_results = await asyncio.gather(*tasks)

        true_ip_nodes = [res for res in filtered_results if res]

        if len(true_ip_nodes) > 150:
            true_ip_nodes = random.sample(true_ip_nodes, 150)

        with open("True_IP_Configs.txt", "w", encoding="utf-8") as f:
            for node in true_ip_nodes:
                f.write(node + "\n")

        print(f"--- Done! ---")
        print(f"Saved {len(true_ip_nodes)} True-IP nodes to 'True_IP_Configs.txt'")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
