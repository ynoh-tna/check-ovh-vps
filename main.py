import requests
import os
import time
from datetime import datetime

SLEEP_TIME = 120

PLAN_CODES = [
    "vps-2025-model1",
    "vps-2025-model2",
    "vps-2025-model3",
    "vps-2025-model4",
    "vps-2025-model5",
]

DC_LOCATIONS = {
    "BHS": "Beauharnois, CA",
    "YNM": "Montreal, CA",
    "SBG": "Strasbourg, FR",
    "GRA": "Gravelines, FR",
    "EU-WEST-RBX": "Roubaix, FR",
    "RBX": "Roubaix, FR",
    "WAW": "Warsaw, PL",
    "DE": "Limburg, DE",
    "EU-SOUTH-MIL": "Milan, IT",
    "SGP": "Singapore, SG",
    "SYD": "Sydney, AU",
    "UK": "London, UK",
}

# --- ANSI Colors ---
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"

# --- Status mapping (text only) ---
STATUS_TEXT = {
    "available": "OK",
    "out-of-stock": "OUT",
    "out-of-stock-preorder-allowed": "PRE",
}

# --- Status colors ---
STATUS_COLOR = {
    "available": COLOR_GREEN,
    "out-of-stock": COLOR_RED,
    "out-of-stock-preorder-allowed": COLOR_YELLOW,
}


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def format_status(status, width=8):
    """
    Align text first, then apply color.
    Prevents ANSI codes from breaking column alignment.
    """
    text = STATUS_TEXT.get(status, status.upper())
    padded = f"{text:^{width}}"
    color = STATUS_COLOR.get(status, "")
    return f"{color}{padded}{COLOR_RESET}"


def fetch_plan(plan_code):
    response = requests.get(
        "https://ca.api.ovh.com/v1/vps/order/rule/datacenter"
        f"?ovhSubsidiary=WE&planCode={plan_code}",
        timeout=5,
    )
    return response.json()["datacenters"]

print(f"OVH VPS MONITOR | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

for plan in PLAN_CODES:
    print(f"\n{plan}")
    print("-" * 80)
    print(f"{'Location':30} | {'Linux':^8} | {'Windows':^8}")
    print("-" * 80)

    try:
        datacenters = fetch_plan(plan)

        # Sort: DCs with at least one available first
        datacenters.sort(
            key=lambda d: not (
                d["linuxStatus"] == "available"
                or d["windowsStatus"] == "available"
            )
        )

        available_count = 0

        for dc in datacenters:
            dc_code = dc["datacenter"]
            location = DC_LOCATIONS.get(dc_code, dc_code)

            linux_status_raw = dc["linuxStatus"]
            win_status_raw = dc["windowsStatus"]

            linux_status = format_status(linux_status_raw)
            win_status = format_status(win_status_raw)

            if (
                linux_status_raw == "available"
                or linux_status_raw == "out-of-stock-preorder-allowed"
                # or win_status_raw == "available"
            ):
                available_count += 1

            print(f"{location:30} | {linux_status} | {win_status}")

        print("-" * 80)
        print(f"Linux Available DCs: {available_count}")
    except Exception as e:
        print(f"ERROR: {e}")
