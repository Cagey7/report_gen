import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher


def main():
    load_dotenv()

    region = os.getenv("REGION")
    name_ru = os.getenv("COUNTRY_GROUP")
    year = int(os.getenv("YEAR"))
    digit = int(os.getenv("DIGIT"))
    category = os.getenv("CATEGORY") or None

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

    tradeDataFetcher = TradeDataFetcher(conn)

    countries = tradeDataFetcher.get_country_list(name_ru)
    months = tradeDataFetcher.get_max_month(region, countries, year)
    tn_veds = tradeDataFetcher.get_tn_ved_list(digit, category)

    data = tradeDataFetcher.fetch_trade_data(region, name_ru, countries, year, months, digit, tn_veds)

    total_export_value = sum(item['export_value'] or 0.0 for item in data)
    total_import_value = sum(item['import_value'] or 0.0 for item in data)

    print(year)
    print(f"Сумма export_value: {total_export_value:.2f}")
    print(f"Сумма import_value: {total_import_value:.2f}")
    print(f"TO {total_export_value + total_import_value:.2f}")


if __name__ == "__main__":
    main()
