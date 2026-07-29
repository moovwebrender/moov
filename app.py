from flask import Flask, request, jsonify, render_template
import httpx
import re

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


@app.route("/api/recharge", methods=["POST"])
async def recharge():
    data = request.get_json(silent=True) or {}

    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()
    target = str(data.get("target", "")).strip()

    user, error = await authenticate(phone, password)
    if error:
        return error

    if not validate_phone(target):
        return jsonify(
            status="error",
            message="رقم الهدف غير صالح"
        ), 400

    # سيتم وضع حدث الشحن هنا لاحقاً

    return jsonify(
        status="success",
        message="تم التحقق بنجاح"
    )


if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
