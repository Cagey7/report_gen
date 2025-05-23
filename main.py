import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher
from tables.table_builder import TradeTableBuilder

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
    tradeTableBuilder = TradeTableBuilder()


    countries = tradeDataFetcher.get_country_list(name_ru)
    months = tradeDataFetcher.get_max_month(region, countries, year)
    tn_veds = tradeDataFetcher.get_tn_ved_list(digit, category)

    base_year_data = tradeDataFetcher.fetch_trade_data(region, name_ru, countries, year, months, digit, tn_veds)
    target_year_data = tradeDataFetcher.fetch_trade_data(region, name_ru, countries, year-1, months, digit, tn_veds)

    import_data = tradeTableBuilder.gen_dict_sum_data("import", base_year_data, target_year_data)
    export_data = tradeTableBuilder.gen_dict_sum_data("export", base_year_data, target_year_data)
    print(export_data)
    print(import_data)
    # print(year)
    # print(f"Сумма export_value: {total_export_value:.2f}")
    # print(f"Сумма import_value: {total_import_value:.2f}")
    # print(f"TO {total_export_value + total_import_value:.2f}")

    

if __name__ == "__main__":
    main()
