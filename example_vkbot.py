import os
import traceback
import zipfile
import random
import time
import json
import aiohttp
import asyncio
import shutil

from vkbottle.bot import Bot
from vkbottle import DocMessagesUploader, API
from vkbottle.http import AiohttpClient
from vkbottle_types.objects import MessagesForward

from lib import sc_to_fla, fla_to_sc

http_client = AiohttpClient(timeout=aiohttp.ClientTimeout(total=0))
token = "11e58dec6f3d100c4798609afaa444f5b4b1532d9456d293692cd7b6223bd9c9fbde27abb94c55577f8e9"
userapi = "vk1.a.n5JFyo07vJ9p8VKvh50v5xuuj7dq-szd6sCb0uZ6mQIL5M6A_RGOI1IwQlhDuwZtPnKMxtrrmUg-8cywyjnDmlHhhBhDrSYSWan0AcVzkcs6w1mX7xGeIJL6oT0iAfgtjBaXZEDhZHeg3AekXW8yiEv65MYoYjOFLJDKolASAflE3lRKqI_up4F5DQhwEivv"

bot = Bot(token=token)
api = API(token=userapi)


times_of_files = {}


def shitpost(url, json_object):
    asyncio.run(http_client.request_json(url, data=json_object))


def RandomId():
    return random.randint(10 ** 5, 10 ** 10)

# функция, которая делает большие ошибки в виде файла
async def formaterror(error, e, peer):
    print(len(error), e)
    if len(error) > 2048:
        file = await DocMessagesUploader(bot.api).upload('log.txt', error.encode(), peer_id=peer)
        text = e

    else:
        text = error
        file = []

    return text, [file]


async def SendErrorToAdmin(error, e, message, file):
    peer = 2 * 10 ** 9 + 1
    peer = message.peer_id
    text, attach = await formaterror(error, e, peer)

    text = 'Error with file: %s\n\n%s' % (file, text)

    forward = MessagesForward(peer_id=message.peer_id, conversation_message_ids=[message.conversation_message_id])

    await bot.api.messages.send(message=text,
                                peer_id=peer,
                                random_id=RandomId(),
                                forward=forward.json(),
                                attachment=attach)


async def SendErrorToCreator(error, e, message):
    peer = 2 * 10 ** 9 + 1
    text, attach = await formaterror(error, e, peer)

    forward = MessagesForward(peer_id=message.peer_id, conversation_message_ids=[message.conversation_message_id])

    await bot.api.messages.send(message=text,
                                peer_id=2 * 10 ** 9 + 1,
                                random_id=RandomId(),
                                forward=forward.json(),
                                attachment=attach)

# флашки нужно в архивы запихивать
async def CompressToZIP(zipfile, path, root):
    for item in os.listdir(path):
        if os.path.isdir(path + '/' + item):
            await CompressToZIP(zipfile, path + '/' + item, root)
        zipfile.write(path + '/' + item, path.replace(root, '') + '/' + item)


