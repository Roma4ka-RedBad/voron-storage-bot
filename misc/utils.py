import re
from pyformatting import optional_format
from aiogram.utils.markdown import hbold, hpre, hcode, hitalic


class FormString:
    def __init__(self, string: str, split_length: int = 4096, split_separator: str = " "):
        self.orig_string = string
        self.split_length = split_length
        self.split_separator = split_separator

    def get_form_string(self, *args, set_style: str = None, with_parts: bool = False, **kwargs):
        string = self.paste_args(self.orig_string, *args, **kwargs)

        if with_parts:
            parts = self.get_parts(string)
            new_parts = []
            for part in parts:
                new_parts.append(self.clear_string(self.set_style(part, set_style)))
            return new_parts

        return self.clear_string(self.set_style(string, set_style))

    @staticmethod
    def clear_string(string: str):
        return string.replace('&lt;', '<').replace('&gt;', '>')

    @staticmethod
    def paste_args(string: str, *args, **kwargs):
        try:
            return optional_format(string, *args, **kwargs)
        except:
            return string

    @staticmethod
    def set_style(string: str, style: str):
        style_functions = {
            "bold": hbold,
            "pre": hpre,
            "code": hcode,
            "italic": hitalic
        }

        if style in style_functions:
            string = style_functions[style](string)

        return string

    def get_parts(self, string: str):
        parts = []
        while string:
            if len(string) > self.split_length:
                try:
                    split_pos = string[:self.split_length].rindex(self.split_separator)
                except ValueError:
                    split_pos = self.split_length
                if split_pos < self.split_length // 4 * 3:
                    split_pos = self.split_length
                parts.append(string[:split_pos])
                string = string[split_pos:].lstrip()
            else:
                parts.append(string)
                break

        return parts

async def get_version_and_query_by_string(string: str):
    raw_text = string.split()
    raw_text.pop(0)
    if raw_text:
        version = re.search("\d+[\.]\d+([\.]\d+)?", ''.join(raw_text))
        version = version[0] if version else None
        major_v, build_v, revision_v = None, None, 1
        if version:
            for x in raw_text:
                if version in x:
                    raw_text.remove(x)
            version = version.split('.')
            major_v = version[0]
            build_v = version[1]
            revision_v = version[2] if len(version) > 2 else 1

        return ''.join(raw_text), major_v, build_v, revision_v
