import math
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.instance_path, "bmi.sqlite3")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-only-change-me")
app.config["LOGIN_USERNAME"] = os.environ.get("LOGIN_USERNAME", "admin")
app.config["LOGIN_PASSWORD_HASH"] = generate_password_hash(
    os.environ.get("LOGIN_PASSWORD", "change-me")
)


def is_authenticated():
    return "username" in session


def save_bmi_record(user_name, height, weight, bmi):
    database_path = app.config["DATABASE"]
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                height REAL NOT NULL,
                weight REAL NOT NULL,
                bmi REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO bmi_records (user_name, height, weight, bmi, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_name,
                height,
                weight,
                bmi,
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def bmi_guidance(bmi):
    if bmi < 18.5:
        return {
            "label": "體重過輕",
            "tone": "low",
            "advice": "留意是否攝取足夠且均衡的營養，規律進食並搭配適度肌力活動；若體重持續下降，建議諮詢醫師或營養師。",
        }
    if bmi < 24:
        return {
            "label": "健康體位",
            "tone": "healthy",
            "advice": "維持均衡飲食與規律運動，並持續留意睡眠及生活習慣，幫助保持健康體位。",
        }
    if bmi < 27:
        return {
            "label": "體重過重",
            "tone": "high",
            "advice": "可從減少含糖飲料、增加蔬菜與日常活動量開始，循序建立適合自己的健康習慣。",
        }
    return {
        "label": "肥胖",
        "tone": "high",
        "advice": "建議與醫師或營養師討論適合自己的飲食及運動計畫，並留意血壓、血糖等健康指標。",
    }


def parse_positive_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    username = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == app.config["LOGIN_USERNAME"] and check_password_hash(
            app.config["LOGIN_PASSWORD_HASH"], password
        ):
            session.clear()
            session["username"] = username
            return redirect(url_for("index"))
        error = "帳號或密碼錯誤，請重新輸入。"

    return render_template("login.html", error=error, username=username)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/", methods=["GET", "POST"])
def index():
    user_name = ""
    height_input = ""
    weight_input = ""
    errors = {}
    result = None

    if request.method == "POST":
        user_name = request.form.get("user_name", "").strip()
        height_input = request.form.get("height", "").strip()
        weight_input = request.form.get("weight", "").strip()
        height = parse_positive_number(height_input)
        weight = parse_positive_number(weight_input)

        if height is None:
            errors["height"] = "請輸入大於 0 的有效身高（公分）。"
        if weight is None:
            errors["weight"] = "請輸入大於 0 的有效體重（公斤）。"

        if not errors:
            height_meters = height / 100
            height_squared = height_meters * height_meters
            if not math.isfinite(height_squared) or height_squared == 0:
                errors["height"] = "無法使用這組數值計算 BMI，請檢查身高與體重。"
            else:
                bmi = weight / height_squared
                if not math.isfinite(bmi) or bmi == 0:
                    errors["weight"] = "無法使用這組數值計算 BMI，請檢查身高與體重。"
                else:
                    displayed_bmi = round(bmi, 1)
                    gauge_percent = min(max(displayed_bmi / 40 * 100, 0), 100)
                    result = {
                        "bmi": f"{displayed_bmi:.1f}",
                        "gauge_angle": -90 + gauge_percent * 1.8,
                        **bmi_guidance(displayed_bmi),
                    }
                    save_bmi_record(user_name, height, weight, displayed_bmi)

    return render_template(
        "index.html",
        logged_in=is_authenticated(),
        logged_in_username=session.get("username"),
        user_name=user_name,
        height_input=height_input,
        weight_input=weight_input,
        errors=errors,
        result=result,
    )


if __name__ == "__main__":
    app.run(debug=True)
