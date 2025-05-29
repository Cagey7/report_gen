import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer
from table_data.preparer import TableDataPreparer
from text_data.preparer import TextDataPreparer
from context.report_context import TradeReportContext
from data.region_cases import region_cases
from data.country_cases import country_cases
from utils.validation import format_month_range


class TradeDataPreparer:
    def __init__(self, conn, region, country_or_group, year, digit, category, text_size, table_size, exclude_tn_veds, month_range):
        self.conn = conn
        self.region = region
        self.country_or_group = country_or_group
        self.year = year
        self.digit = digit
        self.category = category
        self.text_size = text_size
        self.table_size = table_size
        self.exclude_tn_veds = exclude_tn_veds
        self.month_range = month_range
        

    def prepare(self):
        context = TradeReportContext(self.conn, self.region, self.country_or_group, self.year, self.digit, self.category, self.text_size, self.table_size, self.exclude_tn_veds, self.month_range)
        months = context.months

        tableDataPreparer = TableDataPreparer(context)
        textDataPreparer = TextDataPreparer(context)

        data_for_doc = {}
        data_for_doc["document_header"] = f"Взаимная торговля {region_cases[self.region]['родительный']} с {country_cases[self.country_or_group]['творительный']} за {format_month_range(months)}{self.year} {'год' if months[-1] == 12 else 'года'}"
        data_for_doc["summary_text"] = textDataPreparer.gen_summary_text("total")
        data_for_doc["summary_header"] = f"Показатели взаимной торговли {region_cases[self.region]['родительный']} с {country_cases[self.country_or_group]['творительный']}"
        data_for_doc["summary_table"] = tableDataPreparer.build_main_table()
        
        data_for_doc["import_table"] = tableDataPreparer.build_export_import_table("import")
        data_for_doc["export_table"] = tableDataPreparer.build_export_import_table("export")
        data_for_doc["export_header"] = f"Таблица 1 – Основные товары экспорта {region_cases[self.region]['родительный']} в {country_cases[self.country_or_group]['винительный']}"
        data_for_doc["import_header"] = f"Таблица 2 – Основные товары импорта {region_cases[self.region]['родительный']} из {country_cases[self.country_or_group]['родительный']}"

        data_for_doc["import_text"] = textDataPreparer.gen_text_flow("import")
        data_for_doc["export_text"] = textDataPreparer.gen_text_flow("export")

        data_for_doc["months"] = months
        data_for_doc["year"] = self.year
        data_for_doc["export_table_measure"] = context.export_table_measure
        data_for_doc["import_table_measure"] = context.import_table_measure
        data_for_doc["file_name"] = f'Справка по торговле {region_cases[self.region]["родительный"]} с {country_cases[self.country_or_group]["творительный"]} ({format_month_range(months)}{self.year} {"год" if months[-1] == 12 else "года"}).docx'
        return data_for_doc
