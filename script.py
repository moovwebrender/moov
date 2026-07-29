import requests
import uuid
import json
import sys

install_id = "9e41b6d3-8ac2-4f7e-b19d-53a0c6e84f91"
session = requests.Session()

BASE_URL = "https://22201.tagpay.fr/api/client/v1"

COMMON_HEADERS = {
    "User-Agent": "Masrvi / 25.09.6713(6713); com.google.android.packageinstaller; (samsung; SM-E055F; Android; 15)",
    "Accept": "application/json, text/plain, /",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "Cookie": "PHPSESSID=js8chf66dl4qig1l6q9ti8f6b8"
}


# -----------------------
# قراءة المدخلات من Flask
# -----------------------
import sys

pin = sys.argv[1]
num = sys.argv[2] if len(sys.argv) > 2 else "0"


def get_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": "80b60e90eb4c6fafe349f03614f72047",
        "client_secret": "66c0d0406f9502121f002d936485a3ddb2ec633ff78c04f770d393941e59e311",
        "scope": [
            "pincode_check",
            "client_onboarding",
            "acceptor_search",
            "configuration",
            "sda_customer_onboarding_create",
            "sda_customer_onboarding_view"
        ]
    }

    res = session.post(f"{BASE_URL}/oauth2/token", json=payload, headers=COMMON_HEADERS)
    return res.json().get("access_token")


def get_images(token, num):
    headers = COMMON_HEADERS.copy()
    headers["authorization"] = f"Bearer {token}"
    headers["accept-language"] = "ar_MR"

    res = session.get(
        f"{BASE_URL}/keyboard/222{num}",
        params={
            "font": "DMSans-Medium",
            "width": "124",
            "fontSize": "62"
        },
        headers=headers
    )

    data = res.json()
    return data.get("images", []), data.get("id")


