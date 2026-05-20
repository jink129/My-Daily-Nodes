import asyncio
import aiohttp
import base64
import re
import socket
import ipaddress
import sys
import random

# ထုတ်ပေးမည့် အများဆုံး ဆာဗာအရေအတွက်
OUTPUT_LIMIT = 150

# Source (၂၀) ခု
SOURCES = [
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/normal/vless",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub.txt",
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/ts-sf/fly/main/v2",
    "https://raw.githubusercontent.com/itsyebekhe/HiN-VPN/main/subscription",
    "https://raw.githubusercontent.com/free18/v2ray/main/v2ray",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/V2RAY_RAW.txt",
    "https://raw.githubusercontent.com/vpei/Free-Node-Merge/main/o/node.txt",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt",
    "https://raw.githubusercontent.com/mheidari98/.proxy/main/all",
    "https://raw.githubusercontent.com/AzadNetCH/Clash/main/V2Ray.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/server.txt",
    "https://raw.githubusercontent.com/learnhard-cn/free_proxy_ss/main/proxy.txt",
    "https://raw.githubusercontent.com/iwxf/free-v2ray/main/index.txt",
    "https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg"
]

# Cloudflare IPs (မြန်မာနိုင်ငံတွင် ချိတ်မရသော IP များ)
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

def fix_base64(data):
    missing = len(data) % 4
    if missing:
        data += '=' * (4 - missing)
    return data

async def fetch(session, url):
    try:
        async with session.get(url, timeout=15) as r:
            text = await r.text()
            try:
                decoded = base64.b64decode(fix_base64(text.strip())).decode()
                return decoded.splitlines()
            except:
                return text.splitlines()
    except:
        return []

# DNS Resolve အများကြီး တစ်ပြိုင်နက်လုပ်ရင် Error တက်မှာစိုး၍ Semaphore သုံးထားခြင်း
dns_sem = asyncio.Semaphore(200)

async def check_ip_and_filter(config):
    if not config.strip():
        return None

    if not config.startswith(("vless://", "vmess://", "trojan://", "ss://")):
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
            pass # IP မဟုတ်ဘဲ Domain ဖြစ်နေလျှင် ဆက်သွားရန်

        async with dns_sem:
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
        print("Fetching sources... (Scraping from 20 links)")
        tasks = [fetch(session, url) for url in SOURCES]
        results = await asyncio.gather(*tasks)

        all_lines = []
        for r in results:
            all_lines.extend(r)

        # ပုံစံတူများကို အရင်ဖယ်ရှားခြင်း (စစ်ဆေးရမည့် အချိန်ကို သက်သာစေရန်)
        all_lines = list(set(all_lines))
        print("Total unique raw configs:", len(all_lines))
        
        # အချိန်အရမ်းမကြာစေရန် အလုံး ၂၅၀၀ ကိုသာ ကျပန်းရွေးချယ်ပြီး True-IP စစ်မည်
        if len(all_lines) > 2500:
            all_lines = random.sample(all_lines, 2500)
            print("Randomly selected 2500 nodes for True-IP testing...")

        print("Filtering True-IP nodes (Bypassing Cloudflare)... Please wait.")
        tasks = [check_ip_and_filter(cfg) for cfg in all_lines]
        filtered_results = await asyncio.gather(*tasks)

        true_ip_nodes = [res for res in filtered_results if res]

        print("Valid True-IP nodes found:", len(true_ip_nodes))

        if len(true_ip_nodes) > OUTPUT_LIMIT:
            true_ip_nodes = random.sample(true_ip_nodes, OUTPUT_LIMIT)

        # 1. ရိုးရိုး Text ဖိုင် သိမ်းခြင်း
        with open("nodes.txt", "w", encoding="utf-8") as f:
            for n in true_ip_nodes:
                f.write(n + "\n")

        # 2. Hiddify တွင်သုံးရန် Base64 ဖိုင် သိမ်းခြင်း
        sub_data = base64.b64encode("\n".join(true_ip_nodes).encode('utf-8')).decode('utf-8')
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write(sub_data)

        print("Saved", len(true_ip_nodes), "nodes")
        print("Files Generated: nodes.txt, subscription.txt")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
