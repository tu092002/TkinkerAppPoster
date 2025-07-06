

import asyncio
from tkinter import *
from tkinter import filedialog
import os
import threading
import json
import random
import urllib.parse
from playwright.async_api import async_playwright
import requests
from tkinter import simpledialog, messagebox,filedialog

# === CẤU HÌNH ===
REMOTE_DEBUGGING_URL = "http://localhost:9225"
GROUP_FILE = "chinhoanh - Copy.txt"
POSTED_FILE = "chinhoanh - Copy (2).txt"
IMAGE_FOLDER = r"C:\\Users\\Admin\\Music\\nu5"
DEFAULT_CONTENT = "NUBIRA CHẠY CỰC NGON, GIÁ CHỈ 23 TRIỆU, ĐĂNG KIỂM CÒN, XE Ở SAIGON, LIÊN HỆ 0936401783"
API_LOGIN_URL = "https://4e9c-42-118-190-115.ngrok-free.app/api/login/"
TOKEN_FILE = "token.json"
    

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token}, f)


def load_token() -> str | None:
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)["token"]
        except:
            return None
    return None


def request_login():
    root = Tk()
    root.withdraw()

    while True:
        username = simpledialog.askstring("Đăng nhập", "Tên đăng nhập:")
        if username is None:
            root.destroy()
            return None  # Người dùng bấm Cancel

        password = simpledialog.askstring("Mật khẩu", "Nhập mật khẩu:", show="*")
        if password is None:
            root.destroy()
            return None

        try:
            response = requests.post(API_LOGIN_URL, json={"username": username, "password": password})
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                if not token:
                    messagebox.showerror("Lỗi", "Không nhận được token từ server.")
                    continue
                save_token(token)
                messagebox.showinfo("Thành công", "Đăng nhập thành công!")
                root.destroy()
                return token
            else:
                messagebox.showerror("Thất bại", "Sai tài khoản hoặc mật khẩu.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi kết nối: {e}")



