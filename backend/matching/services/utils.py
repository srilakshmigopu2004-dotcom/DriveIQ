def csv_list(text):
    """'Python, Java ' -> ['python', 'java'] (lower-case, stripped, no blanks)."""
    return [x.strip().lower() for x in (text or "").split(",") if x.strip()]


def format_inr(amount):
    """Indian digit grouping: 600000 -> '₹6,00,000'."""
    if amount is None:
        return None
    n = int(round(float(amount)))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if n < 0 else "") + "₹" + s
