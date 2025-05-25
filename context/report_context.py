from db.fetcher import TradeDataFetcher
from data_transform.transformer import TradeDataTransformer


class TradeReportContext:
    def __init__(self, conn, region, country_or_group, year, digit, category=None):
        self.region = region
        self.country = country_or_group
        self.year = year
        self.digit = digit
        self.category = category

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
