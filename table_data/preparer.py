class TableDataPreparer:
    def __init__(self, context):
        self.context = context


    def build_main_table(self):
        div = self.context.table_divider
        units = self.context.table_measure
        export_sum = self.context.export_data_sum
        import_sum = self.context.import_data_sum
        total_sum = self.context.total_data_sum
        base_balance = export_sum["base_year_sum"] - import_sum["base_year_sum"]
        target_balance = export_sum["target_year_sum"] - import_sum["target_year_sum"]

        balance_status = (
            "улучшился" if base_balance > target_balance
            else "ухудшился" if base_balance < target_balance
            else "без изменений"
        )

        header = [
            f"{units} долл. США",
            f"{self.context.year - 1}",
            f"{self.context.year}",
            f"Прирост {self.context.year - 1}/{self.context.year}"
        ]

        target_year_sum_total = self.context.smart_round(total_sum["target_year_sum"]/div)
        base_year_sum_total = self.context.smart_round(total_sum["base_year_sum"]/div)
        
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
                    target_year_sum_total, base_year_sum_total = self.context.smart_pair_round(total_sum["target_year_sum"]/div, total_sum["base_year_sum"]/div)
            
            total_row = ["Товарооборот", target_year_sum_total, base_year_sum_total, self.context.format_percent(growth_value_total)]


        if export_sum["target_year_sum"] == 0 and export_sum["base_year_sum"] == 0:
            export_row = ["Экспорт", 0, 0, ""]
        else:
            target_year_sum_export = self.context.smart_round(export_sum["target_year_sum"]/div)
            base_year_sum_export = self.context.smart_round(export_sum["base_year_sum"]/div)
            if target_year_sum_export == 0:
                growth_value_export = "new"
            elif base_year_sum_export == 0:
                growth_value_export = "-100%"
            else:
                growth_value_export = export_sum["growth_value"]
            if target_year_sum_export == base_year_sum_total:
                target_year_sum_total, base_year_sum_export = self.context.smart_pair_round(export_sum["target_year_sum"]/div, export_sum["base_year_sum"]/div)
            export_row = ["Экспорт", target_year_sum_export, base_year_sum_export, self.context.format_percent(growth_value_export)]


        if import_sum["target_year_sum"] == 0 and import_sum["base_year_sum"] == 0:
            import_row = ["Импорт", 0, 0, ""]
        else:
            target_year_sum_import = self.context.smart_round(import_sum["target_year_sum"]/div)
            base_year_sum_import = self.context.smart_round(import_sum["base_year_sum"]/div)
            if target_year_sum_import == 0:
                growth_value_import = "new"
            elif base_year_sum_import == 0:
                growth_value_import = "-100%"
            else:
                growth_value_import = import_sum["growth_value"]
            if target_year_sum_import == base_year_sum_import:
                target_year_sum_total, base_year_sum_export = self.context.smart_pair_round(import_sum["target_year_sum"]/div, import_sum["base_year_sum"]/div)
            
            import_row = ["Импорт", target_year_sum_import, base_year_sum_import, self.context.format_percent(growth_value_import)]


        target_balance_data = self.context.smart_round(target_balance/div)
        base_balance_data = self.context.smart_round(base_balance/div)
        if target_balance_data == base_balance_data:
            target_year_sum_total, base_year_sum_export = self.context.smart_pair_round(target_balance/div, base_balance/div)
        balance_row = [
            "Торговый баланс",
            self.context.smart_round(target_balance/div),
            self.context.smart_round(base_balance/div),
            balance_status
        ]

        return [header, total_row, export_row, import_row, balance_row]


    def build_export_import_table(self, direction):
        table_size = self.context.table_size
        if direction == "import":
            data = self.context.table_data_import
            div = self.context.import_table_divider
            sum_data = self.context.import_data_sum
            gen_type_name = "импорт"
            measure = self.context.import_table_measure
        elif direction == "export":
            data = self.context.table_data_export
            div = self.context.export_table_divider
            sum_data = self.context.export_data_sum
            gen_type_name = "экспорт"
            measure = self.context.export_table_measure
        
        table_data = []
        sum_row = [
            f"Всего {gen_type_name}",
            "",
            self.context.smart_round(sum_data["target_year_sum"]/div),
            "100%",
            "",
            self.context.smart_round(sum_data["base_year_sum"]/div),
            "100%",
            "",
            self.context.format_percent(sum_data["growth_value"])
        ]
        
        table_data.append(sum_row)
        
        index = 1
        for row in data[:table_size]:
            if row["tn_ved_code"] in self.context.exclude_tn_veds:
                continue
            name = f"{index}. {row['tn_ved_name']} (код {row['tn_ved_code']} ТНВЭД), {row['measure']}"
            index += 1
            if row["target_year_units"]:
                target_volume = self.context.smart_round(row["target_year_units"])
            else:
                target_volume = self.context.smart_round(row["target_year_tons"])
            
            target_year_value = self.context.smart_round(row["target_year_value"]/div)
            target_year_share = self.context.format_percent(row["target_year_share"], False)
            
            if row["base_year_units"]:
                base_volume = self.context.smart_round(row["base_year_units"])
            else:
                base_volume = self.context.smart_round(row["base_year_tons"])
            
            base_year_value = self.context.smart_round(row["base_year_value"]/div)
            base_year_share = self.context.format_percent(row["base_year_share"], False)
            
            if row["growth_units"]:
                growth_volume = self.context.format_percent(row["growth_units"])
            else:
                growth_volume = self.context.format_percent(row["growth_tons"])
            if growth_volume == "100%":
                growth_volume = "new"
            
            growth_value = self.context.format_percent(row["growth_value"])
            if growth_value == "100%":
                growth_value = "new"
            row_data = [name, target_volume, target_year_value, target_year_share, base_volume, base_year_value, base_year_share, growth_volume, growth_value]
            table_data.append(row_data)
        return table_data
            