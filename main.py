import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher
from report_data.preparer import TradeDataPreparer
from document_gen.generator import TradeDocumentGenerator


def main():
    load_dotenv()

    region = os.getenv("REGION")
    country_or_group = os.getenv("COUNTRY_GROUP")
    end_year = int(os.getenv("END_YEAR"))
    start_year = int(os.getenv("START_YEAR") or end_year - 1)
    digit = int(os.getenv("DIGIT"))
    category = os.getenv("CATEGORY") or None
    text_size = int(os.getenv("TEXT_SIZE")) or 7
    table_size = int(os.getenv("TABLE_SIZE")) or 25
    country_table_size = int(os.getenv("COUNTRY_TABLE_SIZE")) or 15
    exclude_raw = os.getenv("EXCLUDE_TN_VEDS") or ""
    change_color = int(os.getenv("CHANGE_COLOR")) or 0
    long_report = int(os.getenv("LONG_REPORT")) or 0
    exclude_tn_veds = [item.strip() for item in exclude_raw.split(",") if item.strip()]

    month_range_raw = os.getenv("MONTH_RANGE") or ""
    parts = [int(m.strip()) for m in month_range_raw.split(",") if m.strip()]

    if len(parts) == 2:
        month_range = list(range(parts[0], parts[1] + 1))
    elif len(parts) == 1:
        month_range = [parts[0]]
    else:
        month_range = []

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

    tradeDataFetcher = TradeDataFetcher(conn)
    if not tradeDataFetcher.is_data_exists(country_or_group, region, end_year, month_range):
        exit("Данных нет")

    tradeDataPreparer = TradeDataPreparer(
        conn,
        region,
        country_or_group,
        start_year,
        end_year,
        digit,
        category,
        text_size,
        table_size,
        country_table_size,
        exclude_tn_veds,
        month_range,
        long_report,
        change_color
    )
    
    data_for_doc = tradeDataPreparer.prepare()
    
    tradeDocumentGenerator = TradeDocumentGenerator(data_for_doc)
    
    doc, filename, short_filename = tradeDocumentGenerator.generate()
    if filename == "Данных нет":
        exit(filename)
    doc.save(filename)

if __name__ == "__main__":
    main()