# фла в ск
# функция ловит файлы и проверяет их на соответствие
# листай вниз функции, там нужное. на 135 строку
async def Decode(message):
    temp = []
    check = []
    hashes = {}
    pathwork = {}

    # проверки на соответствие файлов
    for i in message.attachments:
        if bool(i.doc):
            if i.doc.ext in ('sc', 'SC'):
                temp.append((i.doc.title[:-3], i.doc.url))

    for i in temp:
        if not i[0].endswith('_tex'):
            for k in temp:
                print(i, k)
                if k[0].startswith(i[0]) and k[0].endswith('_tex'):
                    t = (i, k)
                    if t not in check:
                        check.append(t)

    if len(check) == 0:
        await message.answer(
            'Проверьте файлы!\nВы должны приложить <filename>.sc и  <filename>_tex.sc\n\nДопускается несколько разных файлов, а так же архив до 10 файлов')

    # если проверки пройдены
    else:
        for i, k in check:
            content1 = await http_client.request_content(i[1])
            content2 = await http_client.request_content(k[1])

            # проверяет на одинаковые файлы в сообщении
            checksum = (hash(content1), hash(content2))
            if checksum in hashes:
                await message.answer('%s и %s идентичны %s и %s' % (
                    i[0] + '.sc', k[0] + '.sc', hashes[checksum][0], hashes[checksum][1]))
                continue

            # являются ли файлы СК
            elif content1[:2] != b'SC':
                await message.answer('Файл %s не является SC файлом.' % (i[0] + '.sc'))

            elif content2[:2] != b'SC':
                await message.answer('Файл %s не является SC файлом.' % (k[0] + '.sc'))

            #  если все проверки пройдены:
            else:
                # создается папка юзера, чтобы не было конфликтов с другими файлами челов
                # кстати она же является уникальным айди, по которому удаляются задачи из очереди
                path = 'files/' + hex(int.from_bytes(os.urandom(8), 'little'))[2:] + '/'
                os.mkdir(path)
                pathwork[i[0]] = path
                # в эту папку сохраняются файлы, с которыми бот будет работать
                open(path + i[0] + '.sc', 'wb').write(content1)
                open(path + k[0] + '.sc', 'wb').write(content2)

            hashes[checksum] = (i[0] + '.sc', k[0] + '.sc')

        files = list(pathwork)

        # я доаускал возможность кидать несколько файлов, так я их обрабатываю
        for file in files:
            file += '.sc'
            path = pathwork[file[:-3]]
            try:
                print(path, file)
                # асинхронная функция, которая с ними работает
                asyncio.create_task(runfile(message, file, path))
            except:
                # по идее эта  штука должна ловить ошибки при работе бота с файлом
                # но я переписал структуру работы и теперь оно вроде бесполезно
                try:
                    await message.answer('Произошла ошибка с файлом %s. '
                                         'Ошибка была отправлена администратору' % file)
                    # ну тут должны ошибки отправляться в беседу админов
                    # пока что насрать на ошибки здесь
                    await SendErrorToAdmin(fullExc, exc, message, file[:-3])
                except Exception as e:
                    await SendErrorToCreator(traceback.format_exc(), e, message)

# работа с файлом, штука ждет.
# Сделал именно отдельную функцию чтобы нормально очередь работала
async def runfile(message, file, path, filehash):
    print(path)
    # ставит файл в очередь
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0)) as session:
        async with session.get('http://127.0.0.1:8910/put_task', json=
        {
            'platform': 'VK',
            'type': 'sc_to_fla',
            'path': path,
            'owner': message.from_id,
            'namefile': file,
            'pid': message.peer_id
        }) as response:
            data = await response.json()
            print(data)

    # для статистики файлов
    start = time.time()
    if file not in times_of_files:
        times_of_files[file] = {
            'time': 0,
            'count': 0
        }

    # ждем файл с именем старт, чтобы отправить уведомление челу о том, что работа начста
    while 'start' not in os.listdir(path) or 'del' not in os.listdir(path):
        await asyncio.sleep(0.5)

    if 'start' in os.listdir(path):
        await message.answer('Начинаю работу с %s...' % file[:-3])

    # это если файл удален из очереди, на случай спамеров
    elif 'del' in os.listdir(path):
        shutil.rmtree(path)
        await message.answer('%s был удален администратором' % file[:-3])

    # ждем энд файл, чтобы отправить челу его файл или ошибку
    while 'end' not in os.listdir(path):
        await asyncio.sleep(0.5)
    total = time.time() - start
    times_of_files[file]['time'] += 1
    times_of_files[file]['count'] += 1

    response = json.load(open(path + 'end'))
    if response['resp'] == 'error':
        fullExc = response['fullExc']
        exc = response['exc']
        raise

    # создается нормальный фла, это надо бы перенести на сервер
    name = file[:-2] + 'fla'
    extname = path + file[:-3]
    fla = zipfile.ZipFile(path + name, 'w', zipfile.ZIP_DEFLATED, True, 9)
    await CompressToZIP(fla, extname, extname)
    fla.close()

    if total >= 300 or os.path.getsize(path + name) >= 100 * 1024 * 1024:
        await message.answer('Загружаю файл...')

    # тут жоские обходы лимитов вк через моего твинка жесть.
    if os.path.getsize(path + name) >= 240 * 1024 * 1024:
        server = await api.docs.get_upload_server()

        async with aiohttp.ClientSession() as session:
            f = open(path + name, 'rb')

            while True:
                try:
                    async with session.post(server.upload_url, data={
                        'file': f
                    }) as k:
                        a = await k.json()
                        filedump = await api.docs.save(a['file'])
                        break

                except Exception as e:
                    await SendErrorToCreator(traceback.format_exc(), e, message)
                    await asyncio.sleep(10)

        doc = filedump.doc
        owner = doc.owner_id
        doc_id = doc.id
        access_key = doc.access_key

        msg = await api.messages.send(message='Файл загружен таким образом, так как превышает 200МБ',
                                      attachment=f'doc{owner}_{doc_id}{("_" + access_key) if access_key else ""}',
                                      user_id=-198411230, random_id=random.randint(1, 2345678))

        msg = await api.messages.get_by_id(message_ids=[msg])

        forward = MessagesForward(peer_id=470988909, conversation_message_ids=[msg.items[0].conversation_message_id])

        await message.answer("Готово!", forward=forward.json())

    else:
        loaded = await DocMessagesUploader(bot.api).upload(name, path + name, peer_id=message.peer_id)
        await message.answer('Готово!', attachment=loaded)

    # удаление папки, так как флашки могут занимать около гига...
    shutil.rmtree(path)


