import unittest
import os
import sqlite3
import tempfile

from app import app, bmi_guidance
from werkzeug.security import generate_password_hash


class BmiAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.database_directory = tempfile.TemporaryDirectory()
        app.config["DATABASE"] = os.path.join(self.database_directory.name, "test.sqlite3")
        app.config["LOGIN_USERNAME"] = "test-user"
        app.config["LOGIN_PASSWORD_HASH"] = generate_password_hash("test-password")

    def tearDown(self):
        self.database_directory.cleanup()

    def test_initial_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("了解自己的<br><em>健康狀況。</em>", page)
        self.assertIn("計算你的 BMI", page)

    def test_login_page_accepts_valid_credentials_and_persists_session(self):
        response = self.client.post(
            "/login",
            data={"username": "test-user", "password": "test-password"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        page = self.client.get("/").get_data(as_text=True)
        self.assertIn("嗨，test-user", page)
        self.assertIn("登出", page)

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            "/login",
            data={"username": "test-user", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("帳號或密碼錯誤", response.get_data(as_text=True))

    def test_logout_clears_session(self):
        self.client.post(
            "/login",
            data={"username": "test-user", "password": "test-password"},
        )
        response = self.client.post("/logout")

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("嗨，test-user", self.client.get("/").get_data(as_text=True))

    def test_calculation_and_advice(self):
        response = self.client.post("/", data={"height": "170", "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertIn("22.5", page)
        self.assertIn("健康體位", page)
        self.assertIn("維持均衡飲食", page)

    def test_user_name_is_displayed_in_result(self):
        response = self.client.post("/", data={"user_name": "王小明", "height": "170", "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertIn("王小明 BMI 結果", page)

    def test_successful_calculation_is_saved_to_database(self):
        response = self.client.post("/", data={"user_name": "王小明", "height": "170", "weight": "65"})

        self.assertEqual(response.status_code, 200)
        connection = sqlite3.connect(app.config["DATABASE"])
        try:
            record = connection.execute(
                "SELECT user_name, height, weight, bmi FROM bmi_records"
            ).fetchone()
        finally:
            connection.close()
        self.assertEqual(record, ("王小明", 170.0, 65.0, 22.5))

    def test_taiwan_adult_thresholds(self):
        for bmi, category in [
            (18.4, "體重過輕"),
            (18.5, "健康體位"),
            (23.9, "健康體位"),
            (24.0, "體重過重"),
            (26.9, "體重過重"),
            (27.0, "肥胖"),
        ]:
            with self.subTest(bmi=bmi):
                self.assertEqual(bmi_guidance(bmi)["label"], category)

    def test_invalid_fields_do_not_produce_result(self):
        for height, weight in [("", "65"), ("0", "65"), ("abc", "65"), ("170", "-2"), ("inf", "65"), ("170", "nan"), ("1e-300", "65"), ("1e308", "65"), ("1", "1e308")]:
            with self.subTest(height=height, weight=weight):
                response = self.client.post("/", data={"height": height, "weight": weight})
                page = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn('aria-invalid="true"', page)
                self.assertNotIn("YOUR RESULT", page)

    def test_input_is_escaped(self):
        response = self.client.post("/", data={"height": '<script>alert(1)</script>', "weight": "65"})
        page = response.get_data(as_text=True)
        self.assertNotIn("<script>", page)
        self.assertIn("請輸入大於 0", page)


if __name__ == "__main__":
    unittest.main()
