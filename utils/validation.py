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
