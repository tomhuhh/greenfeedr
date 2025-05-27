import os
import io
import pandas as pd
import requests
import certifi

# ── CONFIG ──────────────────────────────────────────────────
USER         = "cornelluniv"
PASS         = "CornellGreenfeeds"
FIDS         = "453, 454, 560"  # <-- comma‑separated list of feeders
ST           = "2024-01-01_00:00:00"
ET           = "2024-03-01_00:00:00"
LOGIN_URL    = "https://portal.c-lockinc.com/api/login"
EMISSIONS_URL= "https://portal.c-lockinc.com/api/getemissions"
# ───────────────────────────────────────────────────────────

def get_token():
    r = requests.post(
        LOGIN_URL,
        data={"user": USER, "pass": PASS},
        verify=certifi.where()
    )
    r.raise_for_status()
    try:
        return r.json()["token"].strip()
    except ValueError:
        return r.text.strip()

def fetch_emissions(token: str) -> str:
    # build the URL with d=visits & your FIDS, ST, ET
    url = (
        f"{EMISSIONS_URL}"
        f"?d=visits&fids={FIDS}"
        f"&st={ST}&et={ET}"
    )
    # POST only the token in the body (exactly what this API expects)
    r = requests.post(
        url,
        data={"token": token},
        verify=certifi.where()
    )
    r.raise_for_status()
    return r.text

def parse_to_df(raw: str) -> pd.DataFrame:
    # Use pandas so that quoted commas are handled correctly
    buf = io.StringIO(raw)
    df  = pd.read_csv(
        buf,
        skiprows=2,       # drop the two header lines
        header=None,      # no built‑in header row
        names=[
            "FeederID","AnimalName","RFID","StartTime","EndTime",
            "GoodDataDuration","CO2GramsPerDay","CH4GramsPerDay",
            "O2GramsPerDay","H2GramsPerDay","H2SGramsPerDay",
            "AirflowLitersPerSec","AirflowCf","WindSpeedMetersPerSec",
            "WindDirDeg","WindCf","WasInterrupted","InterruptingTags",
            "TempPipeDegreesCelsius","IsPreliminary","RunTime"
        ],
        engine="python"    # more robust on messy CSVs
    )
    return df

def save_df(df: pd.DataFrame, save_dir: str, exp: str = None) -> str:
    os.makedirs(save_dir, exist_ok=True)
    fname = f"{exp or 'emissions'}_GFemissions.csv"
    path  = os.path.join(save_dir, fname)
    df.to_csv(path, index=False)
    print("Download complete →", path)
    return path

def main(save_dir: str = ".", exp: str = None):
    token = get_token()
    raw   = fetch_emissions(token)
    print("── RAW RESPONSE PREVIEW ──")
    print("\n".join(raw.splitlines()[:5]))   # show the first 5 lines
    print(f"...\n(total {len(raw.splitlines())} lines)\n")
    df    = parse_to_df(raw)
    return save_df(df, save_dir, exp)

if __name__ == "__main__":
    main(save_dir="data", exp="McFadden_Lab")
