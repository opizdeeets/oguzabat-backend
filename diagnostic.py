import subprocess
import sys

# --- Проверка наличия httpx ---
try:
    import httpx  # noqa
except ImportError:
    print("httpx не найден. Устанавливаю...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
    import httpx  # повторная попытка

# --- Остальной код диагностики ---
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

endpoints = [
    ("GET", "/applications/"),
    ("GET", "/vacancies/"),
    ("GET", "/projects/"),
    ("GET", "/companies/"),
]

for method, url in endpoints:
    try:
        response = client.request(method, url)
        print(f"{method} {url} -> {response.status_code}")
        if response.status_code != 200:
            print("Response:", response.text)
    except Exception as e:
        print(f"Ошибка при запросе {url}: {e}")
