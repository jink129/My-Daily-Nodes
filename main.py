import asyncio
import aiohttp
import base64
import re
import random
import sys

OUTPUT_LIMIT = 120

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

def extract_nodes(lines):
    nodes = []
    for line in lines:
        if line.startswith(("vless://", "vmess://", "trojan://", "ss://")):
            nodes.append(line.strip())
    return nodes

async def main():
    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        print("Fetching sources...")
        tasks = [fetch(session, url) for url in SOURCES]
        results = await asyncio.gather(*tasks)

        all_lines = []
        for r in results:
            all_lines.extend(r)

        print("Total raw lines:", len(all_lines))
        nodes = extract_nodes(all_lines)
        print("Valid nodes:", len(nodes))

        # remove duplicates
        nodes = list(set(nodes))
        print("Unique nodes:", len(nodes))

        # random sample
        if len(nodes) > OUTPUT_LIMIT:
            nodes = random.sample(nodes, OUTPUT_LIMIT)

        # 1. ရိုးရိုး Text ဖိုင် သိမ်းခြင်း
        with open("nodes.txt", "w", encoding="utf-8") as f:
            for n in nodes:
                f.write(n + "\n")

        # 2. Hiddify/V2rayNG တွင်သုံးရန် Base64 ဖိုင် သိမ်းခြင်း
        sub_data = base64.b64encode("\n".join(nodes).encode('utf-8')).decode('utf-8')
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write(sub_data)

        print("Saved", len(nodes), "nodes")
        print("Files Generated: nodes.txt, subscription.txt")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
