import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer
from table_data.preparer import TableDataPreparer
from context.report_context import TradeReportContext


def main():
    load_dotenv()

    region = os.getenv("REGION")
    country_or_group = os.getenv("COUNTRY_GROUP")
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

    context = TradeReportContext(conn, region, country_or_group, year, digit, category)

    tableDataPreparer = TableDataPreparer(context)

    print(tableDataPreparer.build_product_table("export"))


if __name__ == "__main__":
    main()
