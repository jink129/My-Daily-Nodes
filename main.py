import asyncio
import aiohttp
import base64

# Turkey keywords
TR_KEYWORDS = [
    "turkey",
    "istanbul",
    "ankara",
    "izmir",
    "turkiye",
    "🇹🇷"
]

# Source list (GitHub raw)
SOURCES = [
"https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
"https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
"https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
"https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
"https://raw.githubusercontent.com/ts-sf/fly/main/v2",
"https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
]

TIMEOUT = 15

def fix_base64(data):
    missing = len(data) % 4
    if missing:
        data += "=" * (4 - missing)
    return data

async def fetch(session, url):
    try:
        async with session.get(url, timeout=TIMEOUT) as r:
            txt = await r.text()
            # Base64 ဖြစ်နေလျှင် ဖြည်ချရန်၊ ရိုးရိုး Text ဆိုလျှင် ဒီအတိုင်းပြန်ပေးရန်
            try:
                decoded = base64.b64decode(fix_base64(txt.strip())).decode('utf-8')
                return decoded
            except:
                return txt
    except:
        return ""

def filter_turkey(lines):
    results = []
    for cfg in lines:
        if not cfg.strip():
            continue
            
        cfg_l = cfg.lower()
        if any(k in cfg_l for k in TR_KEYWORDS):
            results.append(cfg)
    return results

async def main():
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        print("Fetching sources...")
        tasks = [fetch(session, url) for url in SOURCES]
        responses = await asyncio.gather(*tasks)

    configs = []
    for text in responses:
        lines = text.splitlines()
        configs.extend(lines)

    # ပုံစံတူ Config များကို ဖယ်ရှားရန်
    configs = list(set(configs))

    print("Filtering Turkey nodes...")
    turkey_nodes = filter_turkey(configs)

    print("Total configs:", len(configs))
    print("Turkey nodes:", len(turkey_nodes))

    if not turkey_nodes:
        print("No Turkey nodes found.")
        return

    # save raw
    with open("turkey_nodes.txt", "w", encoding="utf-8") as f:
        for c in turkey_nodes:
            f.write(c + "\n")

    # base64 subscription
    sub = base64.b64encode("\n".join(turkey_nodes).encode('utf-8')).decode('utf-8')
    with open("turkey_subscription.txt", "w", encoding="utf-8") as f:
        f.write(sub)
        
    print("Files saved successfully!")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
