import requests

INPUT_FILE = "proxies.txt"  # Your raw proxy list
OUTPUT_FILE = "working_proxies.txt"  # Filtered proxies

test_url = "https://www.amazon.com"
timeout = 5  # Timeout per request

def check_proxy(proxy):
    """Returns True if proxy works, False otherwise"""
    try:
        response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def filter_proxies():
    with open(INPUT_FILE, "r") as f:
        proxies = [line.strip() for line in f.readlines()]

    working_proxies = [proxy for proxy in proxies if check_proxy(proxy)]

    with open(OUTPUT_FILE, "w") as f:
        for proxy in working_proxies:
            f.write(proxy + "\n")

    print(f"✅ Found {len(working_proxies)} working proxies. Saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    filter_proxies()
