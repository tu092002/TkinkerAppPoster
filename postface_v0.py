import asyncio
from playwright.async_api import async_playwright
import os
import time
import random
import sys

# === CẤU HÌNH ===
REMOTE_DEBUGGING_URL = "http://localhost:9225"
GROUP_FILE = "chinhoanh - Copy.txt"
POSTED_FILE = "chinhoanh - Copy (2).txt"
IMAGE_FOLDER = r"H:\My Drive\FacebookPost"
POST_CONTENT = "NUBIRA CHẠY CỰC NGON, GIÁ CHỈ 23 TRIỆU, ĐĂNG KIỂM CÒN, XE Ở SAIGON, LIÊN HỆ 0936401783"

print(f"\n📂 Đang chạy file Python: {os.path.basename(__file__)}")

print("\n🔰 Chọn chế độ:")
print("1. Tiếp tục đăng từ nhóm chưa đăng")
print("2. Đăng lại từ đầu (xóa file đã đăng)")
choice = input("Nhập 1 hoặc 2: ").strip()

if choice == "2":
    if os.path.exists(POSTED_FILE):
        os.remove(POSTED_FILE)
        print("🗑️ Đã xóa file nhóm đã đăng, sẽ đăng lại từ đầu.")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(REMOTE_DEBUGGING_URL)
        context = browser.contexts[0]
        page = await context.new_page()

        if not os.path.exists(GROUP_FILE):
            print(f"❌ Không tìm thấy file {GROUP_FILE}")
            return

        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            group_links = [line.strip() for line in f if line.strip()]

        posted_links = []
        if os.path.exists(POSTED_FILE):
            with open(POSTED_FILE, "r", encoding="utf-8") as f:
                posted_links = [line.strip() for line in f if line.strip()]

        print(f"\n📋 Tổng nhóm: {len(group_links)} | Đã đăng: {len(posted_links)}")

        for index, link in enumerate(group_links):
            if link in posted_links:
                continue

            print(f"\n🚀 ({index+1}/{len(group_links)}) Đang đăng vào nhóm: {link}")
            try:
                await page.goto(link)
                await page.wait_for_timeout(5000)

                try:
                    await page.click("a[role='tab']:has-text('Thảo luận')")
                    await page.wait_for_timeout(2000)
                except:
                    print("⚠️ Không có tab Thảo luận hoặc đã ở đúng tab.")

                try:
                    group_name = await page.title()
                    print(f"📛 Tên nhóm: {group_name}")
                except:
                    print("⚠️ Không lấy được tên nhóm.")

                await page.click("span:has-text('Bạn viết gì đi')")
                await page.wait_for_timeout(2000)

                await page.keyboard.type(POST_CONTENT)
                await page.wait_for_timeout(1000)

                image_files = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER)
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

                if image_files:
                    for img in image_files:
                        await page.set_input_files("input[type='file']", img)
                        await page.wait_for_timeout(1000)
                    print(f"🖼️ Đã tải {len(image_files)} ảnh.")
                else:
                    print("📄 Không tìm thấy ảnh. Sẽ đăng status nền màu.")
                    # Mở bảng chọn nền
                    await page.evaluate("""
                        const aaButton = document.querySelector('div[role="button"] img[src*="Aa_square"]');
                        if (aaButton) {
                            aaButton.closest('div[role="button"]').click();
                        }
                    """)
                    await page.wait_for_timeout(2000)

                    # Chọn nền ngẫu nhiên
                    await page.evaluate("""
                        const bgOptions = [...document.querySelectorAll('div[role="dialog"] div')]
                            .filter(div => div.style.backgroundColor || div.style.backgroundImage);
                        if (bgOptions.length > 0) {
                            const randomIndex = Math.floor(Math.random() * bgOptions.length);
                            bgOptions[randomIndex].click();
                        }
                    """)
                    await page.wait_for_timeout(2000)

                await page.wait_for_timeout(3000)
                await page.locator("div[aria-label='Đăng']").click()
                print("✅ Đã nhấn Đăng.")
                await page.wait_for_timeout(5000)

                with open(POSTED_FILE, "a", encoding="utf-8") as f:
                    f.write(link + "\n")

            except Exception as e:
                print(f"❌ Lỗi nhóm {link}: {e}")
                continue

            delay = random.randint(280, 360)
            print(f"⏳ Chờ {delay} giây trước khi đăng nhóm tiếp theo...")
            for remaining in range(delay, 0, -1):
                sys.stdout.write(f"\r🕒 Còn lại: {remaining} giây ")
                sys.stdout.flush()
                await asyncio.sleep(1)

        await page.close()
        await browser.close()
        print("\n🎉 Đã hoàn tất đăng bài tất cả nhóm.")

asyncio.run(main())