database = {
    0: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAL9JREFUSInt0zEOhCAQBVAMBSVH4CgeTY7mUTiCpYVhHGLhfD7JZrfYikksfCYDyB/nZs36XHLhexDJAEmkAGwiJ7YQbLIoiAXfwHYNDXYDUUoCSJIDrLtW7XtY0DUBtvN5XtCvq4XWMF0dRADdQ6z2KAoBII/AHNc38ADuJ1gY8gu1g/AXoGV5Y8Otf3v8jEA/eXANOwJd5eCySxcHCgxFikJHsdTgegguRZvCT+NBA0QjxkNIY0qDTKM+a9awbrjnrg9cY3dfAAAAAElFTkSuQmCC",
    1: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAADFJREFUSIljYBgFo4AMwPwHTYAfXcAeTYDxP5oAO7qAPH0EMFw6KjAqMCowCkYBSQAAjXhFBPlDmZUAAAAASUVORK5CYII=",
    2: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAKVJREFUSInt07ENwyAQBVAQBeWNwCiMRkbzKB7BpQuLb9zlfyzhRJHS8DuerOPOgHMzM+OUg9cBYDBgIcjAxiWAnQAAVfV3UHnXNYPhZQQRl71DFbDa6hIcQ2h903RfwBUqegf+cwhyDj3EOgKTw3Wpg10gK5RNACuvvULQ/xN1NtNRknaetdGifckl/EkbWdvQ1+Hkpve7Rt21vR/QR+k/MDPzMCdgeYvq3JSF0QAAAABJRU5ErkJggg==",
    3: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAL9JREFUSInt07sRxCAMBFAYAoeUQCmUZpfmUijBoQOGPV3mXXmOuZwdJ36B+AiFsLIyD27+3wCGApwEFWgEO3BxTXDVaNCfkAwGr9qqwJHB8P0eycPKEHQPkeE2OB5QXiFw5pAUNoU8BIrC3vkf2hi95KBtMDgUzmkNt4rsY4Pbuj+trJsUom4kzGH/CbUZtP/g0hqXLOvhFihdzlKGnDZD7iPb05aXDJ4xNw1J5yXqRPmZq9rsrIMctbUrK6/5AKkKkzmgRRuGAAAAAElFTkSuQmCC",
    4: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAHxJREFUSIntziEOgDAQRNFtKip7hB6lRyuOa+G4Bg6Lo4J0CXIHMQRDSPrlU1+k13tTagCZQkFQBg7BIwQKESFRyDtAWRnobMHpaMHfIVgIDSAeDFIFyBuDsgDoRMDpYMGrWAg3aADxAEiVQd4AysJAr9r3IAJjv4Je70kniyyNqv5M5p4AAAAASUVORK5CYII=",
    5: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAKhJREFUSInt0rENwzAMBEAaLlR6BI3i0azRMopHcGkggj5U538FEZzClb68Rk+KZiMj9wPPT5gegblIr38g34bQh7OBWASAF8Eb2K+w+LCnQlYoCujAHpEIUqAiEb5nAn+TwVtR1QobwWG20jCe9ehBfATo2dqSQatX4OGaaZt9ZFnhUmxmqFtPFwj6L6G5df3sSc/B9GBsA3j6KEdXn0kEBr3lkZFv+QBqsJl9nTuIVgAAAABJRU5ErkJggg==",
    6: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAN1JREFUSIntk7ENAyEMRYmuoLwRPAqjcRtkhIwSpBRZgxEorzjdj93xTaRTpJT8jidkf39wCFNT18oHnxeAwQoUAgJUAgnYuSbAVeHATcHJXZtQ34gtOqCXtt7XqWUIaAuyKvsXkHuQ2iWogTWAPIByDYSmV5egUQJeLmS8gUbg7jLFw2WKJ/gtgQHURH1hqfduteLCwELundnTM2guEwOUml1P7SeQ/wDMA/lI3ukAxA8nh3660oHVB7RahFsHIqoQWPwzDNsw7IttFK9Yct/BtrIQiH6Rg6s5NfVdHzZ0tl+g5INtAAAAAElFTkSuQmCC",
    7: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAHFJREFUSInt0LENgDAQQ9EgipSMwCgZjYzGKIxASYFISBkbyQQhaM7dPema75zN1ryQzs3/Q1mK9d0xwEdPcAB4gh1g0LABjAQrQCBYACYJ3Icg1veTYAgcDEEH4z4SOBjCC8Eu+ij4KFh7QR3MZru3DKTMY/3cTbi/AAAAAElFTkSuQmCC",
    8: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAMFJREFUSIntk7ERAyEMBPE4+JASKOVL40ujFEog/ID5s8h0kmYc2CHK2EA6aYeUdu36Wi9MBgdwEShAJ1CBQQDAzT2BR4O3BTIEYNALzc0QRuCRNgSmDGo6qGzC4A5A/RFk29SDFUwnPR4LILuo99os04FEC19sHZlNOQ1O1GlBJIqaBqImi8q4Ai9Nx4g0VB3kHAE4CfQIjH+DEQAO5qIv2RqUJZsAzD0yWjH2AQ/U22sI7ZNKb9995GS/+q5dYX0AQwSzElqMhjkAAAAASUVORK5CYII=",
    9: "iVBORw0KGgoAAAANSUhEUgAAAHwAAAB8AQMAAACR0Eb9AAAABlBMVEUAAAAAAAClZ7nPAAAAAXRSTlMAQObYZgAAAAlwSFlzAAAOxAAADsQBlSsOGwAAAN1JREFUSInt07kRAyEMBdD1OCCkBJVCabgTt0InpgTCDZiVvzK+8CwuAGW8PQAdx7FjxzIe2hiiXgxJ9UWQVSv/QvknT8A5QgB0D7RN1JIJRGEEHV+NB0kndiZogDIeFMecIE8wXsaeriG1FeR7qP8AJTXb5cak4vpPBkvQCHIhhQRIMkFUV7rgwUr5GcGK/aZqA4Qga2cQbeIapCTXdscMdQX5Fux1KrYBtYNtSSDNtZRYkh0EasvYXZ9iJdTJAVmfmp9gmpdpoizJlQBDWAgwprTGQTrDNOo7dvyMLzbxsSA7uYS5AAAAAElFTkSuQmCC",
}

reverse_db = {v: k for k, v in database.items()}


def extract_fast(user_images):
    results = {}
    for idx, img in enumerate(user_images):
        num = reverse_db.get(img)
        if num is not None:
            results[num] = idx
    return results


def build_password(pin, results_map):
    digits = [int(x) for x in pin]
    indices = []

    for d in digits:
        if d not in results_map:
            return None
        indices.append(results_map[d])

    return ";".join(map(str, indices))


# -----------------------
# التشغيل الرئيسي
# -----------------------
token = get_token()

if not token:
    print(json.dumps({"error": "no_token"}))
    sys.exit()

images, user_id = get_images(token, num)

if not images or not user_id:
    print(json.dumps({"error": "no_images"}))
    sys.exit()

results_map = extract_fast(images)
password_str = build_password(pin, results_map)

if not password_str:
    print(json.dumps({"error": "bad_pin"}))
    sys.exit()

payload = {
    "grant_type": "password",
    "client_id": "80b60e90eb4c6fafe349f03614f72047",
    "client_secret": "66c0d0406f9502121f002d936485a3ddb2ec633ff78c04f770d393941e59e311",
    "scope": ["pincode_check", "otp_check"],
    "username": user_id,
    "password": password_str,
    "install_id": install_id
}

res = session.post(
    f"{BASE_URL}/oauth2/token",
    json=payload,
    headers=COMMON_HEADERS
)

data3 = res.json()

# -----------------------
# أهم سطر: الإخراج لـ Flask
# -----------------------
print(json.dumps(data3))
