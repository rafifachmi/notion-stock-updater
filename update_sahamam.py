import os
import pytz
import yfinance as yf
from notion_client import Client

# --- Konfigurasi ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

def get_pages():
    """Ambil semua halaman di database Notion"""
    results = notion.databases.query(database_id=DATABASE_ID)
    return results["results"]

def update_stock_prices():
    pages = get_pages()
    for page in pages:
        kode_saham = page["properties"]["Kode Saham"]["title"][0]["text"]["content"]

        # Ambil data saham dari yfinance
        ticker = yf.Ticker(kode_saham)
        info = ticker.info
        nama = info.get("longName") or info.get("shortName") or "N/A"

        hist = ticker.history(period="1d", interval="1m")
        if hist.empty:
            print(f"⚠️ Data kosong untuk {kode_saham}, skip...")
            continue

        last_row = hist.tail(1)
        harga = last_row["Close"].iloc[0]
        waktu_update = last_row.index[0].astimezone(pytz.timezone("Asia/Jakarta"))

        # Update ke Notion
        notion.pages.update(
            page_id=page["id"],
            properties={
                "Nama Perusahaan": {"rich_text": [{"text": {"content": nama}}]},
                "Harga saat ini": {"number": float(harga)},
                "Last Update": {"date": {"start": waktu_update.isoformat()}},
            }
        )
        print(f"✅ {kode_saham} updated: {nama} - {harga} (at {waktu_update})")

if __name__ == "__main__":
    print("⏳ Update harga saham...")
    update_stock_prices()
    print("✅ Selesai.\n"
