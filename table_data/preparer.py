from utils.utils import *

class TableDataPreparer:
    def build_main_table(self, start_year, end_year, months, export_sum, import_sum, total_sum, div, units):
        base_balance = export_sum["base_year_sum"] - import_sum["base_year_sum"]
        target_balance = export_sum["target_year_sum"] - import_sum["target_year_sum"]

        balance_status = (
            "улучшился" if base_balance > target_balance
            else "ухудшился" if base_balance < target_balance
            else "без изменений"
        )

        header = [
            f"{units} долл. США",
            f"{start_year} год" if months[-1] == 12 else f"{format_month_range(months)}\n{start_year} {'год' if months[-1] == 12 else 'года'}",
            f"{end_year} год" if months[-1] == 12 else f"{format_month_range(months)}\n{end_year} {'год' if months[-1] == 12 else 'года'}",
            f"Прирост {start_year}/{end_year}"
        ]

        target_year_sum_total = smart_round(total_sum["target_year_sum"]/div)
        base_year_sum_total = smart_round(total_sum["base_year_sum"]/div)
        
        if target_year_sum_total == 0 and base_year_sum_total == 0:
            total_row = []
        else:
            growth_value_total = total_sum["growth_value"]
            if target_year_sum_total == base_year_sum_total:
                target_year_sum_total, base_year_sum_total = smart_pair_round(total_sum["target_year_sum"]/div, total_sum["base_year_sum"]/div)
            
            total_row = ["Товарооборот", target_year_sum_total, base_year_sum_total, format_percent(growth_value_total, if_new=True)]


        if export_sum["target_year_sum"] == 0 and export_sum["base_year_sum"] == 0:
            export_row = ["Экспорт", 0, 0, ""]
        else:
            target_year_sum_export = smart_round(export_sum["target_year_sum"]/div)
            base_year_sum_export = smart_round(export_sum["base_year_sum"]/div)
            growth_value_export = export_sum["growth_value"]
            if target_year_sum_export == base_year_sum_export:
                target_year_sum_export, base_year_sum_export = smart_pair_round(export_sum["target_year_sum"]/div, export_sum["base_year_sum"]/div)
            export_row = ["Экспорт", target_year_sum_export, base_year_sum_export, format_percent(growth_value_export, if_new=True)]


        if import_sum["target_year_sum"] == 0 and import_sum["base_year_sum"] == 0:
            import_row = ["Импорт", 0, 0, ""]
        else:
            target_year_sum_import = smart_round(import_sum["target_year_sum"]/div)
            base_year_sum_import = smart_round(import_sum["base_year_sum"]/div)
            growth_value_import = import_sum["growth_value"]
            if target_year_sum_import == base_year_sum_import:
                target_year_sum_import, base_year_sum_import = smart_pair_round(import_sum["target_year_sum"]/div, import_sum["base_year_sum"]/div)
            
            import_row = ["Импорт", target_year_sum_import, base_year_sum_import, format_percent(growth_value_import, if_new=True)]


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
            format_percent(sum_data["growth_value"], if_new=True)
        ]
        
        table_data.append(sum_row)
        
        index = 1
        count = 0
        for row in data:
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
            if growth_volume == "+100%":
                growth_volume = "new"
            
            growth_value = format_percent(row["growth_value"])
            if growth_value == "100%":
                growth_value = "new"
            row_data = [name, target_volume, target_year_value, target_year_share, base_volume, base_year_value, base_year_share, growth_volume, growth_value]
            table_data.append(row_data)

            count += 1
            if count >= table_size:
                break

        return table_data
    
    
    def build_country_table_table(self, data, table_size):
        table_data = []

        for row in data:
            import_value = row.get("import_value", 0) or 0
            export_value = row.get("export_value", 0) or 0
            total = import_value + export_value
            new_row = [row.get("country", ""), total, export_value, import_value]
            table_data.append(new_row)

        sorted_data = sorted(table_data, key=lambda x: x[1], reverse=True)

        total_total = sum(row[1] or 0 for row in sorted_data)
        total_export = sum(row[2] or 0 for row in sorted_data)
        total_import = sum(row[3] or 0 for row in sorted_data)
        total_total_others = sum(row[1] or 0 for row in sorted_data[table_size:])
        total_export_others = sum(row[2] or 0 for row in sorted_data[table_size:])
        total_import_others = sum(row[3] or 0 for row in sorted_data[table_size:])

        total_row = ["Всего", total_total, total_export, total_import]
        total_row_others = ["Остальные страны", total_total_others, total_export_others, total_import_others]

        table_data_values = [total_row] + sorted_data[:table_size]
        if total_total_others != 0:
            table_data_values.append(total_row_others)

        div, units = get_divider(total_total / 1000)

        final_table_data = []
        for i, row in enumerate(table_data_values):
            if i == 0:
                new_row = [
                    "",
                    row[0],
                    smart_round((row[1] or 0) / div if div != 0 else 0),
                    smart_round((row[2] or 0) / div if div != 0 else 0),
                    smart_round((row[3] or 0) / div if div != 0 else 0),
                    "100%", "100%", "100%"
                ]
            else:
                total_p = round_percent((row[1] or 0) / total_total * 100) if total_total != 0 else 0
                export_p = round_percent((row[2] or 0) / total_export * 100) if total_export != 0 else 0
                import_p = round_percent((row[3] or 0) / total_import * 100) if total_import != 0 else 0

                new_row = [
                    i,
                    row[0],
                    smart_round((row[1] or 0) / div if div != 0 else 0),
                    smart_round((row[2] or 0) / div if div != 0 else 0),
                    smart_round((row[3] or 0) / div if div != 0 else 0),
                    f"{total_p}%",
                    f"{export_p}%",
                    f"{import_p}%"
                ]

            final_table_data.append(new_row)

        return units, final_table_data


    def build_trade_dynamics_table(self, data, div, units):
        summary = {}
        for row in data:
            year = row["year"]
            if year not in summary:
                summary[year] = {"export": 0, "import": 0}
            summary[year]["export"] += row.get("export_value", 0) or 0
            summary[year]["import"] += row.get("import_value", 0) or 0

        years = sorted(summary.keys())

        header = [f"{units} долл. США"] + years
        turnover_row = ["Товарооборот"] + [
            smart_round((summary[y]["export"] + summary[y]["import"]) / div) for y in years
        ]
        export_row = ["Экспорт"] + [
            smart_round(summary[y]["export"] / div) for y in years
        ]
        import_row = ["Импорт"] + [
            smart_round(summary[y]["import"] / div) for y in years
        ]

        return [header, turnover_row, export_row, import_row]
