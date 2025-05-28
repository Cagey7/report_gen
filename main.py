import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer
from table_data.preparer import TableDataPreparer
from text_data.preparer import TextDataPreparer
from context.report_context import TradeReportContext
from report_data.preparer import TradeDataPreparer
from document_gen.generator import TradeDocumentGenerator


def main():
    load_dotenv()

    region = os.getenv("REGION")
    country_or_group = os.getenv("COUNTRY_GROUP")
    year = int(os.getenv("YEAR"))
    digit = int(os.getenv("DIGIT"))
    category = os.getenv("CATEGORY") or None
    text_size = int(os.getenv("TEXT_SIZE")) or 7
    table_size = int(os.getenv("TABLE_SIZE")) or 25

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )

    tradeDataPreparer = TradeDataPreparer(conn, region, country_or_group, year, digit, category, text_size, table_size)
    
    data_for_doc = tradeDataPreparer.prepare()
    
    tradeDocumentGenerator = TradeDocumentGenerator(data_for_doc)
    
    tradeDocumentGenerator.generate()


if __name__ == "__main__":
    main()
