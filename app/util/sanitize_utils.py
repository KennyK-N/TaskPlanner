import bleach


def clean_value(value):
    """
    Strips HTML tags and unsafe content from a single string using bleach.
    Args:
        value (str): The raw input string to sanitize.
    Returns:
        str: Sanitized string, or an empty string if value is falsy.
    """
    return bleach.clean(value, strip=True) if value else ""


def clean_list(values):
    """
    Sanitizes a list of strings, stripping HTML tags from each entry and dropping empty values.
    Args:
        values (list[str]): List of raw input strings.
    Returns:
        list[str]: List of sanitized non-empty strings.
    """
    return [bleach.clean(value, strip=True) for value in values if value]
