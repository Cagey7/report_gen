class TableDataPreparer:
    def __init__(self, context):
        self.context = context


    def build_main_table(self):
        export_sum = self.context.export_data_sum
        import_sum = self.context.import_data_sum

        base_total = export_sum["base_year_sum"] + import_sum["base_year_sum"]
        target_total = export_sum["target_year_sum"] + import_sum["target_year_sum"]

        growth_total = ((base_total - target_total) / target_total) * 100 if target_total else 0

        base_balance = export_sum["base_year_sum"] - import_sum["base_year_sum"]
        target_balance = export_sum["target_year_sum"] - import_sum["target_year_sum"]

        balance_status = (
            "улучшился" if base_balance > target_balance
            else "ухудшился" if base_balance < target_balance
            else "без изменений"
        )

        header = [
            "долл. США",
            f"{self.context.year - 1}",
            f"{self.context.year}",
            f"Прирост {self.context.year - 1}/{self.context.year}"
        ]

        total_row = [
            "Товарооборот",
            target_total,
            base_total,
            growth_total
        ]
        export_row = [
            "Экспорт",
            export_sum["target_year_sum"],
            export_sum["base_year_sum"],
            export_sum["growth_value"]
        ]
        import_row = [
            "Импорт",
            import_sum["target_year_sum"],
            import_sum["base_year_sum"],
            import_sum["growth_value"]
        ]
        balance_row = [
            "Торговый баланс",
            target_balance,
            base_balance,
            balance_status
        ]

        return [header, total_row, export_row, import_row, balance_row]


    def build_product_table(self, gen_type):
        if gen_type == "import":
            table_data = self.context.table_data_import
            sum_data = self.context.import_data_sum
            gen_type_name = "импорт"
        elif gen_type == "export":
            table_data = self.context.table_data_export
            sum_data = self.context.export_data_sum
            gen_type_name = "экспорт"

        data = []

        sum_row = [
            f"Всего {gen_type_name}",
            "",
            sum_data["target_year_sum"],
            "100%",
            "",
            sum_data["base_year_sum"],
            "100%",
            "",
            sum_data["growth_value"]
        ]
        data.append(sum_row)
        for i, row in enumerate(table_data):
            measure_info = "units" if row["base_year_units"] is not None else "tons"
            product_data = [
                f"{i+1}. {row['tn_ved_name']} (код {row['tn_ved_code']} ТНВЭД, в {row['measure']})",
                f"{row[f'target_year_{measure_info}']}",
                f"{row['target_year_value']}",
                f"{row['target_year_share']}",
                f"{row[f'base_year_{measure_info}']}",
                f"{row['base_year_value']}",
                f"{row['base_year_share']}",
                f"{row[f'growth_{measure_info}']}",
                f"{row['growth_value']}",
            ]
            data.append(product_data)

        return data