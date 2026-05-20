import requests
import base64

# -------- SETTINGS --------

MAX_SERVERS = 200

COUNTRY_KEYWORDS = [
"turkey","istanbul","ankara","izmir","turkiye",
"germany","frankfurt",
"netherlands","amsterdam",
"france","paris",
"uk","london",
"usa","united states",
"canada","toronto",
"singapore",
"japan","tokyo",
"korea","seoul"
]

SOURCES = [
"https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
"https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
"https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
"https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
"https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
"https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
"https://raw.githubusercontent.com/freefq/free/master/v2",
"https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt",
"https://raw.githubusercontent.com/ripaojiedian/freenode/main/sub",
"https://raw.githubusercontent.com/ts-sf/fly/main/v2"
]

# -------- UTILS --------

def fix_base64(data):
    missing = len(data) % 4
    if missing:
        data += "=" * (4 - missing)
    return data

# -------- FETCH --------

def fetch_sources():
    configs = []
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            text = r.text.strip()

            # decode base64 if needed
            if "vmess://" not in text and "vless://" not in text:
                try:
                    text = base64.b64decode(fix_base64(text)).decode('utf-8', errors='ignore')
                except:
                    pass

            configs += text.splitlines()
        except:
            pass

    return configs

# -------- FILTER --------

def filter_nodes(configs):
    results = []
    for cfg in configs:
        t = cfg.lower()
        if any(k in t for k in COUNTRY_KEYWORDS):
            if cfg.startswith(("vmess://","vless://","trojan://", "ss://")):
                results.append(cfg)

    # remove duplicates
    results = list(set(results))

    # limit
    results = results[:MAX_SERVERS]
    return results

# -------- SAVE --------

def save_results(nodes):
    with open("nodes.txt","w", encoding="utf-8") as f:
        for n in nodes:
            f.write(n+"\n")

    sub = base64.b64encode("\n".join(nodes).encode('utf-8')).decode('utf-8')
    with open("subscription.txt","w", encoding="utf-8") as f:
        f.write(sub)

# -------- MAIN --------

def main():
    print("Fetching sources...")
    configs = fetch_sources()
    print("Total configs:", len(configs))

    nodes = filter_nodes(configs)
    print("Filtered nodes:", len(nodes))

    if not nodes:
        print("No nodes found.")
        return

    save_results(nodes)
    print("Files successfully generated: nodes.txt, subscription.txt")

if __name__ == "__main__":
    main()
