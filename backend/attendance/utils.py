import re


def in_string_list(lst, value):
    parsed_list = re.split(r"[;,\s]+", lst.lower())
    return value.lower() in parsed_list
