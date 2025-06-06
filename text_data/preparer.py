import math
from data.country_cases import country_cases
from data.region_cases import region_cases
from utils.utils import *


class TextDataPreparer:
    def gen_summary_text(self, direction, country, region, year, months, sum_data, div, units):
        base_year_sum = smart_round(sum_data["base_year_sum"]/div)
        target_year_sum = smart_round(sum_data["target_year_sum"]/div)
        if sum_data["base_year_sum"] == 0 and sum_data["target_year_sum"] == 0:
            return ""
        if base_year_sum == target_year_sum:
            base_year_sum, target_year_sum = smart_pair_round(sum_data["base_year_sum"]/div, sum_data["target_year_sum"]/div)
        
        direction_map = {
            "total": "Товарооборот",
            "export": "Экспорт",
            "import": "Импорт"
        }
        direction_ru = direction_map.get(direction, "")

        percent = sum_data['growth_value']
        change = sum_data["growth_value"]
        
        month_str = format_month_range(months)
        year_str = f"{year} {'год' if month_str == '' else 'года'}"
        if direction == "total":
            subject = f"{direction_ru} между {region_cases[region]['творительный']} и {country_cases[country]['творительный']}"
            if change > 0:
                return f"{subject} за {month_str}{year_str} составил {base_year_sum} {units} долл. США, что на {format_percent(percent, False)} больше, чем за аналогичный период предыдущего года {target_year_sum} {units} долл. США)."
            elif change < 0:
                return f"{subject} за {month_str}{year_str} составил {base_year_sum} {units} долл. США, что на {format_percent(percent, False)} ниже, чем за аналогичный период предыдущего года {target_year_sum} {units} долл. США)."
            elif change > 100:
                return f"{subject} за {month_str}{year_str} составил {base_year_sum} {units} долл. США, увеличился {format_percent(percent, False)}, чем за аналогичный период предыдущего года {target_year_sum} {units} долл. США)."
            else:
                return f"{subject} за {month_str}{year_str} составил {base_year_sum} {units} долл. США."
        
        if direction == "export":
            subject = f"{direction_ru} из {region_cases[region]['родительный']} в {country_cases[country]['винительный']}"
            if change > 0:
                return f"{subject} за {month_str}{year_str}, вырос на {format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            elif change < 0:
                return f"{subject} за {month_str}{year_str}, снизнился на {format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            elif change > 100:
                return f"{subject} за {month_str}{year_str}, увеличился {format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            else:
                return f"{subject} за {month_str}{year_str} составил {base_year_sum} {units} долл. США."

        if direction == "import":
            subject = f"{direction_ru} в {region_cases[region]['винительный']} из {country_cases[country]['творительный']}"
            if change > 0:
                return f"{subject} за {month_str}{year_str}, вырос на {format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            elif change < 0:
                return f"{subject} за {month_str}{year_str}, снизнился на {format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            elif change > 100:
                return f"{subject} за {month_str}{year_str}, увеличился {format_percent(percent, False)} и составил {base_year_sum} {units} долл. США."
            else:
                return f"{subject} за {month_str}{year_str} составил {base_year_sum} {units} долл. США."


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
                drop_value, units = num_converter(drop_value)
                if units == "трлн.":
                    curr_value = curr_value / 1_000_000_000
                    prev_value = prev_value / 1_000_000_000
                elif units == "млрд.":
                    curr_value = curr_value / 1_000_000
                    prev_value = prev_value / 1_000_000
                elif units == "млн.":
                    curr_value = curr_value / 1_000
                    prev_value = prev_value / 1_000
                drop_percent_formatted = format_percent(drop_percent, False)
                if "-" in drop_percent_formatted:
                    drop_percent_formatted = "100%"
                return f"{name} - {'на ' if not drop_percent_formatted.lower().startswith('рост') else ''}{drop_percent_formatted} или на {smart_round(drop_value)} {units} долл. США (с {smart_round(prev_value)} до {smart_round(curr_value)} {units} долл. США)"
            elif trend == "growth":
                growth_value = data["growth_value"]
                prev_value, units = num_converter(prev_value)
                if units == "трлн.":
                    drop_value = drop_value / 1_000_000_000
                    curr_value = curr_value / 1_000_000_000
                elif units == "млрд.":
                    drop_value = drop_value / 1_000_000
                    curr_value = curr_value / 1_000_000
                elif units == "млн.":
                    drop_value = drop_value / 1_000
                    curr_value = curr_value / 1_000
                
                growth_value_formatted = format_percent(growth_value, False)
                if "-" in growth_value_formatted:
                    growth_value_formatted = "100%"
                return f"{name} - {'на ' if not growth_value_formatted.lower().startswith('рост') else ''}{growth_value_formatted} или на {smart_round(drop_value)} {units} долл. США (с {smart_round(curr_value)} до {smart_round(prev_value)} {units} долл. США)"


    def gen_summary_row(self, data):
        name = data["tn_ved_name"].lower()
        value = data["base_year_value"]
        share = data["base_year_share"]
        formatted_value, units = num_converter(value)
        return f"{name} – {smart_round(formatted_value)} {units} долл. США (с долей {format_percent(share, False)})"


    def gen_text_flow(self, direction, year, months, data, data_reverse, sum_data, region, country_or_group, exclude_tn_veds, text_size, div, units):
        
        if direction == "export":
            export_text = []

            summary_text = self.gen_summary_text(direction, country_or_group, region, year, months, sum_data, div, units)
            if summary_text == "":
                return [f"Экспорт в {year} году в {region_cases[region]['винительный']} за отчетный период отсутствовал."]
            export_text.append(summary_text)

            rows_decline_text = self.gen_decline_growth_text("decline", data_reverse, text_size, exclude_tn_veds)

            row_growth_text = self.gen_decline_growth_text("growth", data, text_size, exclude_tn_veds)
            row_main_text = self.gen_main_text(data, text_size, exclude_tn_veds)

            
            main_text = (
                f"Основными товарами экспорта из {region_cases[region]['родительный']} в {country_cases[country_or_group]['винительный']} являются: "
                f"{', '.join(row_main_text)}."
            )
            
            info_text = f"Более подробная информация по основным экспортируемым товарам в {country_cases[country_or_group]['винительный']} за {format_month_range(months)}{year} {'год' if months[-1] == 12 else 'года'} показана в Таблице №1."
            

            if sum_data["base_year_sum"] > sum_data["target_year_sum"]:
                growth_text = (
                    f"Рост экспорта обосновывается увеличением поставок таких товаров, как: "
                    f"{', '.join(row_growth_text)}."
                )
                decline_text = (
                    f"Вместе с тем, наблюдается снижение экспортных поставок таких товаров, как: "
                    f"{', '.join(rows_decline_text)}."
                )
                
                if row_growth_text == []:
                    export_text.append("")
                else:
                    export_text.append(growth_text)

                if rows_decline_text == []:
                    export_text.append("")
                else:
                    export_text.append(decline_text)
                
            else:
                decline_text = (
                    f"Сокращение экспорта из {region_cases[region]['родительный']} обосновывается снижением поставок таких товаров, как: "
                    f"{', '.join(rows_decline_text)}."
                )
                
                growth_text = (
                    f"Вместе с тем, наблюдается рост поставок таких товаров, как: "
                    f"{', '.join(row_growth_text)}."
                )

                if rows_decline_text == []:
                    export_text.append("")
                else:
                    export_text.append(decline_text)
                
                if row_growth_text == []:
                    export_text.append("")
                else:
                    export_text.append(growth_text)
            
            if row_main_text == []:
                export_text.append("")
            else:
                export_text.append(main_text)
            
            export_text.append(info_text)
            
            return export_text
        
        if direction == "import":
            import_text = []
            summary_text = self.gen_summary_text(direction, country_or_group, region, year, months, sum_data, div, units)
            if summary_text == "":
                return [f"Импорт в {year} году из {region_cases[region]['винительный']} за отчетный период отсутствовал."]
            import_text.append(summary_text)


            rows_decline_text = self.gen_decline_growth_text("decline", data_reverse, text_size, exclude_tn_veds)
            row_growth_text = self.gen_decline_growth_text("growth", data, text_size, exclude_tn_veds)
            row_main_text = self.gen_main_text(data, text_size, exclude_tn_veds)

            main_text = (
                f"Основными товарами импорта в {region_cases[region]['винительный']} из {country_cases[country_or_group]['родительный']} являются: "
                f"{', '.join(row_main_text)}."
            )
            
            info_text = f"Более подробная информация по основным импортируемым товарам из {country_cases[country_or_group]['родительный']} за {format_month_range(months)}{year} {'год' if months[-1] == 12 else 'года'} показана в Таблице №2."
            
            if sum_data["base_year_sum"] > sum_data["target_year_sum"]:
                growth_text = (
                    f"Рост экспорта обосновывается увеличением поставок таких товаров, как: "
                    f"{', '.join(row_growth_text)}."
                )
                decline_text = (
                    f"Вместе с тем, наблюдается снижение экспортных поставок таких товаров, как: "
                    f"{', '.join(rows_decline_text)}."
                )

            else:
                decline_text = (
                    f"Сокращение экспорта из {region_cases[region]['родительный']} обосновывается снижением поставок таких товаров, как: "
                    f"{', '.join(rows_decline_text)}."
                )

                growth_text = (
                    f"Вместе с тем, наблюдается рост поставок таких товаров, как: "
                    f"{', '.join(row_growth_text)}."
                )

                if rows_decline_text == []:
                    import_text.append("")
                else:
                    import_text.append(decline_text)
                
                if row_growth_text == []:
                    import_text.append("")
                else:
                    import_text.append(growth_text)
            
            if row_main_text == []:
                import_text.append("")
            else:
                import_text.append(main_text)
            import_text.append(info_text)

            return import_text


    def gen_decline_growth_text(self, trand, data, text_size, exclude_tn_veds):
        sorted_data = sorted(data, key=lambda x: x["abs_change"], reverse=False)
        text_block = []
        for row in sorted_data[:text_size]:
            if row["tn_ved_code"] in exclude_tn_veds:
                continue
            result = self.gen_decline_growth_row(row, trand)
            if result is not None:
                text_block.append(result)
        
        return text_block


    def gen_main_text(self, data, text_size, exclude_tn_veds):
        row_main_text = []
        for row in data[:text_size]:
            if row["tn_ved_code"] in exclude_tn_veds:
                continue
            result = self.gen_summary_row(row)
            if result is not None:
                row_main_text.append(result)
        
        return row_main_text
