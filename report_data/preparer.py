from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer
from table_data.preparer import TableDataPreparer
from text_data.preparer import TextDataPreparer
from data.region_cases import region_cases
from data.country_cases import country_cases
from data.category_descriptions import category_descriptions
from data.short_regions import short_regions
from utils.utils import *


class TradeDataPreparer:
    def __init__(self, conn, region, country_or_group, start_year, end_year, digit, category, text_size, table_size, country_table_size, exclude_tn_veds, month_range, long_report):
        self.conn = conn
        self.region = region
        self.country_or_group = country_or_group
        self.start_year = start_year
        self.end_year = end_year
        self.digit = digit
        self.category = category
        self.text_size = text_size
        self.table_size = table_size
        self.country_table_size = country_table_size
        self.exclude_tn_veds = exclude_tn_veds
        self.month_range = month_range
        self.long_report = long_report
        

    def prepare(self):
        fetcher = TradeDataFetcher(self.conn)
        transformer = TradeDataTransformer()
        tableDataPreparer = TableDataPreparer()
        textDataPreparer = TextDataPreparer()
        countries = fetcher.get_country_list(self.country_or_group)
        months = self.month_range or fetcher.get_max_month_list(self.region, countries, self.end_year)

        if self.category:
            category_text = f", {self.category}"
            tn_veds_category = fetcher.get_tn_ved_list(category=self.category)
            category_digit = len(tn_veds_category[0])
            tn_len = self.digit if self.digit in (4, 6) else category_digit
            tn_veds = list(set(code[:tn_len] for code in tn_veds_category))
            trade_data = fetcher.fetch_trade_data(
                self.region, countries, months, category_digit, tn_veds_category,
                self.start_year, self.end_year, group_digit=self.digit, use_category=True
            )
        else:
            category_text = ""
            tn_veds = fetcher.get_tn_ved_list(digit=self.digit)
            trade_data = fetcher.fetch_trade_data(
                self.region, countries, months, self.digit, tn_veds,
                self.start_year, self.end_year
            )

        trade_months_data_aggr = transformer.aggregate_by_month(trade_data, self.end_year)
        trade_year_data_aggr = transformer.aggregate_by_year(trade_data)
        trade_country_data_aggr = transformer.aggregate_by_year(trade_data, merge_countries=False)

        target_year_data = [row for row in trade_year_data_aggr if row["year"] == self.start_year]
        base_year_data = [row for row in trade_year_data_aggr if row["year"] == self.end_year]
        country_base_year_data = [row for row in trade_country_data_aggr if row["year"] == self.end_year]

        trade_country_data = transformer.aggregate_trade_data_by_country(country_base_year_data)

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
            growth_total = 0
        else:
            growth_total = ((base_total - target_total) / target_total) * 100

        total_data_sum = {
            "base_year_sum": base_total,
            "target_year_sum": target_total,
            "growth_value": growth_total
        }


        data_for_doc = {}

        period = get_year_period_str(self.start_year, self.end_year)

        data_for_doc["document_header"] = (
            f"Взаимная торговля {region_cases[self.region]['родительный']} "
            f"{s_or_so(self.country_or_group)} {country_cases[self.country_or_group]['творительный']} "
            f"за {format_month_range(months)}{period} "
            f"{'год' if months[-1] == 12 else 'года'}"
        )

        if self.category:
            data_for_doc["category_description"] = category_descriptions.get(self.category, self.category)
        
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
             self.start_year,
             self.end_year,
             months,
             total_data_sum,
             main_table_divider,
             main_table_measure
        )
        
        data_for_doc["summary_header"] = (
            f"Показатели взаимной торговли "
            f"{region_cases[self.region]['родительный']} "
            f"{s_or_so(self.country_or_group)} {country_cases[self.country_or_group]['творительный']}"
        )

        data_for_doc["summary_table"] = tableDataPreparer.build_main_table(
            self.start_year,
            self.end_year,
            months,
            export_data_sum,
            import_data_sum,
            total_data_sum,
            main_table_divider,
            main_table_measure
        )

        if self.long_report:
            data_for_doc["trade_dynamics_table"] = tableDataPreparer.build_trade_dynamics_table(trade_data, main_table_divider, main_table_measure)
            data_for_doc["months_table_data"] = tableDataPreparer.build_month_table(trade_months_data_aggr)

        if len(countries) > 1:
            country_table_units, country_table_data = tableDataPreparer.build_country_table_table(
                trade_country_data,
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
            self.start_year,
            self.end_year,
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
            self.start_year,
            self.end_year,
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
        data_for_doc["start_year"] = self.start_year
        data_for_doc["end_year"] = self.end_year
        data_for_doc["export_table_measure"] = export_table_measure
        data_for_doc["import_table_measure"] = import_table_measure
        data_for_doc["filename"] = (
            f'Справка по торговле '
            f'{region_cases[self.region]["родительный"]} '
            f'{s_or_so(self.country_or_group)} {country_cases[self.country_or_group]["творительный"]} '
            f'({format_month_range(months)}{period} '
            f'{"год" if months[-1] == 12 else "года"})'
            f'{category_text}'
            f'{", " + str(self.digit) + "-знак(ов)" if self.digit != 4 else ""}'
            f'.docx'
        )
        
        data_for_doc["short_filename"] = (
            f'{short_regions[self.region]} '
            f'- {country_cases[self.country_or_group]["именительный"][:15]} '
            f'({get_short_period(format_month_range(months))}{period} )'
            f'{" " + str(self.digit) + " зн. " if self.digit != 4 else ""}'
            f'{category_text[2:]}'
            f'.docx'
        )
        return data_for_doc
