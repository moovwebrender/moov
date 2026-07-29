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

        num = data.get("num")
        current_pin = data.get("current_pin")
        offer = data.get("offer")
        token = data.get("token")


        if not num or not current_pin or not offer or not token:
            return jsonify({
                "status": "error",
                "message": "بيانات الدفع ناقصة"
            }), 400


        result = subprocess.run(
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


        output = result.stdout.strip()

        print("PAYMENT OUTPUT:", output)


        try:
            return jsonify(json.loads(output))

        except Exception:
            return jsonify({
                "status": "error",
                "message": "استجابة payment.py غير مفهومة",
                "output": output
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

    # حساب المصرف المستخدم للتنفيذ
    num = str(data.get("num", "")).strip()
    current_pin = str(data.get("current_pin", "")).strip()

    # العرض المختار
    offer = str(data.get("offer", "")).strip().upper()


    # التحقق من حساب المستخدم
    user, error = await authenticate(phone, password)

    if error:
        return error


    # التحقق من البيانات المطلوبة
    if not num:
        return jsonify(
            status="error",
            message="رقم حساب المصرف مطلوب"
        ), 400

    if not current_pin:
        return jsonify(
            status="error",
            message="كلمة سر المصرف مطلوبة"
        ), 400


    if offer not in ["A", "B", "C", "D"]:
        return jsonify(
            status="error",
            message="العرض غير صالح"
        ), 400


    # مؤقتاً فقط للتأكد من وصول البيانات
    return jsonify({
        "status": "success",
        "message": "تم استقبال بيانات الشحن",
        "user": phone,
        "bank": num,
        "offer": offer
    })


if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
