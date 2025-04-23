import os
import ssl
import urllib.request
import urllib.parse
import pandas as pd
from datetime import datetime

def convert_unit(unit):
    if isinstance(unit, (list, tuple)):
        return ','.join(map(str, unit))
    return str(unit)

def ensure_date_format(date):
    try:
        datetime.strptime(date, "%m/%d/%Y")
    except ValueError:
        raise ValueError(f"Date {date} is not in mm/dd/yyyy format.")
    return date

def get_gfdata_urllib(user, passw, exp=None, unit=None,
                      start_date=None, end_date=None, save_dir=None):
    if save_dir is None:
        save_dir = os.getcwd()

    unit = convert_unit(unit)
    start_date = ensure_date_format(start_date)
    end_date   = ensure_date_format(end_date)

    # common SSL context to avoid cert issues
    ctx = ssl.create_default_context()

    # 1) Login
    login_url  = "https://portal.c-lockinc.com/api/login"
    login_data = urllib.parse.urlencode({'user': user, 'pass': passw}).encode()
    login_req  = urllib.request.Request(login_url, data=login_data)
    with urllib.request.urlopen(login_req, context=ctx) as resp:
        token = resp.read().decode().strip()

    # 2) Fetch data
    # note: space → %20 already in the URL
    api_url = (
        "https://portal.c-lockinc.com/api/getemissions"
        f"?d=visits&fids={unit}"
        f"&st={start_date}&et={end_date}%2012:00:00"
    )
    # pass token in the POST body just like in the R version
    post_data = urllib.parse.urlencode({'token': token}).encode()
    data_req  = urllib.request.Request(api_url, data=post_data)
    with urllib.request.urlopen(data_req, context=ctx) as resp:
        raw = resp.read().decode()

    # 3) Parse into DataFrame
    lines = raw.splitlines()[2:]  # drop the first two header lines
    rows  = [line.split(',') for line in lines]
    cols  = [
        "FeederID","AnimalName","RFID","StartTime","EndTime","GoodDataDuration",
        "CO2GramsPerDay","CH4GramsPerDay","O2GramsPerDay","H2GramsPerDay","H2SGramsPerDay",
        "AirflowLitersPerSec","AirflowCf","WindSpeedMetersPerSec","WindDirDeg","WindCf",
        "WasInterrupted","InterruptingTags","TempPipeDegreesCelsius","IsPreliminary","RunTime"
    ]
    df = pd.DataFrame(rows, columns=cols)

    # 4) Save CSV
    os.makedirs(save_dir, exist_ok=True)
    fname = f"{exp or 'GFdata'}_GFdata.csv"
    path  = os.path.join(save_dir, fname)
    df.to_csv(path, index=False)

    print("Download complete →", path)
    return path

# Example usage:
if __name__ == "__main__":
    user       = os.getenv("API_USER")
    passw      = os.getenv("API_PASS")
    exp        = "StudyName"
    start_date = "01/01/2024"
    end_date   = datetime.today().strftime("%m/%d/%Y")
    save_dir   = "/tmp"

    unit = [304, 305]
    get_gfdata_urllib(user, passw, exp, unit, start_date, end_date, save_dir)
