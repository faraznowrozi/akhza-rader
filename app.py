import asyncio
import aiohttp
import pandas as pd
import time
from IPython.display import display, clear_output

# دیکشنری نمادها
akhza_portfolio = {
    "21702706902357649": "201", "50949399050647500": "211",
    "58965534586323216": "203", "36248702773456944": "212",
    "36408112396351116": "202", "67294227180710857": "204",
    "25402505872480393": "213", "16697812875985850": "210",
    "20529306741775719": "301", "45765735050842391": "405",
    "8502069339043866": "402",  "24327721111488243": "403",
    "57655849747995489": "404", "19362905444618753": "406",
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

async def fetch_ticker_data(session, ins_id, short_name):
    url_price = f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceInfo/{ins_id}"
    url_limits = f"https://cdn.tsetmc.com/api/BestLimits/{ins_id}"
    try:
        async with session.get(url_price, headers=headers, timeout=3) as res_p, \
                   session.get(url_limits, headers=headers, timeout=3) as res_l:
            closing_price = 0
            best_sell_price = 0
            if res_p.status == 200:
                data_p = await res_p.json()
                if 'closingPriceInfo' in data_p and data_p['closingPriceInfo'] is not None:
                    closing_price = data_p['closingPriceInfo'].get('pClosing', 0)
            if res_l.status == 200:
                data_l = await res_l.json()
                if 'bestLimits' in data_l and len(data_l['bestLimits']) > 0:
                    best_sell_price = data_l['bestLimits'][0].get('pMeOfr', 0)

            status = "🟢 باز" if best_sell_price > 0 else "🔴 بسته"
            return {"نماد": f"اخزا {short_name}", "وضعیت": status, "قیمت پایانی": closing_price, "قیمت سرخط فروش": best_sell_price}
    except:
        return {"نماد": f"اخزا {short_name}", "وضعیت": "⚠️ خطا", "قیمت پایانی": 0, "قیمت سرخط فروش": 0}

async def get_all_data():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_ticker_data(session, ins_id, name) for ins_id, name in akhza_portfolio.items()]
        return await asyncio.gather(*tasks)

# تابع اصلی برای نمایش استایل‌دهی شده و آپدیت خودکار زنده
async def live_dashboard():
    print("🚀 در حال راه‌اندازی رادار زنده اخزا...")
    while True:
        start_time = time.time()
        results = await get_all_data()
        df = pd.DataFrame(results)

        # پاک کردن خروجی قبلی برای جلوگیری از شلوغ شدن صفحه
        clear_output(wait=True)

        # طراحی استایل جدول (رنگ‌بندی وضعیت‌ها و راست‌چین کردن متن)
        styled_df = df.style.map(
            lambda v: 'color: green; font-weight: bold;' if v == '🟢 باز'
            else ('color: red; font-weight: bold;' if v == '🔴 بسته' else ''),
            subset=['وضعیت']
        ).set_properties(**{
            'text-align': 'right',
            'font-family': 'Vazir, Tahoma, sans-serif',
            'background-color': '#f8f9fa',
            'border': '1px solid #dee2e6'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#007bff'), ('color', 'white'), ('text-align', 'center')]}
        ])

        # نمایش عنوان و اطلاعات زمان‌سنجی
        print(f"📊 آخرین بروزرسانی: {time.strftime('%H:%M:%S')}")
        print(f"⚡ زمان پردازش همزمان: {time.time() - start_time:.2f} ثانیه")
        print("-" * 50)

        # نمایش جدول شیک شده در خروجی جپیتر
        display(styled_df)

        # توقف ۵ ثانیه‌ای قبل از بروزرسانی بعدی (داشبورد زنده)
        await asyncio.sleep(5)

# اجرای داشبورد زنده درون جپیتر
await live_dashboard()
