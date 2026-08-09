from flask import Flask, request, jsonify, render_template
import httpx
import re
import subprocess
import urllib3
import json
from datetime import datetime, timezone

app = Flask(__name__)

FIREBASE_URL = "https://moov-befcb-default-rtdb.firebaseio.com"


def validate_phone(phone):
    return re.fullmatch(r"[234]\d{7}", str(phone)) is not None


def validate_password(password):
    return re.fullmatch(r"\d{4}", str(password)) is not None


async def authenticate(phone, password):
    if not validate_phone(phone):
        return None, (jsonify(status="error", message="رقم الهاتف غير صالح"), 400)

    if not validate_password(password):
        return None, (jsonify(status="error", message="كلمة المرور غير صالحة"), 400)

    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{FIREBASE_URL}/{phone}.json")

    if r.status_code != 200:
        return None, (jsonify(status="error", message="فشل الاتصال"), 500)

    user = r.json()

    if not user:
        return None, (jsonify(status="error", message="الحساب غير موجود"), 404)

    if str(user.get("password", "")) != password:
        return None, (jsonify(status="error", message="كلمة المرور غير صحيحة"), 401)

    return user, None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/login", methods=["POST"])
async def login():
    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()

    user, error = await authenticate(phone, password)
    if error:
        return error

    total_money = float(user.get("total_money", 0))
    my_money = float(user.get("my_money", 0))
    gifts = float(user.get("gifts", 0))

    # أموال المدير
    manager_money = max(0, total_money - my_money - gifts - 20)

    return jsonify(
        status="success",
        my_money=my_money,
        total_money=total_money,
        gifts=gifts,
        debts=manager_money,
        admin_phone=user.get("admin_phone", ""),
        admin_password=user.get("admin_password", "")
    )

@app.route("/api/withdraw", methods=["POST"])
async def withdraw():
    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()

    user, error = await authenticate(phone, password)
    if error:
        return error

    # سيتم وضع حدث السحب هنا لاحقاً

    return jsonify(
        status="success",
        message="تم التحقق بنجاح"
    )


@app.route("/api/send_gift", methods=["POST"])
async def send_gift():
    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()
    receiver = str(data.get("receiver", "")).strip()

    user, error = await authenticate(phone, password)
    if error:
        return error

    if not validate_phone(receiver):
        return jsonify(
            status="error",
            message="رقم المستلم غير صالح"
        ), 400

    # سيتم وضع حدث إرسال الهدية هنا لاحقاً

    return jsonify(
        status="success",
        message="تم التحقق بنجاح"
    )


@app.route("/execute-payment", methods=["POST"])
def execute_payment():

    try:
        data = request.get_json(silent=True) or {}
        phone = data.get("phone")
        num = data.get("num")
        current_pin = data.get("current_pin")
        offer = data.get("offer")
        token = data.get("token")

        if not phone or not num or not current_pin or not offer or not token:
            return jsonify({
                "status": "error",
                "message": "بيانات الدفع ناقصة"
            }), 400

        # ==========================
        # أولاً: تنفيذ العرض
        # ==========================
        offer_result = subprocess.run(
            [
                "python",
                "offer.py",
                str(phone),
                str(offer)
            ],
            capture_output=True,
            text=True
        )

        offer_output = offer_result.stdout.strip()

        print("OFFER OUTPUT:", offer_output)

        try:
            offer_json = json.loads(offer_output)
        except Exception:
            return jsonify({
                "status": "error",
                "message": "استجابة offer.py غير مفهومة",
                "output": offer_output
            })

        # إذا فشل العرض لا يتم الخصم
        if offer_json.get("status") != "success":
            return jsonify(offer_json)

        # ==========================
        # ثانياً: تنفيذ الخصم
        # ==========================
        payment_result = subprocess.run(
            [
                "python",
                "payment.py",
                str(num),
                str(current_pin),
                str(offer),
                str(token)
            ],
            capture_output=True,
            text=True
        )

        payment_output = payment_result.stdout.strip()

        print("PAYMENT OUTPUT:", payment_output)

        try:
            return jsonify(json.loads(payment_output))
        except Exception:
            return jsonify({
                "status": "error",
                "message": "استجابة payment.py غير مفهومة",
                "output": payment_output
            })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
