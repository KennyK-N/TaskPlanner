import bleach


def clean_value(value):
    return bleach.clean(value, strip=True) if value else ""


def clean_list(values):
    return [bleach.clean(value, strip=True) for value in values if value]
