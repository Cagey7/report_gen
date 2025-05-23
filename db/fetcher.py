from datetime import datetime
from typing import Any, Optional, Union, List
import psycopg2.extensions
from db.queries import (
    GET_COUNTRY_GROUPS,
    GET_COUNTRY_MEMBERS,
    GET_MAX_MONTH,
    GET_MAX_MONTH_EAEU,
    GET_TN_VEDS_BY_CATEGORY,
    GET_TN_VEDS_BY_DIGIT,
    FETCH_TRADE_DATA
)

class TradeDataFetcher:
    def __init__(self, conn: psycopg2.extensions.connection):
        self.conn = conn


    def execute_query(self, query: str, params: Optional[Union[tuple, list]] = None, one: bool = False) -> Union[Any, List[Any]]:
        with self.conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone() if one else cursor.fetchall()


    def get_country_list(self, country_or_group: str) -> List[str]:
        groups = [row[0] for row in self.execute_query(GET_COUNTRY_GROUPS)]
        if country_or_group in groups:
            return [row[0] for row in self.execute_query(GET_COUNTRY_MEMBERS, (country_or_group,))]
        return [country_or_group]


    def get_max_month(self, region: str, country_list: List[str], year: int) -> List[int]:
        row = self.execute_query(GET_MAX_MONTH, (country_list, region, year), one=True)
        month = row[0] if row and row[0] is not None else 0
        
        if not month:
            return []

        if datetime.now().year != year:
            months = list(range(1, 13))
        elif len(country_list) > 1 and any(item in country_list for item in self.get_country_list("страны ЕАЭС")):
            row = self.execute_query(GET_MAX_MONTH_EAEU, (region, year), one=True)
            month = row[0] if row and row[0] is not None else 0
            months = list(range(1, month+1))
        else:
            months = list(range(1, month+1)) 

        return months


    def get_tn_ved_list(self, digit: int, category: Optional[str]) -> List[str]:
        if category:
            rows = self.execute_query(GET_TN_VEDS_BY_CATEGORY, (category, digit))
        else:
            rows = self.execute_query(GET_TN_VEDS_BY_DIGIT, (digit,))
        return [row[0] for row in rows]


    def fetch_trade_data(
        self,
        region: str,
        country: str,
        country_list: List[str],
        year: int,
        months: List[int],
        digit: int,
        tn_veds: List[str]
    ) -> List[dict]:
        params = (country, country_list, region, year, months, digit, tn_veds)
        rows = self.execute_query(FETCH_TRADE_DATA, params)

        columns = [
            "export_tons", "export_units", "export_value",
            "import_tons", "import_units", "import_value",
            "country", "region", "tn_ved_code",
            "tn_ved_name", "tn_ved_measure", "year"
        ]
        results = [dict(zip(columns, row)) for row in rows]
        return results
