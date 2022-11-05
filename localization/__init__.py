import json

languages = {
    'ru': json.load(open('localization/ru.json', 'r', encoding='UTF-8')),
    'en': json.load(open('localization/en.json', 'r', encoding='UTF-8'))
}
