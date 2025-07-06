


import asyncio
from tkinter import *
from tkinter import filedialog
import os
import sys
import threading
import json
import random
import urllib.parse
import subprocess
from playwright.async_api import async_playwright
import requests
from tkinter import simpledialog, messagebox,filedialog
from config import DEFAULT_CONTENT, IMAGE_FOLDER, REMOTE_DEBUGGING_URL,GROUP_FILE, POSTED_FILE,GROUP_FILE
from auth import load_token, refresh_access_token, logout

class AutoPosterGUI:
    
    # def __init__(self, master,token):
    #     self.token = token

    #     self.CHUNK_SIZE = 8
    #     self.REST_SECONDS_BETWEEN_CHUNKS = 300

    #     self.master = master
    #     master.title("🚀 Auto Post Facebook Group (Playwright GUI)")

    #     self.posting_running = True
    #     self.posting_paused = False

    #     Label(master, text="📝 Nội dung bài đăng:", font=("Arial", 10, "bold")).pack()
    #     self.content_text = Text(master, height=5, width=80)
    #     self.content_text.insert(END, DEFAULT_CONTENT)
    #     self.content_text.pack()

    #     Button(master, text="📁 Ảnh: Chọn thư mục", command=self.choose_folder).pack(pady=5)
    #     self.image_folder = IMAGE_FOLDER

    #     self.choice = IntVar(value=1)
    #     Radiobutton(master, text="1. Tiếp tục", variable=self.choice, value=1).pack(anchor="w")
    #     Radiobutton(master, text="2. Đăng lại từ đầu", variable=self.choice, value=2).pack(anchor="w")

    #     button_frame = Frame(master)
    #     button_frame.pack(pady=10)

    #     Button(button_frame, text="🟢 ĐĂNG BÀI", bg="#4CAF50", fg="white", width=12, command=self.start_posting).grid(row=0, column=0, padx=5)
    #     Button(button_frame, text="🟡 TẠM DỪNG", bg="#FFC107", fg="black", width=12, command=self.pause).grid(row=0, column=1, padx=5)
    #     Button(button_frame, text="🔵 TIẾP TỤC", bg="#03A9F4", fg="white", width=12, command=self.resume).grid(row=0, column=2, padx=5)
    #     Button(button_frame, text="🔴 DỪNG", bg="#F44336", fg="white", width=12, command=self.stop).grid(row=0, column=3, padx=5)
    #     Button(button_frame, text="🔍 Tìm Nhóm Đăng", bg="#9C27B0", fg="white", width=15, command=self.open_search_dialog).grid(row=0, column=4, padx=5)
    #     Button(button_frame, text="🔓 ĐĂNG XUẤT", bg="#9E9E9E", fg="white", width=12, command=self.logout_app).grid(row=0, column=6, padx=5)

    #     self.join_button = Button(button_frame, text="👥 Tham gia các nhóm", bg="#795548", fg="white", width=15, command=self.join_groups_from_list)
    #     self.join_button.grid(row=0, column=5, padx=5)

    #     Label(master, text="📋 Kết quả", font=("Arial", 10, "bold")).pack()
    #     self.result_text = Text(master, height=15, width=100)
    #     self.result_text.pack()
    
    def __init__(self, master, token):
        self.token = token
        self.CHUNK_SIZE = 8
        self.REST_SECONDS_BETWEEN_CHUNKS = 300

        self.master = master
        master.title("🚀 Auto Post Facebook Group (Playwright GUI)")
        master.geometry("1200x700")
        master.configure(bg="#f5f7fa")

        self.posting_running = True
        self.posting_paused = False
        self.joining_running = True      # 🆕 Thêm dòng này
        self.joining_paused = False      # 🆕 Thêm dòng này


        # Sidebar trái
        self.sidebar = Frame(master, bg="#1e293b", width=200)
        self.sidebar.pack(side=LEFT, fill=Y)

        Label(self.sidebar, text="Auto Poster", bg="#1e293b", fg="white", font=("Arial", 12, "bold"), pady=15).pack()

        Button(self.sidebar, text="Đăng bài", anchor="w", padx=10, pady=5,
               bg="#1e293b", fg="white", relief=FLAT,
               activebackground="#334155", activeforeground="white",
               command=self.show_post_buttons).pack(fill=X)

        Button(self.sidebar, text="Tìm nhóm", anchor="w", padx=10, pady=5,
               bg="#1e293b", fg="white", relief=FLAT,
               activebackground="#334155", activeforeground="white",
               command=self.show_group_buttons).pack(fill=X)

        Button(self.sidebar, text="Cài đặt", anchor="w", padx=10, pady=5,
               bg="#1e293b", fg="white", relief=FLAT,
               activebackground="#334155", activeforeground="white").pack(fill=X)

        Button(self.sidebar, text="Đăng xuất", anchor="w", padx=10, pady=5,
               bg="#1e293b", fg="white", relief=FLAT,
               activebackground="#334155", activeforeground="white",
               command=self.logout_app).pack(fill=X)

        # Vùng nội dung bên phải
        self.content_area = Frame(master, bg="white")
        self.content_area.pack(side=LEFT, fill=BOTH, expand=True)

        Label(self.content_area, text="📝 Nội dung bài đăng:", font=("Arial", 10, "bold"), bg="white").pack(pady=(15, 5), anchor="w", padx=20)

        self.content_text = Text(self.content_area, height=5, width=80)
        self.content_text.insert(END, DEFAULT_CONTENT)
        self.content_text.pack(padx=20, fill=X)

        Button(self.content_area, text="📁 Ảnh: Chọn thư mục", command=self.choose_folder, bg="#1e293b", fg="white").pack(pady=5, anchor="w", padx=20)
        self.image_folder = IMAGE_FOLDER

        self.choice = IntVar(value=1)
        Radiobutton(self.content_area, text="1. Tiếp tục", variable=self.choice, value=1, bg="white").pack(anchor="w", padx=20)
        Radiobutton(self.content_area, text="2. Đăng lại từ đầu", variable=self.choice, value=2, bg="white").pack(anchor="w", padx=20)

        # Nút điều khiển
        button_frame = Frame(self.content_area, bg="white")
        button_frame.pack(pady=10, padx=20, anchor="w")

        # Nhóm nút: Đăng bài
        self.post_buttons = Frame(button_frame, bg="white")
        self.post_buttons.grid(row=0, column=0, columnspan=4, sticky="w")

        Button(self.post_buttons, text="🟢 ĐĂNG BÀI", bg="#4CAF50", fg="white", width=12, command=self.start_posting).grid(row=0, column=0, padx=5)
        Button(self.post_buttons, text="🟡 TẠM DỪNG", bg="#FFC107", fg="black", width=12, command=self.pause).grid(row=0, column=1, padx=5)
        Button(self.post_buttons, text="🔵 TIẾP TỤC", bg="#03A9F4", fg="white", width=12, command=self.resume).grid(row=0, column=2, padx=5)
        Button(self.post_buttons, text="🔴 DỪNG", bg="#F44336", fg="white", width=12, command=self.stop).grid(row=0, column=3, padx=5)

        # Nhóm nút: Tìm nhóm
        self.group_buttons = Frame(button_frame, bg="white")
        self.group_buttons.grid(row=0, column=0, columnspan=4, sticky="w")

        Button(self.group_buttons, text="🔍 Tìm Nhóm Đăng", bg="#9C27B0", fg="white", width=15, command=self.open_search_dialog).grid(row=0, column=0, padx=5)
        self.join_button = Button(self.group_buttons, text="👥 Tham gia các nhóm", bg="#795548", fg="white", width=15, command=self.join_groups_from_list)
        self.join_button.grid(row=0, column=1, padx=5)

        # Ban đầu chỉ hiện nhóm Đăng bài
        self.group_buttons.grid_remove()

        # Kết quả
        Label(self.content_area, text="📋 Kết quả", font=("Arial", 10, "bold"), bg="white").pack(pady=(10, 5), anchor="w", padx=20)
        self.result_text = Text(self.content_area, height=15, width=100)
        self.result_text.pack(padx=20, fill=BOTH, expand=True)

    def show_post_buttons(self):
        self.group_buttons.grid_remove()
        self.post_buttons.grid()

    def show_group_buttons(self):
        self.post_buttons.grid_remove()
        self.group_buttons.grid()
    
    
    

   

    
    def logout_app(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất không?"):
            logout()
            # self.master.withdraw()  # ✅ ẩn cửa sổ
            # self.master.quit()      # ✅ dừng vòng lặp GUI (mainloop), không hủy cửa sổ
            
    
            
            python = sys.executable
            script = os.path.abspath(sys.argv[0])  # file main.py

            try:
                # 👉 Khởi chạy lại chính app
                subprocess.Popen([python, script])
            except Exception as e:
                print("❌ Không thể khởi động lại app:", e)

            self.master.destroy()  # ✅ Đóng app hiện tại


    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_folder = folder

    def log(self, message):
        self.result_text.insert(END, message + "\n")
        self.result_text.see(END)

    def pause(self):
        self.posting_paused = True
        self.log("⏸️ Đã tạm dừng đăng bài.")

    def resume(self):
        self.posting_paused = False
        self.log("▶️ Tiếp tục đăng bài.")

    def stop(self):
        self.posting_running = False
        self.log("🛑 Đã yêu cầu dừng đăng bài.")

    # def start_posting(self):
    #     threading.Thread(target=lambda: asyncio.run(self.main()), daemon=True).start()
    def start_posting(self):
        # Lấy dữ liệu từ tkinter ở luồng chính
        self.group_mode = self.choice.get()
        self.post_content = self.content_text.get("1.0", END).strip()

        # Chạy phần async trong thread phụ
        threading.Thread(target=lambda: asyncio.run(self.main()), daemon=True).start()

    
    async def main(self):
        self.log("🔄 Bắt đầu đăng bài...")

        if not os.path.exists(GROUP_FILE):
            self.log(f"❌ Không tìm thấy file nhóm: {GROUP_FILE}")
            return

        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            all_links = [line.strip() for line in f if line.strip()]

        posted_links = set()
        if self.group_mode == 1:
            if os.path.exists(POSTED_FILE):
                with open(POSTED_FILE, "r", encoding="utf-8") as f:
                    posted_links = set(line.strip() for line in f if line.strip())
            group_links = [link for link in all_links if link not in posted_links]
        else:
            group_links = all_links.copy()
            if os.path.exists(POSTED_FILE):
                os.remove(POSTED_FILE)

        if not group_links:
            self.log("✅ Không còn nhóm nào cần đăng.")
            return

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(REMOTE_DEBUGGING_URL)
            context = browser.contexts[0]
            page = await context.new_page()

            for index, link in enumerate(group_links):
                if not self.posting_running:
                    self.log("🛑 Đã dừng quá trình đăng.")
                    break
                while self.posting_paused:
                    await asyncio.sleep(1)

                self.log(f"\n🚀 ({index + 1}/{len(group_links)}) Đang đăng vào nhóm: {link}")
                try:
                    await page.goto(link)
                    await page.wait_for_timeout(5000)

                    try:
                        group_name = await page.title()
                        self.log(f"📛 Tên nhóm: {group_name}")
                    except:
                        self.log("⚠️ Không lấy được tên nhóm.")

                    try:
                        await page.click("a[role='tab']:has-text('Thảo luận')")
                        await page.wait_for_timeout(2000)
                    except:
                        self.log("⚠️ Không thấy hoặc không cần chuyển tab Thảo luận.")

                    await page.click("span:has-text('Bạn viết gì đi')")
                    await page.wait_for_timeout(2000)

                    await page.keyboard.type(self.post_content)
                    await page.wait_for_timeout(1000)

                    image_files = [os.path.join(self.image_folder, f) for f in os.listdir(self.image_folder)
                                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

                    if image_files:
                        for img in image_files:
                            await page.set_input_files("input[type='file']", img)
                            await page.wait_for_timeout(1000)
                        self.log(f"🖼️ Đã tải {len(image_files)} ảnh.")
                    else:
                        self.log("📄 Không tìm thấy ảnh. Sẽ dùng nền màu.")
                        await page.evaluate("""
                            const btn = document.querySelector('div[role="button"] img[src*="Aa_square"]');
                            if (btn) btn.closest('div[role="button"]').click();
                        """)
                        await page.wait_for_timeout(2000)
                        await page.evaluate("""
                            const bgOptions = [...document.querySelectorAll('div[role="dialog"] div')].filter(d => d.style.backgroundColor || d.style.backgroundImage);
                            if (bgOptions.length > 0) bgOptions[Math.floor(Math.random() * bgOptions.length)].click();
                        """)
                        await page.wait_for_timeout(2000)

                    await page.locator("div[aria-label='Đăng']").click()
                    self.log("✅ Đã nhấn Đăng.")
                    await page.wait_for_timeout(5000)

                    with open(POSTED_FILE, "a", encoding="utf-8") as f:
                        f.write(link + "\n")

                    delay = random.randint(280, 360)
                    for remaining in range(delay, 0, -1):
                        if not self.posting_running:
                            self.log("🛑 Đã dừng trong khi đếm ngược.")
                            return
                        while self.posting_paused:
                            await asyncio.sleep(1)
                        self.result_text.delete("end-2l", "end-1l")
                        self.result_text.insert(END, f"⏳ Chờ {remaining} giây...\n")
                        self.result_text.see(END)
                        await asyncio.sleep(1)

                except Exception as e:
                    self.log(f"❌ Lỗi: {str(e)}")
                    continue

            await page.close()
            await browser.close()
            self.log("\n🎉 Hoàn tất đăng tất cả nhóm.")

    
    
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
                    if not self.joining_running:
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
                            if not self.joining_running:
                                return
                            while self.joining_paused:
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
                        if not self.posting_running:
                            return
                        while self.posting_paused:
                            await asyncio.sleep(1)

                        self.result_text.delete("end-2l", "end-1l")
                        self.result_text.insert(END, f"🕒 Nghỉ {i} giây...\n")
                        self.result_text.see(END)
                        await asyncio.sleep(1)

            await page.close()
            await browser.close()
            self.log("\n🎉 Đã hoàn thành tất cả các nhóm.")

    