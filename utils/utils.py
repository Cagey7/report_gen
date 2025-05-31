import math


def format_month_range(months):
    if sorted(months) == list(range(1, 13)):
        return ""

    month_names = [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"
    ]

    if not months:
        return ""

    months = sorted(set(months))
    start = month_names[months[0] - 1]
    end = month_names[months[-1] - 1]

    if start == end:
        return start
    else:
        return f"{start}–{end} "


def smart_round(num):
    if num == 0:
        rounded = 0
    elif abs(int(num)) >= 1:
        rounded = round(num, 1)
    else:
        order = int(math.floor(math.log10(abs(num))))
        decimals = -order
        rounded = round(num, decimals)

    str_num = str(rounded).replace(".", ",")

    if "," in str_num:
        int_part, frac_part = str_num.split(",")
    else:
        int_part, frac_part = str_num, ""

    try:
        int_part_with_spaces = "{:,}".format(int(float(int_part))).replace(",", " ")
    except ValueError:
        int_part_with_spaces = int_part

    if frac_part == "0" or frac_part == "":
        return int_part_with_spaces
    else:
        return f"{int_part_with_spaces},{frac_part}"

def format_percent(value, with_sign=True):
    if with_sign and value is None:
        result = "100%"
    elif not with_sign and value is None:
        result = "-"
    else:
        rounded = round_percent(value)
        abs_value = abs(rounded)

        if value <= 0:
            result = f"{abs_value}%" if not with_sign else f"{rounded}%"
        elif value <= 100:
            result = f"{abs_value}%" if not with_sign else f"+{abs_value}%"
        else:
            growth = round(1 + value / 100, 1)
            result = f"рост в {growth} р."

    result = result.replace(".", ",")

    return result

def round_percent(num):
    if abs(int(num)) >= 1:
        return round(num, 1)
    if num == 0:
        return 0
    order = int(math.floor(math.log10(abs(num))))
    decimals = -order
    decimals = max(decimals, 2)

    return round(num, decimals)


def smart_pair_round(num1, num2):
    
    precision = 1
    while True:
        rounded1 = round(num1, precision)
        rounded2 = round(num2, precision)
        if rounded1 != rounded2 or precision >= 10:
            
            return rounded1, rounded2
        precision += 1

def get_main_table_divider(values):
    max_value = max(values)
    min_value = min(values)

    if min_value == 0 or max_value / min_value < 1000:
        return get_divider(max_value)
    else:
        return get_divider(min_value) 


def get_divider(num):
    if num >= 1_000_000_000:
        return 1_000_000_000, "трлн."
    elif num >= 1_000_000:
        return 1_000_000, "млрд."
    elif num >= 1_000:
        return 1_000, "млн."
    else:
        return 1,"тыс."


def get_export_import_table_divider(values):
    max_value = max(values)/1000
    return get_divider(max_value)


def num_converter(num):
    if num >= 1_000_000_000:
        return num / 1_000_000_000, "трлн."
    elif num >= 1_000_000:
        return num / 1_000_000, "млрд."
    elif num >= 1_000:
        return num / 1_000, "млн."
    else:
        return num, "тыс."


