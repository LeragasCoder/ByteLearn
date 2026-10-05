_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def format_toman(value):
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return value
    grouped = f"{amount:,}".replace(",", "٬")
    return grouped.translate(_DIGITS) + " تومان"