class AutoPosterGUI:
    
    def __init__(self, master,token):
        self.token = token

        self.CHUNK_SIZE = 8
        self.REST_SECONDS_BETWEEN_CHUNKS = 300

        self.master = master
        master.title("🚀 Auto Post Facebook Group (Playwright GUI)")

        self.is_running = True
        self.is_paused = False

        Label(master, text="📝 Nội dung bài đăng:", font=("Arial", 10, "bold")).pack()
        self.content_text = Text(master, height=5, width=80)
        self.content_text.insert(END, DEFAULT_CONTENT)
        self.content_text.pack()

        Button(master, text="📁 Ảnh: Chọn thư mục", command=self.choose_folder).pack(pady=5)
        self.image_folder = IMAGE_FOLDER

        self.choice = IntVar(value=1)
        Radiobutton(master, text="1. Tiếp tục", variable=self.choice, value=1).pack(anchor="w")
        Radiobutton(master, text="2. Đăng lại từ đầu", variable=self.choice, value=2).pack(anchor="w")

        button_frame = Frame(master)
        button_frame.pack(pady=10)

        Button(button_frame, text="🟢 ĐĂNG BÀI", bg="#4CAF50", fg="white", width=12, command=self.start_posting).grid(row=0, column=0, padx=5)
        Button(button_frame, text="🟡 TẠM DỪNG", bg="#FFC107", fg="black", width=12, command=self.pause).grid(row=0, column=1, padx=5)
        Button(button_frame, text="🔵 TIẾP TỤC", bg="#03A9F4", fg="white", width=12, command=self.resume).grid(row=0, column=2, padx=5)
        Button(button_frame, text="🔴 DỪNG", bg="#F44336", fg="white", width=12, command=self.stop).grid(row=0, column=3, padx=5)
        Button(button_frame, text="🔍 Tìm Nhóm Đăng", bg="#9C27B0", fg="white", width=15, command=self.open_search_dialog).grid(row=0, column=4, padx=5)

        self.join_button = Button(button_frame, text="👥 Tham gia các nhóm", bg="#795548", fg="white", width=15, command=self.join_groups_from_list)
        self.join_button.grid(row=0, column=5, padx=5)

        Label(master, text="📋 Kết quả", font=("Arial", 10, "bold")).pack()
        self.result_text = Text(master, height=15, width=100)
        self.result_text.pack()

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_folder = folder

    def log(self, message):
        self.result_text.insert(END, message + "\n")
        self.result_text.see(END)

    def pause(self):
        self.is_paused = True
        self.log("⏸️ Đã tạm dừng.")

    def resume(self):
        self.is_paused = False
        self.log("▶️ Tiếp tục.")

    def stop(self):
        self.is_running = False
        self.log("🛑 Đã yêu cầu dừng.")

    def start_posting(self):
        threading.Thread(target=lambda: asyncio.run(self.main()), daemon=True).start()

    def join_groups_from_list(self):
        self.join_button.config(state=DISABLED, text="⏳ Đang tham gia...")
        threading.Thread(target=self._join_groups_wrapper, daemon=True).start()

    def _join_groups_wrapper(self):
        asyncio.run(self._join_groups())
        self.join_button.config(state=NORMAL, text="👥 Tham gia các nhóm")

    def open_search_dialog(self):
        search_window = Toplevel(self.master)
        search_window.title("🔍 Nhập từ khóa tìm kiếm")
        search_window.geometry("+1000+50")

        Label(search_window, text="🔎 Từ khóa tìm kiếm:").pack(padx=10, pady=5)
        keyword_entry = Entry(search_window, width=40)
        keyword_entry.pack(padx=10, pady=5)

        def perform_search(mode):
            keyword = keyword_entry.get().strip()
            if keyword:
                threading.Thread(target=lambda: asyncio.run(self.search_facebook(keyword, mode)), daemon=True).start()

        Button(search_window, text="➕ Tìm kiếm & Thêm vào danh sách nhóm", bg="#4CAF50", fg="white", command=lambda: perform_search("append")).pack(pady=5)
        Button(search_window, text="🆕 Tìm kiếm Tạo danh sách nhóm mới", bg="#F44336", fg="white", command=lambda: perform_search("overwrite")).pack(pady=5)

    async def search_facebook(self, keyword, mode="append"):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(REMOTE_DEBUGGING_URL)
                context = browser.contexts[0]
                page = await context.new_page()

                encoded_keyword = urllib.parse.quote(keyword)
                search_url = f"https://www.facebook.com/search/groups?q={encoded_keyword}"
                await page.goto(search_url, timeout=60000)

                self.log(f"🔍 Đã tìm nhóm với từ khóa: {keyword}")
                await page.wait_for_timeout(3000)

                for _ in range(10):
                    await page.mouse.wheel(0, 10000)
                    await asyncio.sleep(2)

                hrefs = await page.eval_on_selector_all("a[href]", "elements => elements.map(e => e.href)")
                group_links = [
                    href for href in hrefs
                    if href.startswith("http") and "group" in href and "?__tn__=%3C" not in href and "/search/groups/" not in href
                ]

                unique_links = list(set(group_links))

                existing_links = set()
                if os.path.exists(GROUP_FILE) and mode == "append":
                    with open(GROUP_FILE, "r", encoding="utf-8") as f:
                        existing_links = set(line.strip() for line in f if line.strip())

                new_links = [link for link in unique_links if link not in existing_links]

                if new_links:
                    write_mode = "a" if mode == "append" else "w"
                    with open(GROUP_FILE, write_mode, encoding="utf-8") as f:
                        for link in new_links:
                            f.write(link + "\n")
                    action = "Thêm" if mode == "append" else "Ghi đè"
                    self.log(f"✅ {action} {len(new_links)} nhóm mới vào {GROUP_FILE}")
                else:
                    self.log("⚠️ Không có nhóm mới nào cần ghi (đã có trong file).")

        except Exception as e:
            self.log(f"❌ Lỗi khi tìm kiếm: {str(e)}")

    def chunk_groups(self, groups, size):
        for i in range(0, len(groups), size):
            yield groups[i:i + size]

    async def _join_groups(self):
        self.log("🔄 Bắt đầu tham gia các nhóm trong danh sách...")

        if not os.path.exists(GROUP_FILE):
            self.log(f"❌ Không tìm thấy file nhóm: {GROUP_FILE}")
            return

        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            all_groups = [line.strip() for line in f if line.strip()]

        if not all_groups:
            self.log("⚠️ Danh sách nhóm trống.")
            return

        chunks = list(self.chunk_groups(all_groups, self.CHUNK_SIZE))
        total_chunks = len(chunks)

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(REMOTE_DEBUGGING_URL)
            context = browser.contexts[0]
            page = await context.new_page()

            for chunk_index, chunk in enumerate(chunks):
                self.log(f"\n🔷 Đợt {chunk_index + 1}/{total_chunks} — Tổng {len(chunk)} nhóm")

                for index, link in enumerate(chunk):
                    if not self.is_running:
                        self.log("🛑 Đã dừng quá trình tham gia nhóm.")
                        return

                    self.log(f"\n➡️ ({index + 1}/{len(chunk)}) Nhóm: {link}")
                    try:
                        await page.goto(link, timeout=60000)
                        await page.wait_for_timeout(5000)

                        # 👉 Nếu phát hiện popup "Đóng", bỏ qua nhóm này
                        try:
                            close_btn = page.locator('[aria-label="Đóng"]')
                            if await close_btn.count() > 0:
                                self.log("❗ Phát hiện popup — bỏ qua nhóm này.")
                                continue
                        except Exception as e:
                            self.log(f"⚠️ Lỗi khi kiểm tra popup: {e}")

                        # Kiểm tra nút tham gia
                        joined = False
                        join_button = page.locator("span", has_text="Tham gia nhóm")
                        if await join_button.count() > 0:
                            try:
                                await join_button.first.click()
                                self.log("✅ Đã gửi yêu cầu tham gia.")
                                joined = True
                            except:
                                self.log("⚠️ Không thể click nút 'Tham gia nhóm'. Bỏ qua nhóm này.")
                                continue
                        else:
                            self.log("❌ Không tìm thấy nút 'Tham gia nhóm'. Có thể đã tham gia. Bỏ qua nhóm này.")
                            continue

                        # Mô phỏng hành vi
                        has_liked = False
                        has_commented = False

                        actions = (
                            ["pause"] * 3 +
                            ["scroll_down"] * 3 +
                            ["scroll_up"] * 2 +
                            (["pause_and_like"] if not has_liked else []) +
                            (["pause_and_comment"] if not has_commented else []) +
                            ["nothing"] * 2
                        )

                        random.shuffle(actions)
                        action_count = random.randint(10, 18)

                        for step in range(action_count):
                            if not self.is_running:
                                return
                            while self.is_paused:
                                await asyncio.sleep(1)

                            if not actions:
                                break
                            action = actions.pop()

                            if action == "pause":
                                pause_time = random.randint(3, 8)
                                self.log(f"⏸️ Dừng lại {pause_time}s như đang đọc bài...")
                                await asyncio.sleep(pause_time)

                            elif action == "scroll_down":
                                scroll_amount = random.randint(300, 1000)
                                self.log(f"🖱️ Cuộn xuống nhẹ {scroll_amount}px")
                                await page.mouse.wheel(0, scroll_amount)
                                await asyncio.sleep(random.randint(1, 3))

                            elif action == "scroll_up":
                                scroll_amount = random.randint(100, 500)
                                self.log(f"🖱️ Cuộn lên nhẹ {scroll_amount}px")
                                await page.mouse.wheel(0, -scroll_amount)
                                await asyncio.sleep(random.randint(1, 2))

                            elif action == "pause_and_like" and not has_liked:
                                self.log("❤️ Dừng và thử Like...")
                                await asyncio.sleep(random.randint(2, 4))
                                try:
                                    like_button = page.locator('[aria-label="Thích"]')
                                    if await like_button.count() > 0:
                                        await like_button.first.click()
                                        has_liked = True
                                        self.log("✅ Đã Like bài.")
                                except:
                                    self.log("⚠️ Không thể Like.")

                            elif action == "pause_and_comment" and not has_commented:
                                self.log("💬 Dừng và thử comment...")
                                await asyncio.sleep(random.randint(4, 6))
                                try:
                                    comment_box = page.locator('[aria-label="Viết câu trả lời..."]')
                                    if await comment_box.count() > 0:
                                        await comment_box.first.click()
                                        await asyncio.sleep(1)
                                        comment = random.choice([
                                            "Quan tâm ạ.", "Đặt cọc sao bác?", "Ủng hộ bài viết!",
                                            "Giá ổn đó.", "Cần thêm ảnh nhé."
                                        ])
                                        await comment_box.first.fill(comment)
                                        await comment_box.first.press("Enter")
                                        has_commented = True
                                        self.log(f"💬 Đã comment: {comment}")
                                except:
                                    self.log("⚠️ Không thể comment.")

                            else:
                                self.log("😐 Không làm gì trong bước này.")
                                await asyncio.sleep(random.randint(1, 3))

                            self.result_text.delete("end-2l", "end-1l")
                            self.result_text.insert(END, f"⏳ Mô phỏng hành vi ({step + 1}/{action_count})...\n")
                            self.result_text.see(END)

                        progress = int((index + 1) / len(chunk) * 100)
                        self.log(f"📊 Tiến độ đợt này: {progress}%")

                    except Exception as e:
                        self.log(f"❌ Lỗi khi tham gia nhóm: {str(e)}")
                        continue

                if chunk_index < total_chunks - 1:
                    self.log(f"\n⏸️ Nghỉ {self.REST_SECONDS_BETWEEN_CHUNKS // 60} phút trước đợt tiếp theo...")
                    for i in range(self.REST_SECONDS_BETWEEN_CHUNKS, 0, -1):
                        if not self.is_running:
                            return
                        while self.is_paused:
                            await asyncio.sleep(1)

                        self.result_text.delete("end-2l", "end-1l")
                        self.result_text.insert(END, f"🕒 Nghỉ {i} giây...\n")
                        self.result_text.see(END)
                        await asyncio.sleep(1)

            await page.close()
            await browser.close()
            self.log("\n🎉 Đã hoàn thành tất cả các nhóm.")

    
   


if __name__ == "__main__":
    token = load_token()
    if not token:
        token = request_login()

    if token:
        root = Tk()
        app = AutoPosterGUI(root, token=token)
        root.mainloop()
    # token = show_login()  # ← Đăng nhập trước
    # root = Tk()
    # app = AutoPosterGUI(root)
    # root.mainloop()

