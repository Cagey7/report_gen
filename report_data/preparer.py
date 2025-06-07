import os
import psycopg2
from dotenv import load_dotenv
from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer
from table_data.preparer import TableDataPreparer
from text_data.preparer import TextDataPreparer
from data.region_cases import region_cases
from data.country_cases import country_cases
from utils.utils import *


class TradeDataPreparer:
    def __init__(self, conn, region, country_or_group, year, digit, category, text_size, table_size, country_table_size, exclude_tn_veds, month_range):
        self.conn = conn
        self.region = region
        self.country_or_group = country_or_group
        self.year = year
        self.digit = digit
        self.category = category
        self.text_size = text_size
        self.table_size = table_size
        self.country_table_size = country_table_size
        self.exclude_tn_veds = exclude_tn_veds
        self.month_range = month_range
        

    def prepare(self):
        fetcher = TradeDataFetcher(self.conn)
        transformer = TradeDataTransformer()
        tableDataPreparer = TableDataPreparer()
        textDataPreparer = TextDataPreparer()
        countries = fetcher.get_country_list(self.country_or_group)
            
        if self.month_range == []:
            months = fetcher.get_max_month_list(self.region, countries, self.year)
        else:
            months = self.month_range
        
        if self.category:
            category_text = f", {self.category}"
            tn_veds_category = fetcher.get_tn_ved_list(6, self.category)
            if self.digit == 4:
                tn_veds = list(set(num[:-2] for num in tn_veds_category))
            elif self.digit == 6:
                tn_veds = fetcher.get_tn_ved_list(self.digit, self.category)

            base_year_data_category = fetcher.fetch_trade_data(
                self.region,
                self.country_or_group,
                countries,
                self.year,
                months,
                6,
                tn_veds_category
            )
            target_year_data_category = fetcher.fetch_trade_data(
                self.region,
                self.country_or_group,
                countries,
                self.year - 1,
                months,
                6,
                tn_veds_category
            )

            country_trade_data_category = fetcher.fetch_country_trade_data(
                self.region,
                countries,
                self.year,
                months,
                6,
                tn_veds_category
            )

            import_data_sum_category = transformer.gen_dict_sum_data("import", base_year_data_category, target_year_data_category)
            export_data_sum_category = transformer.gen_dict_sum_data("export", base_year_data_category, target_year_data_category)

            base_total_category = export_data_sum_category["base_year_sum"] + import_data_sum_category["base_year_sum"]
            target_total_category = export_data_sum_category["target_year_sum"] + import_data_sum_category["target_year_sum"]
            growth_total_category = ((base_total_category - target_total_category) / target_total_category) * 100 if target_total_category else 0
            total_data_sum_category = {
                "base_year_sum": base_total_category,
                "target_year_sum": target_total_category,
                "growth_value": growth_total_category
            }

        else:
            tn_veds = fetcher.get_tn_ved_list(self.digit)
            category_text = ""


        base_year_data = fetcher.fetch_trade_data(
            self.region,
            self.country_or_group,
            countries,
            self.year,
            months,
            self.digit,
            tn_veds
        )
        target_year_data = fetcher.fetch_trade_data(
            self.region,
            self.country_or_group,
            countries,
            self.year - 1,
            months,
            self.digit,
            tn_veds
        )
        country_trade_data = fetcher.fetch_country_trade_data(
            self.region,
            countries,
            self.year,
            months,
            self.digit,
            tn_veds
        )

        table_data_import = transformer.get_table_data("import", base_year_data, target_year_data)
        table_data_export = transformer.get_table_data("export", base_year_data, target_year_data)
        
        table_data_import_reverse = transformer.get_table_data("import", target_year_data, base_year_data)
        table_data_export_reverse = transformer.get_table_data("export", target_year_data, base_year_data)

        import_data_sum = transformer.gen_dict_sum_data("import", base_year_data, target_year_data)
        export_data_sum = transformer.gen_dict_sum_data("export", base_year_data, target_year_data)

        base_total = export_data_sum["base_year_sum"] + import_data_sum["base_year_sum"]
        target_total = export_data_sum["target_year_sum"] + import_data_sum["target_year_sum"]

        if target_total == 0:
            growth_total = 100
        elif base_total == 0:
            growth_total == 0
        else:
            growth_total = ((base_total - target_total) / target_total) * 100 if target_total else 0
        total_data_sum = {
            "base_year_sum": base_total,
            "target_year_sum": target_total,
            "growth_value": growth_total
        }
        if self.category:
            import_data_sum = import_data_sum_category
            export_data_sum = export_data_sum_category
            base_total = base_total_category
            target_total = target_total_category
            total_data_sum = total_data_sum_category
            country_trade_data = country_trade_data_category
        data_for_doc = {}
            
        
        data_for_doc["document_header"] = (
            f"Взаимная торговля {region_cases[self.region]['родительный']} "
            f"с {country_cases[self.country_or_group]['творительный']} "
            f"за {format_month_range(months)}{self.year} "
            f"{'год' if months[-1] == 12 else 'года'}"
        )

        main_table_divider, main_table_measure = get_main_table_divider(
            [
                import_data_sum["base_year_sum"], 
                import_data_sum["target_year_sum"], 
                export_data_sum["base_year_sum"], 
                export_data_sum["target_year_sum"]
            ]
        )
        
        data_for_doc["summary_text"] = textDataPreparer.gen_summary_text(
            "total",
             self.country_or_group,
             self.region,
             self.year,
             months,
             total_data_sum,
             main_table_divider,
             main_table_measure
        )
        
        data_for_doc["summary_header"] = (
            f"Показатели взаимной торговли "
            f"{region_cases[self.region]['родительный']} "
            f"с {country_cases[self.country_or_group]['творительный']}"
        )

        data_for_doc["summary_table"] = tableDataPreparer.build_main_table(
            self.year,
            export_data_sum,
            import_data_sum,
            total_data_sum,
            main_table_divider,
            main_table_measure
        )
        
        if len(countries) > 1:
            country_table_units, country_table_data = tableDataPreparer.build_country_table_table(
                country_trade_data,
                self.country_table_size
            )
            
            data_for_doc["country_table_units"] = country_table_units
            data_for_doc["country_table_data"] = country_table_data
            data_for_doc["country_table_header"] = "Показатели внешней торговли в разрезе стран"

                    
        import_table_div, import_table_measure = get_export_import_table_divider(
            [import_data_sum["base_year_sum"],
            import_data_sum["target_year_sum"]]
        )

        export_table_div, export_table_measure = get_export_import_table_divider(
            [export_data_sum["base_year_sum"],
            export_data_sum["target_year_sum"]]
        )
        
        data_for_doc["import_table"] = tableDataPreparer.build_export_import_table(
            "import",
            import_data_sum,
            table_data_import,
            self.exclude_tn_veds,
            self.table_size,
            import_table_div
        )
        


        data_for_doc["export_table"] = tableDataPreparer.build_export_import_table(
            "export",
            export_data_sum,
            table_data_export,
            self.exclude_tn_veds,
            self.table_size,
            export_table_div
        )
        
        data_for_doc["export_header"] = (
            f"Таблица 1 – Основные товары экспорта "
            f"{region_cases[self.region]['родительный']} "
            f"в {country_cases[self.country_or_group]['винительный']}"
        )

        data_for_doc["import_header"] = (
            f"Таблица 2 – Основные товары импорта "
            f"{region_cases[self.region]['родительный']} "
            f"из {country_cases[self.country_or_group]['родительный']}"
        )
        data_for_doc["import_text"] = textDataPreparer.gen_text_flow(
            "import",
            self.year,
            months,
            table_data_import,
            table_data_import_reverse,
            import_data_sum,
            self.region,
            self.country_or_group,
            self.exclude_tn_veds,
            self.text_size,
            main_table_divider,
            main_table_measure
        )

        data_for_doc["export_text"] = textDataPreparer.gen_text_flow(
            "export",
            self.year,
            months,
            table_data_export,
            table_data_export_reverse,
            export_data_sum,
            self.region,
            self.country_or_group,
            self.exclude_tn_veds,
            self.text_size,
            main_table_divider,
            main_table_measure
        )

        data_for_doc["months"] = months
        data_for_doc["year"] = self.year
        data_for_doc["export_table_measure"] = export_table_measure
        data_for_doc["import_table_measure"] = import_table_measure
        data_for_doc["file_name"] = (
            f'Справка по торговле '
            f'{region_cases[self.region]["родительный"]} '
            f'с {country_cases[self.country_or_group]["творительный"]} '
            f'({format_month_range(months)}{self.year} '
            f'{"год" if months[-1] == 12 else "года"})'
            f'{category_text}, '
            f'{self.digit}-знак(ов).docx'
        )
        return data_for_doc
