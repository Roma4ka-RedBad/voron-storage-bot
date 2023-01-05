import json

languages = {
    'ru': json.load(open(f"{__path__[0]}/ru.json", 'r', encoding='UTF-8')),
    'en': json.load(open(f"{__path__[0]}/en.json", 'r', encoding='UTF-8'))
}
