import re


async def get_version_and_query_by_string(string: str):
    raw_text = string.split()
    raw_text.pop(0)
    if raw_text:
        version = re.search(r"\d+\.\d(\.\d+)?", ''.join(raw_text))
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
