def parse_bool(s: str) -> bool:
    s = s.lower()
    if s in ('true', 'yes', 'y', 'on', '1'):
        return True
    elif s in ('false', 'no', 'n', 'off', '0'):
        return False
    raise AssertionError("not a boolean value (true/false, 1/0, etc.)")


def read_system_prompt(path='system_prompt.txt'):
    try:
        with open(path, encoding='utf8') as f:
            return f.read()
    except FileNotFoundError:
        return 'You are a helpful and reliable assistant.'

