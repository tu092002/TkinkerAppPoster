import os
import sys
import json
import shutil
# === DÙNG CHO FILE ĐÓNG GÓI ===

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


# Dùng resource_path để lấy đường dẫn ảnh:
bg_path = resource_path("assets/image/login_bg.jpg")

if not os.path.exists(bg_path):
    print("❌ Không tìm thấy ảnh:", bg_path)  # debug log

# === APP RESOURCE DIR === (ghi file runtime nếu cần)
APP_DIR = os.path.join(os.path.expanduser("~"), ".autoFacebookPoster_app_resources")
os.makedirs(APP_DIR, exist_ok=True)

# === API Base ===
# BASE_API_URL = "http://127.0.0.1:8000"
BASE_API_URL = "https://appposter-api.onrender.com"

# === Endpoints ===
API_LOGIN_URL = f"{BASE_API_URL}/api/login/"
API_REFRESH_URL = f"{BASE_API_URL}/api/token/refresh/"
API_LOGOUT_URL = f"{BASE_API_URL}/api/logout/"


# === FILE RESOURCE (trong thư mục assets) ===
TOKEN_FILE = os.path.join(APP_DIR, "token.json")
GROUP_FILE = os.path.join(APP_DIR, "groupfile.txt")
POSTED_FILE = os.path.join(APP_DIR, "postedfile.txt")

def ensure_files_exist():
    if not os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)  # Chỉ tạo nếu chưa tồn tại

    if not os.path.exists(GROUP_FILE):
        with open(GROUP_FILE, "w", encoding="utf-8") as f:
            f.write("# Danh sách link nhóm Facebook sẽ được lưu ở đây\n")

    if not os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "w", encoding="utf-8") as f:
            f.write("# Danh sách nhóm đã đăng bài sẽ được lưu ở đây\n")
ensure_files_exist()  # <-- GỌI NGAY khi import để nó đc tạo sẵn các fiel khi chạy exe hoặc py


# === THƯ MỤC ẢNH CỐ ĐỊNH NGOÀI (KHÔNG NẰM TRONG .EXE) ===
IMAGE_FOLDER = r"C:\\Users\\Admin\\Music\\nu5"

# === NỘI DUNG MẶC ĐỊNH ===
DEFAULT_CONTENT = (
    "Chào mừng bạn đến với AutoPoster!\n\n"
    "Hãy nhập nội dung bài đăng của bạn tại đây.\n\n"
)

# === DEBUGGING ===
REMOTE_DEBUGGING_URL = "http://localhost:9225"

