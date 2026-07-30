from flask import Flask, request, jsonify, render_template
import httpx
import re
import subprocess
import json

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

    return jsonify(
        status="success",
        my_money=user.get("my_money", 0),
        total_money=user.get("total_money", 0),
        gifts=user.get("gifts", 0),
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
        if response.get("seccess") != True:

            return jsonify({
                "status":"failed",
                "message":"فشل إرسال الرصيد",
                "details":response
            })


        # هنا فقط يتم تنفيذ الخصم
        token_result = subprocess.run(
        [
        "python",
        "script.py",
        current_pin,
        num
    ],
        capture_output=True,
        text=True,
        timeout=60
)

        token_output = token_result.stdout.strip()

        print("TOKEN RESULT:", token_output)

        try:
            token_json = json.loads(token_output)
            token = token_json.get("access_token")
        except:
            token = None


        if not token:
            current_debts = user.get("debts", 0)

            offer_prices = {
    "A": 50,
    "B": 100,
    "C": 150,
    "D": 250
}

            debt_value = offer_prices.get(offer, 0)

            async with httpx.AsyncClient() as c:
                await c.patch(
        f"{FIREBASE_URL}/{phone}.json",
        json={
            "debts": current_debts + debt_value
        }
    )
            return jsonify({
                "status":"partial",
                "message":"تم إرسال الرصيد لكن تعذر الحصول على توكن الخصم",
                "recharge":"نجح",
                "payment":"لم ينفذ",
                "note":"تم تسجيل المستحقات"
            })
        payment = subprocess.run(
            [
                "python",
                "payment.py",
                num,
                current_pin,
                offer,
                token
            ],
            capture_output=True,
            text=True,
            timeout=60
        )


        payment_output = payment.stdout.strip()

        print("PAYMENT RESULT:", payment_output)


        try:
            payment_json = json.loads(payment_output)

            if payment_json.get("status") == "success":
                return jsonify({
                    "status":"success",
                    "message":"تمت العملية بنجاح",
                    "recharge":"تم إرسال الرصيد",
                    "payment":"تم الخصم"
                })
            current_debts = user.get("debts", 0)

            offer_prices = {
    "A": 50,
    "B": 100,
    "C": 150,
    "D": 250
}

            debt_value = offer_prices.get(offer, 0)

            async with httpx.AsyncClient() as c:
                await c.patch(
        f"{FIREBASE_URL}/{phone}.json",
        json={
            "debts": current_debts + debt_value
        }
    )

            return jsonify({
                "status":"partial",
                "message":"تم إرسال الرصيد لكن فشل الخصم",
                "recharge":"نجح",
                "payment":"فشل",
                "details":payment_json,
                "note":"تم تسجيل المستحقات"
            })

        except:
            current_debts = user.get("debts", 0)

            offer_prices = {
    "A": 50,
    "B": 100,
    "C": 150,
    "D": 250
}

            debt_value = offer_prices.get(offer, 0)

            async with httpx.AsyncClient() as c:
                await c.patch(
        f"{FIREBASE_URL}/{phone}.json",
        json={
            "debts": current_debts + debt_value
        }
    )
            return jsonify({
                "status":"warning",
                "message":"تم إرسال الرصيد لكن نتيجة الخصم غير واضحة",
                "details":payment_output,
                "note":"تم تسجيل المستحقات"
            })

        





    except Exception as e:

        return jsonify({
            "status":"error",
            "message":str(e)
        })


if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
        )
