import re

def FormatPhone(number):
    if not number:
        return number
    digits = re.sub(r'\D', '', str(number))
    if digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return number

def ExtractEmails(emailList):
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    emails = set()
    with open(emailList, "r", encoding="utf-8") as f:
        for line in f:
            emails.update(re.findall(email_regex, line))
    return list(emails)