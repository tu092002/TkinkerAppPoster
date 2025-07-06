import asyncio
from tkinter import *
from tkinter import filedialog
import os
import threading
import random
import sys
from playwright.async_api import async_playwright

# === CẤU HÌNH ===
REMOTE_DEBUGGING_URL = "http://localhost:9225"
GROUP_FILE = "chinhoanh - Copy.txt"
POSTED_FILE = "chinhoanh - Copy (2).txt"
IMAGE_FOLDER = r"C:\Users\Admin\Music\nu5"
DEFAULT_CONTENT = "NUBIRA CHẠY CỰC NGON, GIÁ CHỈ 23 TRIỆU, ĐĂNG KIỂM CÒN, XE Ở SAIGON, LIÊN HỆ 0936401783"

class AutoPosterGUI:
    def __init__(self, master):
        self.master = master
        master.title("🚀 Auto Post Facebook Group (Playwright GUI)")

        # Trạng thái điều khiển
        self.is_running = True
        self.is_paused = False

        # Nội dung
        Label(master, text="📝 Nội dung bài đăng:", font=("Arial", 10, "bold")).pack()
        self.content_text = Text(master, height=5, width=80)
        self.content_text.insert(END, DEFAULT_CONTENT)
        self.content_text.pack()

        # Chọn thư mục ảnh
        Button(master, text="📁 Ảnh: Chọn thư mục", command=self.choose_folder).pack(pady=5)
        self.image_folder = IMAGE_FOLDER

        # Radio chọn chế độ
        self.choice = IntVar(value=1)
        Radiobutton(master, text="1. Tiếp tục", variable=self.choice, value=1).pack(anchor="w")
        Radiobutton(master, text="2. Đăng lại từ đầu", variable=self.choice, value=2).pack(anchor="w")

        # Nút chức năng
        button_frame = Frame(master)
        button_frame.pack(pady=10)

        Button(button_frame, text="🟢 ĐĂNG BÀI", bg="#4CAF50", fg="white", width=12, command=self.start_posting).grid(row=0, column=0, padx=5)
        self.pause_button = Button(button_frame, text="🟡 TẠM DỪNG", bg="#FFC107", fg="black", width=12, command=self.pause)
        self.pause_button.grid(row=0, column=1, padx=5)
        self.resume_button = Button(button_frame, text="🔵 TIẾP TỤC", bg="#03A9F4", fg="white", width=12, command=self.resume)
        self.resume_button.grid(row=0, column=2, padx=5)
        self.stop_button = Button(button_frame, text="🔴 DỪNG", bg="#F44336", fg="white", width=12, command=self.stop)
        self.stop_button.grid(row=0, column=3, padx=5)

        # Kết quả
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

    async def main(self):
        self.log("🔄 Bắt đầu đăng bài...")
        if not os.path.exists(GROUP_FILE):
            self.log(f"❌ Không tìm thấy file nhóm: {GROUP_FILE}")
            return

        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            all_links = [line.strip() for line in f if line.strip()]

        posted_links = set()
        if self.choice.get() == 1:
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
                if not self.is_running:
                    self.log("🛑 Đã dừng quá trình đăng.")
                    break
                while self.is_paused:
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

                    await page.keyboard.type(self.content_text.get("1.0", END).strip())
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

                    # Đếm ngược giữa các bài
                    delay = random.randint(280, 360)
                    for remaining in range(delay, 0, -1):
                        if not self.is_running:
                            self.log("🛑 Đã dừng trong khi đếm ngược.")
                            return
                        while self.is_paused:
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

if __name__ == "__main__":
    root = Tk()
    app = AutoPosterGUI(root)
    root.mainloop()
