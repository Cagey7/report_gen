import pandas as pd
from utils.utils import *


class TradeDataTransformer:
    def sort_by_key(self, data, key):
        filtered_data = [x for x in data if x.get(key) is not None]
        return sorted(filtered_data, key=lambda x: x[key], reverse=True)


    def sum_by_key(self, data, key):
        return sum(x[key] for x in data if isinstance(x.get(key), (int, float)))


    def find_by_tn_ved_code(self, data, code):
        for item in data:
            if item.get("tn_ved_code") == code:
                return item
        return None


    def calc_share(self, value, total):
        if total is None or total == 0:
            return None
        return value / total * 100


    def calc_growth(self, current, previous):
        if current == 0 and previous == 0:
            return None
        elif previous is None or previous == 0:
            return 100
        elif current is None or current == 0:
            return 0
        return (current / previous - 1) * 100
        

    def build_dict_data(self, gen_type, base_year_row, target_year_data, base_year_sum, target_year_sum):
        tn_ved_name = base_year_row["tn_ved_name"]
        tn_ved_code = base_year_row["tn_ved_code"]
        base_year_tons = base_year_row[f"{gen_type}_tons"]
        base_year_units = base_year_row[f"{gen_type}_units"]
        base_year_value = base_year_row.get(f"{gen_type}_value", 0)
        measure = (base_year_row.get("tn_ved_measure") or "тонна").lower()

        target_year_row = self.find_by_tn_ved_code(target_year_data, tn_ved_code)
        
        if base_year_value == 0:
            return None

        if target_year_row and target_year_row.get(f"{gen_type}_value"):
            target_year_value = target_year_row[f"{gen_type}_value"]
            target_year_tons = target_year_row[f"{gen_type}_tons"]
            target_year_units = target_year_row[f"{gen_type}_units"]

            target_year_share = self.calc_share(target_year_value, target_year_sum)
            growth_value = self.calc_growth(base_year_value, target_year_value)
            growth_tons = self.calc_growth(base_year_tons, target_year_tons)
            growth_units = self.calc_growth(base_year_units, target_year_units)
        else:
            target_year_value = 0
            target_year_tons = 0
            target_year_share = 0
            target_year_units = 0

            growth_value = 100
            growth_tons = 100
            growth_units = 100
            

        base_year_share = self.calc_share(base_year_value, base_year_sum)
        abs_change = target_year_value - base_year_value

        if measure == "тонна" and (base_year_units != 0 or target_year_units != 0):
            target_year_units = 0
            base_year_units = 0
            growth_units = 0

        return {
            "tn_ved_name": tn_ved_name,
            "tn_ved_code": tn_ved_code,
            "measure": measure,
            "target_year_units": target_year_units,
            "target_year_tons": target_year_tons,
            "target_year_value": target_year_value,
            "target_year_share": target_year_share,
            "base_year_tons": base_year_tons,
            "base_year_units": base_year_units,
            "base_year_value": base_year_value,
            "base_year_share": base_year_share,
            "growth_value": growth_value,
            "growth_tons": growth_tons,
            "growth_units": growth_units,
            "abs_change": abs_change
        }


    def gen_dict_sum_data(self, gen_type, base_year_data, target_year_data):
        base_year_sum = self.sum_by_key(base_year_data, f"{gen_type}_value")
        target_year_sum = self.sum_by_key(target_year_data, f"{gen_type}_value")
        growth_value = self.calc_growth(base_year_sum, target_year_sum)
        
        return {
            "base_year_sum": base_year_sum,
            "target_year_sum": target_year_sum,
            "growth_value": growth_value
        }


    def get_table_data(self, gen_type, base_year_data, target_year_data):
        data = []
        sorted_base_year_data = self.sort_by_key(base_year_data, f"{gen_type}_value")

        base_year_sum = self.sum_by_key(base_year_data, f"{gen_type}_value")
        target_year_sum = self.sum_by_key(target_year_data, f"{gen_type}_value")
        for base_year_row in sorted_base_year_data:
            new_row = self.build_dict_data(gen_type, base_year_row, target_year_data, base_year_sum, target_year_sum)
            if new_row:
                data.append(new_row)

        return data


    def aggregate_by_year(self, data, merge_countries=True, group_by_region=False):
        df = pd.DataFrame(data)
        df["tn_ved_name"] = df["tn_ved_name"].fillna("")
        df["tn_ved_measure"] = df["tn_ved_measure"].fillna("")

        group_cols = []
        if merge_countries:
            if group_by_region:
                group_cols = ["region", "tn_ved_code", "year"]
            else:
                group_cols = ["tn_ved_code", "year"]
        else:
            if group_by_region:
                group_cols = ["country", "region", "tn_ved_code", "year"]
            else:
                group_cols = ["country", "tn_ved_code", "year"]

        grouped = df.groupby(group_cols, as_index=False).agg({
            "export_tons": "sum",
            "export_units": "sum",
            "export_value": "sum",
            "import_tons": "sum",
            "import_units": "sum",
            "import_value": "sum",
            "tn_ved_name": "first",
            "tn_ved_measure": "first"
        })

        return grouped.to_dict("records")


    def aggregate_by_month(self, data, target_year):
        df = pd.DataFrame(data)
        df = df[df["year"] == target_year]

        numeric_fields = [
            "export_tons", "export_units", "export_value",
            "import_tons", "import_units", "import_value"
        ]
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

        grouped = df.groupby("month", as_index=False).agg({
            "export_tons": "sum",
            "export_units": "sum",
            "export_value": "sum",
            "import_tons": "sum",
            "import_units": "sum",
            "import_value": "sum"
        })

        return grouped.to_dict("records")


    def aggregate_trade_data(self, data, by="country"):
        if by not in ["country", "region"]:
            raise ValueError("Parameter 'by' must be either 'country' or 'region'.")

        df = pd.DataFrame(data)
        df_agg = df.groupby(by, as_index=False)[
            ["export_tons", "export_units", "export_value",
             "import_tons", "import_units", "import_value"]
        ].sum()

        return df_agg.to_dict(orient="records")
