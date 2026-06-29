"""Currency utility functions."""


def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code (EUR, USD, etc.)

    Returns:
        Formatted currency string
    """
    symbols = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£",
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"