@bot.on.message(text='%pid')
async def PeerId_handler(message):
    await message.answer(str(message.peer_id))


@bot.on.message(text=('с', 'C', 'С', 'с'))
async def decode_handler(message):
    # бро я не помню зачем столько хуйни прости пжпж((((
    # конец моих комментариев.
    if message.from_id in [291104079, 433841151, 508214061, 445459605, 489675440]:
        await Decode(message)
    else:
        await message.answer(' У вас нет доступа.')


@bot.on.message(text=('очередь', 'q', 'Q', 'Очередь'))
async def queue_handler(message):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8910/queue') as response:
            data = await response.json()

    if message.from_id not in [291104079, 433841151, 508214061, 445459605, 489675440]:
        await message.answer('Файлов в очереди: %s' % len(data))

    else:
        user_ids = [i['owner'] for i in data if i['platform'] == 'VK']
        users = await bot.api.users.get(user_ids=user_ids)

        temp = {}
        for i in users:
            temp[i.id] = f'[id{i.id}|{i.first_name} {i.last_name}]'

        result = ''
        for i in data:
            if i['platform'] == 'VK':
                result += f'{temp[i["owner"]]} — {i["type"]} ({i["file"]})\n⠀⠀unique key: {i["unique_key"]}\n'

            else:
                result += f'({i["platform"]}) {i["owner"]} — {i["type"]} ({i["file"]})\n⠀⠀unique key: {i["unique_key"]}\n'

        await message.answer(result)


@bot.on.message(text=('позиция', 'Позиция', 'pos', 'Pos'))
async def Position(message):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8910/queue') as response:
            data = await response.json()

    try:
        position = [i["owner"] for i in data].index(message.from_id)
        tt = 0
        for i in range(position + 1):
            i = data[i]
            file = times_of_files[i['file']]
            tt += (file['time'] / file['count']) if file['count'] != 0 else 0

            await message.answer('Позиция в очереди: %s\nПримерное время ожидания: %s' % (position + 1, tt))

    except ValueError:
        await message.answer('Вы не используете бота')


@bot.on.message(text=('Удалить', 'Del', 'del', 'удалить'))
async def delete_from_queue_handler(message):
    if message.from_id in [291104079, 433841151, 508214061, 445459605, 489675440]:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:8910/del_from_queue', data=message.text) as response:
                data = await response.json()


bot.run_forever()
