import requests, json, os
from tkinter import Tk, simpledialog, messagebox
from config import API_LOGIN_URL, API_REFRESH_URL, TOKEN_FILE, resource_path, API_LOGOUT_URL
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk  # Cần Pillow
import requests
import os

from tkinter import Toplevel, Label, Entry, Button, StringVar, Frame, CENTER
from tkinter import messagebox

def save_token(access: str, refresh: str):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access": access, "refresh": refresh}, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def refresh_access_token(refresh_token: str):
    try:
        response = requests.post(API_REFRESH_URL, json={"refresh": refresh_token})
        if response.status_code == 200:
            new_access = response.json().get("access")
            if new_access:
                save_token(new_access, refresh_token)
                return new_access
    except:
        pass
    return None


    
def logout():
    # Gọi API logout để xóa trạng thái đăng nhập trên server (nếu cần)
    tokens = load_token()
    print(f"📄 Đang tải token từ {tokens}...")
    if tokens:
        access_token = tokens.get("access")
        try:
            response = requests.post(API_LOGOUT_URL, headers={
                "Authorization": f"Bearer {access_token}"
            })
            print(f"📡 Server logout response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"⚠️ Không thể gọi API logout: {e}")

    # Xóa token local
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

def custom_login_dialog(master):
    login_success = {"token": None}

    def try_login(event=None):
        username = username_var.get()
        password = password_var.get()
        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tài khoản và mật khẩu.", parent=win)
            return

        try:
            response = requests.post(API_LOGIN_URL, json={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                print(f"📡 Đăng nhập thành công: {data}")
                access = data.get("token")
                refresh = data.get("refresh")
                if not access:
                    messagebox.showerror("Lỗi", "Không nhận được token.", parent=win)
                    return
                save_token(access, refresh or "")
                login_success["token"] = access
                messagebox.showinfo("Thành công", "Đăng nhập thành công!", parent=win)
                win.destroy()
            else:
                print(f"📡 Đăng nhập thất bại: {response.status_code} - {response.text}")
                messagebox.showerror("Thất bại", {response.text}, parent=win)
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", str(e), parent=win)

    def cancel_login():
        login_success["token"] = None
        win.destroy()

    win = Toplevel(master)
    win.title("Đăng nhập hệ thống")
    win.geometry("700x400")
    win.resizable(False, False)
    win.grab_set()

    # Căn giữa màn hình
    win.update_idletasks()
    w = 700
    h = 400
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

    # === Cấu trúc chia 2 cột: trái là ảnh, phải là form ===
    left_frame = Frame(win, width=300, height=400)
    left_frame.pack(side=LEFT, fill=Y)
    right_frame = Frame(win, bg="white", width=400, height=400)
    right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

    # === Ảnh nền mờ bên trái ===
    bg_path = resource_path("assets\image\login_bg.jpg")
    print("🖼️ Đang mở ảnh từ:", bg_path)

    if os.path.exists(bg_path):
        bg_img_raw = Image.open(bg_path).resize((300, 400)).convert("RGBA")
        bg_img_raw.putalpha(180)
        bg_img = ImageTk.PhotoImage(bg_img_raw)
        bg_label = Label(left_frame, image=bg_img)
        bg_label.image = bg_img
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Overlay chữ chào mừng
        Label(left_frame, text="WELCOME TO", fg="white", bg="#000000", font=("Segoe UI", 12, "bold")).place(x=20, y=140)
        Label(left_frame, text="PROFESIONAL", fg="white", bg="#000000", font=("Segoe UI", 26, "bold")).place(x=20, y=170)

    # === Form đăng nhập bên phải ===
    Label(right_frame, text="Welcome back,", font=("Segoe UI", 18, "bold"), bg="white").pack(pady=(40, 10))

    form_frame = Frame(right_frame, bg="white")
    form_frame.pack(pady=10)

    username_var = StringVar()
    password_var = StringVar()

    Label(form_frame, text="Username", font=("Segoe UI", 10), bg="white", anchor="w").grid(row=0, column=0, sticky="w")
    username_entry = Entry(form_frame, textvariable=username_var, width=30, font=("Segoe UI", 10))
    username_entry.grid(row=1, column=0, pady=(0, 15))

    Label(form_frame, text="Password", font=("Segoe UI", 10), bg="white", anchor="w").grid(row=2, column=0, sticky="w")
    password_entry = Entry(form_frame, textvariable=password_var, show="*", width=30, font=("Segoe UI", 10))
    password_entry.grid(row=3, column=0, pady=(0, 10))

    # Nút Đăng nhập
    Button(form_frame, text="SIGN IN", bg="#007BFF", fg="white", font=("Segoe UI", 10, "bold"),
           width=30, height=2, command=try_login).grid(row=4, column=0, pady=(10, 10))

    # Quên mật khẩu + Đăng ký
    bottom_frame = Frame(right_frame, bg="white")
    bottom_frame.pack()

    Label(bottom_frame, text="Forgot Password?", fg="blue", bg="white", font=("Segoe UI", 9)).pack()
    Label(bottom_frame, text="Don't have an account? ", bg="white", font=("Segoe UI", 9)).pack(side=LEFT)
    Label(bottom_frame, text="Create one", fg="blue", bg="white", font=("Segoe UI", 9, "underline")).pack(side=LEFT)

    # Keyboard shortcut
    username_entry.focus_set()
    win.bind("<Return>", try_login)

    win.wait_window()
    return login_success["token"]

