import requests
import certifi

# credentials & endpoints
USER, PASS = "cornelluniv", "CornellGreenfeeds"
FID, ST, ET = "453", "2024-01-01_00:00:00", "2025-01-01_00:00:00"
LOGIN_URL = "https://portal.c-lockinc.com/api/login"
DATA_URL  = "https://portal.c-lockinc.com/api/getraw"

# 1) login and grab the token
login = requests.post(
    LOGIN_URL,
    data={"user": USER, "pass": PASS},
    verify=certifi.where()
)
login.raise_for_status()

# parse out the token (plain text or JSON)
try:
    token = login.json().get("token", "").strip()
except ValueError:
    token = login.text.strip()

if not token:
    raise RuntimeError("Login did not return a token")

# 2) build URL *with* d, fid, st, et in the query string
url = (
    f"{DATA_URL}"
    f"?d=meas&fid={FID}"
    f"&st={ST}&et={ET}"
)

# 3) POST *only* the token in the body
resp = requests.post(
    url,
    data={"token": token},
    verify=certifi.where()
)
resp.raise_for_status()

print(resp.text)
