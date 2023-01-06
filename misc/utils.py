from pyformatting import optional_format
from aiogram.utils.markdown import hbold, hpre, hcode, hitalic


def easy_format(string: str, *args, formatting: list = None, **kwargs):
    formatting_functions = {
        "bold": hbold,
        "pre": hpre,
        "code": hcode,
        "italic": hitalic
    }
    try:
        string = optional_format(string, *args, **kwargs)
        if formatting:
            for _format in formatting:
                if _format in formatting_functions:
                    string = formatting_functions[_format](string)
        return string
    except:
        return string
