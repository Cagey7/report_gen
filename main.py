import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer
from table_data.preparer import TableDataPreparer
from text_data.preparer import TextDataPreparer
from context.report_context import TradeReportContext


def main():
    load_dotenv()

    region = os.getenv("REGION")
    country_or_group = os.getenv("COUNTRY_GROUP")
    year = int(os.getenv("YEAR"))
    digit = int(os.getenv("DIGIT"))
    category = os.getenv("CATEGORY") or None
    text_size = int(os.getenv("TEXT_SIZE")) or 7

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

    context = TradeReportContext(conn, region, country_or_group, year, digit, category, text_size)

    tableDataPreparer = TableDataPreparer(context)
    textDataPreparer = TextDataPreparer(context)

    # print(textDataPreparer.gen_summary_text("total"))
    # print(textDataPreparer.gen_summary_text("export"))
    # print(textDataPreparer.gen_summary_text("import"))
    print(textDataPreparer.gen_text_flow("export"))
    print(textDataPreparer.gen_text_flow("import"))

    # print(tableDataPreparer.build_main_table())


if __name__ == "__main__":
    main()
