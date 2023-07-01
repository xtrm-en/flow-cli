# -*- coding: utf-8 -*-

def stringify(v: object) -> str:
    if isinstance(v, list):
        return ",".join(map(stringify, v))
    return str(v)


def parse(value: str, t: type) -> object:
    if t == str:
        return value
    elif t == int:
        return int(value)
    elif t == float:
        return float(value)
    elif t == bool:
        return value.lower() == "true"
    elif t == list:
        value_list = value.split(",")
        if len(value_list) == 1 and value_list[0] == "":
            return []
        return value_list
    else:
        raise ValueError(f"Invalid type {t}")
