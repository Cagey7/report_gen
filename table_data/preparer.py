from utils.utils import *

class TableDataPreparer:
    def build_main_table(self, year, export_sum, import_sum, total_sum, div, units):
        base_balance = export_sum["base_year_sum"] - import_sum["base_year_sum"]
        target_balance = export_sum["target_year_sum"] - import_sum["target_year_sum"]

        balance_status = (
            "улучшился" if base_balance > target_balance
            else "ухудшился" if base_balance < target_balance
            else "без изменений"
        )

        header = [
            f"{units} долл. США",
            f"{year}",
            f"{year}",
            f"Прирост {year - 1}/{year}"
        ]

        target_year_sum_total = smart_round(total_sum["target_year_sum"]/div)
        base_year_sum_total = smart_round(total_sum["base_year_sum"]/div)
        
        if target_year_sum_total == 0 and base_year_sum_total == 0:
            total_row = []
        else:
            if target_year_sum_total == 0:
                growth_value_total = "new"
            elif base_year_sum_total == 0:
                growth_value_total = "-100%"
            else:
                growth_value_total = total_sum["growth_value"]
                if target_year_sum_total == base_year_sum_total:
                    target_year_sum_total, base_year_sum_total = smart_pair_round(total_sum["target_year_sum"]/div, total_sum["base_year_sum"]/div)
            
            total_row = ["Товарооборот", target_year_sum_total, base_year_sum_total, format_percent(growth_value_total)]


        if export_sum["target_year_sum"] == 0 and export_sum["base_year_sum"] == 0:
            export_row = ["Экспорт", 0, 0, ""]
        else:
            target_year_sum_export = smart_round(export_sum["target_year_sum"]/div)
            base_year_sum_export = smart_round(export_sum["base_year_sum"]/div)
            if target_year_sum_export == 0:
                growth_value_export = "new"
            elif base_year_sum_export == 0:
                growth_value_export = "-100%"
            else:
                growth_value_export = export_sum["growth_value"]
            if target_year_sum_export == base_year_sum_total:
                target_year_sum_total, base_year_sum_export = smart_pair_round(export_sum["target_year_sum"]/div, export_sum["base_year_sum"]/div)
            export_row = ["Экспорт", target_year_sum_export, base_year_sum_export, format_percent(growth_value_export)]


        if import_sum["target_year_sum"] == 0 and import_sum["base_year_sum"] == 0:
            import_row = ["Импорт", 0, 0, ""]
        else:
            target_year_sum_import = smart_round(import_sum["target_year_sum"]/div)
            base_year_sum_import = smart_round(import_sum["base_year_sum"]/div)
            if target_year_sum_import == 0:
                growth_value_import = "new"
            elif base_year_sum_import == 0:
                growth_value_import = "-100%"
            else:
                growth_value_import = import_sum["growth_value"]
            if target_year_sum_import == base_year_sum_import:
                target_year_sum_total, base_year_sum_export = smart_pair_round(import_sum["target_year_sum"]/div, import_sum["base_year_sum"]/div)
            
            import_row = ["Импорт", target_year_sum_import, base_year_sum_import, format_percent(growth_value_import)]


        target_balance_data = smart_round(target_balance/div)
        base_balance_data = smart_round(base_balance/div)
        if target_balance_data == base_balance_data:
            target_year_sum_total, base_year_sum_export = smart_pair_round(target_balance/div, base_balance/div)
        balance_row = [
            "Торговый баланс",
            smart_round(target_balance/div),
            smart_round(base_balance/div),
            balance_status
        ]

        return [header, total_row, export_row, import_row, balance_row]


    def build_export_import_table(self, direction, sum_data, data, exclude_tn_veds, table_size, div):
        if direction == "import":
            gen_type_name = "импорт"
        elif direction == "export":
            gen_type_name = "экспорт"
        
        table_data = []
        sum_row = [
            f"Всего {gen_type_name}",
            "",
            smart_round(sum_data["target_year_sum"]/div),
            "100%",
            "",
            smart_round(sum_data["base_year_sum"]/div),
            "100%",
            "",
            format_percent(sum_data["growth_value"])
        ]
        
        table_data.append(sum_row)
        
        index = 1
        for row in data[:table_size]:
            if row["tn_ved_code"] in exclude_tn_veds:
                continue
            name = f"{index}. {row['tn_ved_name']} (код {row['tn_ved_code']} ТНВЭД), {row['measure']}"
            index += 1
            if row["target_year_units"]:
                target_volume = smart_round(row["target_year_units"])
            else:
                target_volume = smart_round(row["target_year_tons"])
            
            target_year_value = smart_round(row["target_year_value"]/div)
            target_year_share = format_percent(row["target_year_share"], False)
            
            if row["base_year_units"]:
                base_volume = smart_round(row["base_year_units"])
            else:
                base_volume = smart_round(row["base_year_tons"])
            
            base_year_value = smart_round(row["base_year_value"]/div)
            base_year_share = format_percent(row["base_year_share"], False)
            
            if row["growth_units"]:
                growth_volume = format_percent(row["growth_units"])
            else:
                growth_volume = format_percent(row["growth_tons"])
            if growth_volume == "100%":
                growth_volume = "new"
            
            growth_value = format_percent(row["growth_value"])
            if growth_value == "100%":
                growth_value = "new"
            row_data = [name, target_volume, target_year_value, target_year_share, base_volume, base_year_value, base_year_share, growth_volume, growth_value]
            table_data.append(row_data)
        return table_data
            