@app.route("/check-token", methods=["POST"])
def check_token():
    try:
        data = request.get_json()

        pin = data.get("pin")
        num = data.get("num")

        print("PIN RECEIVED:", pin)
        print("NUM RECEIVED:", num)

        result = subprocess.run(
            ["python", "script.py", pin, num],
            capture_output=True,
            text=True
        )

        output = result.stdout.strip()

        print("SCRIPT OUTPUT:", output)

        try:
            data = json.loads(output)
        except:
            data = {}

        token = data.get("access_token")

        # ❌ لا يوجد توكن
        if not token:
            return jsonify({
                "token": None,
                "ready": False
            })

        # 🔥 فحص الجاهزية
        try:
            import base64

            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)

            decoded = json.loads(
                base64.urlsafe_b64decode(payload).decode()
            )

            scopes = decoded.get("scopes", [])

            # جاهز إذا ليس فقط pincode_check
            ready = scopes != ["pincode_check"]

        except:
            ready = False

        return jsonify({
            "token": token,
            "ready": ready
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "token": None,
            "ready": False
        })


@app.route("/api/recharge", methods=["POST"])
async def recharge():

    data = request.get_json(silent=True) or {}

    # حساب المستخدم في الموقع
    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()

    # رقم الحساب البنكي المخزن
    num = phone

    # كلمة السر البنكية المخزنة
    current_pin = password

    # رقم المستلم
    target = str(data.get("target", "")).strip()

    # العرض
    offer = str(data.get("offer", "")).strip().upper()


    # التحقق من المستخدم
    user, error = await authenticate(phone, password)

    if error:
        return error



    if int(user.get("total_money", 0)) >= 6000:
        return jsonify({
        "status": "error",
        "message": "لقد تجاوزت الحد الأقصى المسموح به (3000). يرجى تسديد مستحقاتك للمدير أولاً."
    }), 400


    if not validate_phone(target):
        return jsonify({
            "status": "error",
            "message": "رقم المستلم غير صالح"
        }),400


    if offer not in ["A","B","C","D"]:
        return jsonify({
            "status":"error",
            "message":"العرض غير صالح"
        }),400


    try:

        # تشغيل عملية الشحن
        result = subprocess.run(
            [
                "python",
                "offer.py",
                target,
                offer
            ],
            capture_output=True,
            text=True,
            timeout=60
        )


        output = result.stdout.strip()

        print("OFFER RESULT:",output)


        try:
            response = json.loads(output)

        except:
            return jsonify({
                "status":"error",
                "message":"استجابة الشحن غير مفهومة",
                "details":output
            })


        # فشل إرسال الرصيد
        if response.get("status") != "success":

            return jsonify({
                "status":"failed",
                "message":"فشل إرسال الرصيد,رصيد موف موني غير كافي",
                "details":response
            })

 
        offer_prices = {
            "A": 50,
            "B": 100,
            "C": 150,
            "D": 250
        }

        price = offer_prices.get(offer, 0)

        offer_names = {
            "A": "6GB",
            "B": "12GB",
            "C": "20GB",
            "D": "40GB"
        }

        # توقيت موريتانيا = UTC
        now = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        transaction_text = (
            f"تم إرسال الخدمة {offer_names.get(offer, offer)} "
            f"إلى المستلم {target} "
            f"بتكلفة {price} "
            f"في {now} (بتوقيت موريتانيا)"
        )

        transactions = user.get("transactions", [])

        if not isinstance(transactions, list):
            transactions = []

        transactions.append(transaction_text)

        # رسوم موف موني
        old_gifts = float(user.get("gifts", 0))

        if old_gifts == 0:
            moov_fee = 30
        else:
            moov_fee = old_gifts + 10

        async with httpx.AsyncClient() as c:
            await c.patch(
                f"{FIREBASE_URL}/{phone}.json",
                json={
                    "total_money": float(user.get("total_money", 0)) + price,
                    "my_money": float(user.get("my_money", 0)) + (price * 0.10),
                    "gifts": moov_fee,
                    "transactions": transactions
                }
            )

        return jsonify({
            "status": "success",
            "message": "تم إرسال الرصيد بنجاح",
            "recharge": "تم إرسال الرصيد",
            "payment": "تم تجاوز الخصم (معطل مؤقتًا)"
        })     





    except Exception as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        })
@app.route("/check-service")
def check_service():

    import requests

    try:

        r = requests.get(
            "https://mymoov.moov-mauritel.mr",
            timeout=5,
            verify=False
        )


        if r.status_code == 200:

            data = r.json()

            if "_links" in data:

                return jsonify({
                    "available": True
                })


        return jsonify({
            "available": False
        })


    except Exception as e:

        print("SERVICE ERROR:", e)

        return jsonify({
            "available": False
        })

if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
        )



