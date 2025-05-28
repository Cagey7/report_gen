import math
from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer


class TradeReportContext:
    def __init__(self, conn, region, country_or_group, year, digit, category, text_size, table_size, exclude_tn_veds):
        self.region = region
        self.country = country_or_group
        self.year = year
        self.digit = digit
        self.category = category
        self.text_size = text_size
        self.table_size = table_size
        self.exclude_tn_veds = exclude_tn_veds
        
        self.fetcher = TradeDataFetcher(conn)
        self.transformer = TradeDataTransformer()

        self.countries = self.fetcher.get_country_list(country_or_group)
        self.months = self.fetcher.get_max_month(region, self.countries, year)
        self.tn_veds = self.fetcher.get_tn_ved_list(digit, category)
        self.month = self.months[-1]

        self.base_year_data = self.fetcher.fetch_trade_data(region, country_or_group, self.countries, year, self.months, digit, self.tn_veds)
        self.target_year_data = self.fetcher.fetch_trade_data(region, country_or_group, self.countries, year - 1, self.months, digit, self.tn_veds)

        self.table_data_import = self.transformer.get_table_data("import", self.base_year_data, self.target_year_data)
        self.table_data_export = self.transformer.get_table_data("export", self.base_year_data, self.target_year_data)

        self.table_data_import_reverse = self.transformer.get_table_data("import", self.target_year_data, self.base_year_data)
        self.table_data_export_reverse = self.transformer.get_table_data("export", self.target_year_data, self.base_year_data)

        self.import_data_sum = self.transformer.gen_dict_sum_data("import", self.base_year_data, self.target_year_data)
        self.export_data_sum = self.transformer.gen_dict_sum_data("export", self.base_year_data, self.target_year_data)

        base_total = self.export_data_sum["base_year_sum"] + self.import_data_sum["base_year_sum"]
        target_total = self.export_data_sum["target_year_sum"] + self.import_data_sum["target_year_sum"]
        growth_total = ((base_total - target_total) / target_total) * 100 if target_total else 0
        self.total_data_sum = {
            "base_year_sum": base_total,
            "target_year_sum": target_total,
            "growth_value": growth_total
        }

        self.table_divider = self.get_main_table_divider()["divider"]
        self.table_measure = self.get_main_table_divider()["measure"]
        self.export_table_divider = self.get_export_import_table_divider("export")["divider"]
        self.import_table_divider = self.get_export_import_table_divider("export")["divider"]
        self.export_table_measure = self.get_export_import_table_divider("import")["measure"]
        self.import_table_measure = self.get_export_import_table_divider("import")["measure"]

    
    def get_main_table_divider(self):
        values = [
            self.export_data_sum["base_year_sum"],
            self.import_data_sum["base_year_sum"],
            self.export_data_sum["target_year_sum"],
            self.import_data_sum["target_year_sum"]
        ]
        
        max_value = max(values)
        min_value = min(values)

        if min_value == 0 or max_value / min_value < 1000:
            return self.get_divider(max_value)
        else:
            return self.get_divider(min_value) 


    def get_export_import_table_divider(self, direction):
        if direction == "export":
            values = [
                self.export_data_sum["base_year_sum"],
                self.export_data_sum["target_year_sum"]
            ]
        elif direction == "import":
            values = [
                self.import_data_sum["base_year_sum"],
                self.import_data_sum["target_year_sum"]
            ]
        max_value = max(values)
        return self.get_divider(max_value)


    def get_divider(self, num):
        if num >= 1_000_000_000:
            return {"divider": 1_000_000_000, "measure": "трлн."}
        elif num >= 1_000_000:
            return {"divider": 1_000_000, "measure": "млрд."}
        elif num >= 1_000:
            return {"divider": 1_000, "measure": "млн."}
        else:
            return {"divider": 1, "measure": "тыс."}


    def num_converter(self, num):
        if num >= 1_000_000_000:
            return num / 1_000_000_000, "трлн."
        elif num >= 1_000_000:
            return num / 1_000_000, "млрд."
        elif num >= 1_000:
            return num / 1_000, "млн."
        else:
            return num, "тыс."


    def smart_round(self, num):
        if abs(int(num)) >= 1:
            return round(num, 1)
        if num == 0:
            return 0
        order = int(math.floor(math.log10(abs(num))))
        decimals = -order
        return round(num, decimals)


    def round_percent(self, num):
        if abs(int(num)) >= 1:
            return round(num, 1)
        if num == 0:
            return 0
        order = int(math.floor(math.log10(abs(num))))
        decimals = -order
        decimals = max(decimals, 2)

        return round(num, decimals)


    def smart_pair_round(self, num1, num2):
        
        precision = 1
        while True:
            rounded1 = round(num1, precision)
            rounded2 = round(num2, precision)
            if rounded1 != rounded2 or precision >= 10:
                
                return rounded1, rounded2
            precision += 1


    def format_percent(self, value, with_sign=True):
        if with_sign and value is None:
            return "100%"
        elif not with_sign and value is None:
            return "+100%"
        rounded = self.round_percent(value)
        abs_value = abs(rounded)

        if value <= 0:
            return f"{abs_value}%" if not with_sign else f"{rounded}%"
        elif value <= 100:
            return f"{abs_value}%" if not with_sign else f"+{abs_value}%"
        else:
            growth = round(1 + value / 100, 1)
            return f"рост в {growth} р."
