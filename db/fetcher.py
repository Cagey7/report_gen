from datetime import datetime
from db.queries import (
    GET_COUNTRY_GROUPS,
    GET_COUNTRY_MEMBERS,
    GET_MAX_MONTH,
    GET_MAX_MONTH_EAEU,
    GET_MAX_MONTH_WITHOUT_EAEU,
    GET_TN_VEDS_BY_CATEGORY,
    GET_TN_VEDS_BY_DIGIT,
    FETCH_TRADE_DATA,
    FETCH_TRADE_DATA_CATEGORY
)

class TradeDataFetcher:
    def __init__(self, conn):
        self.conn = conn


    def execute_query(self, query, params=None, one=False):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone() if one else cursor.fetchall()


    def get_country_list(self, country_or_group):
        groups = [row[0] for row in self.execute_query(GET_COUNTRY_GROUPS)]

        if country_or_group in groups:
            return [row[0] for row in self.execute_query(GET_COUNTRY_MEMBERS, (country_or_group,))]
        return [country_or_group]


    def get_max_month_list(self, region, country_list, year):
        row = self.execute_query(GET_MAX_MONTH, (country_list, region, year), one=True)
        month = row[0] if row and row[0] is not None else 0
        
        if not month:
            return []

        if datetime.now().year != year:
            months = list(range(1, 13))
        elif any(item in country_list for item in self.get_country_list("страны ЕАЭС")):
            row = self.execute_query(GET_MAX_MONTH_EAEU, (region, year), one=True)
            month = row[0] if row and row[0] is not None else 0
            months = list(range(1, month+1))
        elif any(item in country_list for item in self.get_country_list("страны ДЗ")):
            row = self.execute_query(GET_MAX_MONTH_WITHOUT_EAEU, (region, year), one=True)
            month = row[0] if row and row[0] is not None else 0
            months = list(range(1, month+1))
        else:
            months = list(range(1, month+1))

        return months


    def get_tn_ved_list(self, digit=None, category=None):
        if category:
            rows = self.execute_query(GET_TN_VEDS_BY_CATEGORY, (category,))
        else:
            rows = self.execute_query(GET_TN_VEDS_BY_DIGIT, (digit,))
        return [row[0] for row in rows]


    def fetch_trade_data(self, region, country_list, months, digit, tn_veds, year_start, year_end=None, group_digit=None, use_category=False):
        if year_end is None:
            year_end = year_start

        if use_category:
            query = FETCH_TRADE_DATA_CATEGORY
            params = (
                group_digit, country_list, region,
                year_start, year_end, months, digit, tn_veds,
                group_digit, group_digit
            )
        else:
            query = FETCH_TRADE_DATA
            params = (
                country_list, region,
                year_start, year_end, months, digit, tn_veds
            )

        rows = self.execute_query(query, params)

        columns = [
            "export_tons", "export_units", "export_value",
            "import_tons", "import_units", "import_value",
            "country", "region", "tn_ved_code",
            "tn_ved_name", "tn_ved_measure", "year", "month"
        ]
        results = [dict(zip(columns, row)) for row in rows]
        return results


    def is_data_exists(self, country_or_group, region, year, months_range):
        countries = self.get_country_list(country_or_group)
        months = self.get_max_month_list(region, countries, year)
        if months == []:
            return False
        else:
            if months_range == []:
                return True
            last_db_month = months[-1]
            input_month = months_range[-1]
            if input_month > last_db_month:
                return False
            return True
