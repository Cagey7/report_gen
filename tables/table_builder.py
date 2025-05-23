class TradeTableBuilder:
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
        if previous is None or previous == 0:
            return None
        return (current / previous - 1) * 100
        

    def build_dict_data(self, gen_type, base_year_row, target_year_data, base_year_sum, target_year_sum):
        tn_ved_name = base_year_row["tn_ved_name"]
        tn_ved_code = base_year_row["tn_ved_code"]
        base_year_tons = base_year_row[f"{gen_type}_tons"]
        base_year_units = base_year_row[f"{gen_type}_units"]
        base_year_value = base_year_row.get(f"{gen_type}_value", 0)
        measure = (base_year_row.get("tn_ved_measure") or "тонна").lower()

        target_year_row = self.find_by_tn_ved_code(target_year_data, tn_ved_code)
        
        if target_year_row and target_year_row.get(f"{gen_type}_value"):
            target_year_value = target_year_row[f"{gen_type}_value"]
            target_year_tons = target_year_row[f"{gen_type}_tons"]
            target_year_units = target_year_row[f"{gen_type}_units"]

            target_year_share = self.calc_share(target_year_value, target_year_sum)
            growth_value = self.calc_growth(base_year_value, target_year_value)
            growth_tons = self.calc_growth(base_year_tons, target_year_tons)
            growth_units = self.calc_growth(base_year_units, target_year_units) if target_year_units else None

        else:
            target_year_value = 0
            target_year_tons = 0
            target_year_share = 0
            growth_value = "new"
            growth_tons = "new"
            

        base_year_share = self.calc_share(base_year_value, base_year_sum)
        
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
            "growth_units": growth_units
        }


    def gen_dict_sum_data(self, gen_type, base_year_data, target_year_data):
        print(target_year_data)
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
        for base_year_row in sorted_base_year_data[:5]:
            new_row = self.build_dict_data(gen_type, base_year_row, target_year_data, base_year_sum, target_year_sum)
            data.append(new_row)