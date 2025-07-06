from tkinter import Tk
from auth import load_token, refresh_access_token,custom_login_dialog
from gui import AutoPosterGUI
import requests
from config import TOKEN_FILE
import subprocess
import os
def is_token_valid(token: str) -> bool:
    try:
        resp = requests.get("https://httpbin.org/bearer", headers={"Authorization": f"Bearer {token}"})
        return resp.status_code == 200
    except:
        return False
    
# def run_app():
#     root = Tk()
#     root.withdraw()  # Ẩn cửa sổ root ban đầu

#     while True:
#         token = None
#         tokens = load_token()

#         if tokens:
#             token = tokens.get("access")
#             refresh = tokens.get("refresh")

#             if not is_token_valid(token) and refresh:
#                 token = refresh_access_token(refresh)

#         if not token:
#             token = custom_login_dialog(root)  # Truyền root

#         if not token:
#             print("❌ Đăng nhập thất bại hoặc bị hủy.")
#             break

#         try:
#             root.deiconify()  # Hiện root để chạy GUI chính
#             app = AutoPosterGUI(root, token)
#             root.mainloop()
#         except Exception as e:
#             print(f"❌ Lỗi khi chạy GUI: {e}")
#             break

#         if not os.path.exists(TOKEN_FILE):
#             continue
#         else:
#             break

def run_app():
    while True:
        root = Tk()
        root.withdraw()

        token = None
        tokens = load_token()

        if tokens:
            token = tokens.get("access")
            refresh = tokens.get("refresh")
            if not is_token_valid(token) and refresh:
                token = refresh_access_token(refresh)

        if not token:
            token = custom_login_dialog(root)

        if not token:
            print("❌ Đăng nhập thất bại hoặc bị hủy.")
            root.destroy()
            break

        try:
            root.deiconify()
            app = AutoPosterGUI(root, token)
            root.mainloop()
        except Exception as e:
            print(f"❌ Lỗi khi chạy GUI: {e}")
        finally:
            root.destroy()

        # 🔄 Quay lại màn hình đăng nhập nếu file token không tồn tại
        if not os.path.exists(TOKEN_FILE):
            continue
        else:
            break



def start_chrome_debug():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_user_data = r"C:\ChromeDebug"  # Bạn có thể chọn nơi khác nếu muốn

    # Nếu thư mục chưa có, tạo mới
    os.makedirs(chrome_user_data, exist_ok=True)

    # Khởi chạy Chrome nếu chưa chạy
    try:
        subprocess.Popen([
            chrome_path,
            f'--remote-debugging-port=9225',
            f'--user-data-dir={chrome_user_data}'
        ])
    except FileNotFoundError:
        print("❌ Không tìm thấy Chrome. Vui lòng kiểm tra lại đường dẫn.")

if __name__ == "__main__":
    start_chrome_debug()

    run_app()
