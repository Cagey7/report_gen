import math
from data.country_cases import country_cases
from data.region_cases import region_cases
from data.month_ranges import month_ranges


class TextDataPreparer:
    def __init__(self, context):
        self.context = context
    
    def gen_summary_text(self, direction):
        div = self.context.table_divider
        units = self.context.table_measure
        
        if direction == "total":
            direction_ru = "Товарооборот"
            sum_data = self.context.total_data_sum
            base_year_sum = self.context.smart_round(sum_data["base_year_sum"]/div)
            target_year_sum = self.context.smart_round(sum_data["target_year_sum"]/div)
            
            # if base_year_sum == 0 and target_year_sum == 0:
            #     return ""
            # elif target_year_sum == 0:
            #     percent = "100%"
            if base_year_sum == target_year_sum:
                base_year_sum, target_year_sum = self.context.smart_pair_round(sum_data["base_year_sum"]/div, sum_data["target_year_sum"]/div)
        elif direction == "export":
            direction_ru = "Экспорт"
            sum_data = self.context.export_data_sum
            base_year_sum = self.context.smart_round(sum_data["base_year_sum"]/div)
            if base_year_sum == 0:
                return ""
        elif direction == "import":
            direction_ru = "Импорт"
            sum_data = self.context.import_data_sum
            base_year_sum = self.context.smart_round(sum_data["base_year_sum"]/div)
            if base_year_sum == 0:
                return ""

        percent = sum_data['growth_value']
        change = sum_data["growth_value"]
        if direction == "total":
            if change > 0:
                return f"{direction_ru} между {region_cases[self.context.region]['творительный']} и {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'} составил {base_year_sum} {units} долл. США, что на {self.context.format_percent(percent)} больше, чем за аналогичный период предыдущего года {target_year_sum} {units} долл. США)."
            elif change < 0:
                return f"{direction_ru} между {region_cases[self.context.region]['творительный']} и {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'} составил {base_year_sum} {units} долл. США, что на {self.context.format_percent(percent)} ниже, чем за аналогичный период предыдущего года {target_year_sum} {units} долл. США)."
            elif change > 100:
                return f"{direction_ru} между {region_cases[self.context.region]['творительный']} и {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'} составил {base_year_sum} {units} долл. США, увеличился {self.context.format_percent(percent)}, чем за аналогичный период предыдущего года {target_year_sum} {units} долл. США)."
            else:
                return f"{direction_ru} между {region_cases[self.context.region]['творительный']} и {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'} составил {base_year_sum} {units} долл. США."
        elif direction == "export":
            if change > 0:
                return f"{direction_ru} из {region_cases[self.context.region]['родительный']} в {country_cases[self.context.country]['винительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'}, вырос на {self.context.format_percent(percent)} и составил {base_year_sum} {units} долл. США."
            elif change < 0:
                return f"{direction_ru} из {region_cases[self.context.region]['родительный']} в {country_cases[self.context.country]['винительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'}, снизнился на {self.context.format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            elif change > 100:
                return f"{direction_ru} из {region_cases[self.context.region]['родительный']} в {country_cases[self.context.country]['винительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'}, увеличился {self.context.format_percent(percent)} и составил {base_year_sum} {units} долл. США."
            else:
                return f"{direction_ru} из {region_cases[self.context.region]['родительный']} в {country_cases[self.context.country]['винительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'} составил {base_year_sum} {units} долл. США."
        elif direction == "import":
            if change > 0:
                return f"{direction_ru} в {region_cases[self.context.region]['винительный']} из {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'}, вырос на {self.context.format_percent(percent)} и составил {base_year_sum} {units} долл. США."
            elif change < 0:
                return f"{direction_ru} в {region_cases[self.context.region]['винительный']} из {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'}, снизнился на {self.context.format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            elif change > 100:
                return f"{direction_ru} в {region_cases[self.context.region]['винительный']} из {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'}, увеличился {self.context.format_percent(percent)} и составил {base_year_sum} {units} долл. США."
            else:
                return f"{direction_ru} в {region_cases[self.context.region]['винительный']} из {country_cases[self.context.country]['творительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if month_ranges[self.context.month] == '' else 'года'} составил {base_year_sum} {units} долл. США."


    def gen_decline_growth_row(self, data, trend):
        if data["abs_change"] < 0:
            name = data["tn_ved_name"].lower()
            curr_value = data["target_year_value"]
            prev_value = data["base_year_value"]
            drop_value = abs(data["abs_change"])

            if trend == "decline":
                if prev_value == 0:
                    return
                drop_percent = (math.trunc(drop_value * 10) / 10) / prev_value * 100
                drop_value, units = self.context.num_converter(drop_value)
                if units == "трлн.":
                    curr_value = curr_value / 1_000_000_000
                    prev_value = prev_value / 1_000_000_000
                elif units == "млрд.":
                    curr_value = curr_value / 1_000_000
                    prev_value = prev_value / 1_000_000
                elif units == "млн.":
                    curr_value = curr_value / 1_000
                    prev_value = prev_value / 1_000

                return f"{name} - на {self.context.format_percent(drop_percent, False)} или на {self.context.smart_round(drop_value)} {units} долл. США (с {self.context.smart_round(prev_value)} до {self.context.smart_round(curr_value)} {units} долл. США)"
            elif trend == "growth":
                growth_value = data["growth_value"]
                prev_value, units = self.context.num_converter(prev_value)
                if units == "трлн.":
                    drop_value = drop_value / 1_000_000_000
                    curr_value = curr_value / 1_000_000_000
                elif units == "млрд.":
                    drop_value = drop_value / 1_000_000
                    curr_value = curr_value / 1_000_000
                elif units == "млн.":
                    drop_value = drop_value / 1_000
                    curr_value = curr_value / 1_000
                return f"{name} - {self.context.format_percent(growth_value, False)} или на {self.context.smart_round(drop_value)} {units} долл. США (с {self.context.smart_round(curr_value)} до {self.context.smart_round(prev_value)} {units} долл. США)"


    def gen_summary_row(self, data):
        name = data["tn_ved_name"].lower()
        value = data["base_year_value"]
        share = data["base_year_share"]
        formatted_value, units = self.context.num_converter(value)
        return f"{name} – {self.context.smart_round(formatted_value)} {units} долл. США (с долей {self.context.format_percent(share, False)})"


    def gen_text_flow(self, direction):
        text_size = self.context.text_size

        if direction == "export":
            export_text = []

            summary_text = self.gen_summary_text(direction)
            export_text.append(summary_text)

            decline_data = sorted(self.context.table_data_export_reverse, key=lambda x: x["abs_change"], reverse=False)
            rows_decline_text = []
            for row in decline_data[:text_size]:
                if row["tn_ved_code"] in self.context.exclude_tn_veds:
                    continue
                result = self.gen_decline_growth_row(row, "decline")
                if result is not None:
                    rows_decline_text.append(result)
        
            decline_text = (
                f"Сокращение экспорта в {region_cases[self.context.region]['винительный']} обосновывается снижением поставок таких товаров, как: "
                f"{', '.join(rows_decline_text)}."
            )
            
            export_text.append(decline_text)

            growth_data = sorted(self.context.table_data_export, key=lambda x: x["abs_change"], reverse=False)
            row_growth_text = []
            for row in growth_data[:text_size]:
                result = self.gen_decline_growth_row(row, 'growth')
                if result is not None:
                    row_growth_text.append(result)
            growth_text = (
                f"Вместе с тем, наблюдается рост поставок таких товаров, как: "
                f"{', '.join(row_growth_text)}."
            )
            export_text.append(growth_text)
            
            row_main_text = []
            for row in self.context.table_data_export[:text_size]:
                if row["tn_ved_code"] in self.context.exclude_tn_veds:
                    continue
                result = self.gen_summary_row(row)
                if result is not None:
                    row_main_text.append(result)

            main_text = (
                f"Основными товарами экспорта в {region_cases[self.context.region]['винительный']} из {country_cases[self.context.country]['родительный']} являются: "
                f"{', '.join(row_main_text)}."
            )

            export_text.append(main_text)

            info_text = f"Более подробная информация по основным экспортируемым товарам в {country_cases[self.context.country]['винительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if self.context.month == 12 else 'года'} показана в Таблице №1."
            export_text.append(info_text)

            return export_text
        
        if direction == "import":
            import_text = []
            summary_text = self.gen_summary_text(direction)
        
            import_text.append(summary_text)

            decline_data = sorted(self.context.table_data_import_reverse, key=lambda x: x["abs_change"], reverse=False)
            row_decline_text = []
            for row in decline_data[:text_size]:
                if row["tn_ved_code"] in self.context.exclude_tn_veds:
                    continue
                result = self.gen_decline_growth_row(row, 'decline')
                if result is not None:
                    row_decline_text.append(result)

            decline_text = (
                f"Сокращение импорта из {country_cases[self.context.country]['родительный']} обосновывается снижением ввоза таких товаров, как: "
                f"{', '.join(row_decline_text)}."
            )
            import_text.append(decline_text)
            
            growth_data = sorted(self.context.table_data_import, key=lambda x: x["abs_change"], reverse=False)
            row_growth_text = []
            for row in growth_data[:text_size]:
                result = self.gen_decline_growth_row(row, 'growth')
                if result is not None:
                    row_growth_text.append(result)

            growth_text = (
                f"Вместе с тем, наблюдается рост импорта таких товаров, как: "
                f"{', '.join(row_growth_text)}."
            )
            import_text.append(growth_text)

            row_main_text = []
            for row in self.context.table_data_import[:text_size]:
                if row["tn_ved_code"] in self.context.exclude_tn_veds:
                    continue
                result = self.gen_summary_row(row)
                if result is not None:
                    row_main_text.append(result)

            main_text = (
                f"Основными товарами импорта в {region_cases[self.context.region]['винительный']} из {country_cases[self.context.country]['родительный']} являются: "
                f"{', '.join(row_main_text)}."
            )
            import_text.append(main_text)

            info_text = f"Более подробная информация по основным импортируемым товарам из {country_cases[self.context.country]['родительный']} за {month_ranges[self.context.month]}{self.context.year} {'год' if self.context.month == 12 else 'года'} показана в Таблице №2."
            import_text.append(info_text)

            return import_text
