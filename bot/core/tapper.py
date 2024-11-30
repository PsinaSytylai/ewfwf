from datetime import datetime, timedelta, timezone
from dateutil import parser
from time import time, sleep
from urllib.parse import unquote, quote
import re

from json import dump as dp, loads as ld
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw import types

import asyncio
import random
import string
import brotli
import base64
import secrets
import uuid
import aiohttp
import json

import requests

from .agents import generate_random_user_agent
from .headers import headers
from .helper import format_duration

from bot.config import settings
from bot.utils import logger
from bot.utils.logger import SelfTGClient
from bot.exceptions import InvalidSession

import asyncio
from telegram import ParseMode
from telegram import Bot
from telegram.error import TelegramError

"""all_for_picture"""

from PIL import Image
import numpy as np

TEMPLATE_ID = 1270595015

elements = []

def download_image_with_timestamp(base_url, save_path):
    """
    Делает GET-запрос с временной меткой и сохраняет полученное изображение на диск.
    
    :param base_url: Базовый URL для запроса изображения
    :param save_path: Путь, куда сохранить загруженное изображение
    """
    # Получаем текущее время в миллисекундах
    timestamp = int(time() * 1000)
    
    # Формируем URL с временной меткой
    url_with_timestamp = f"{base_url}?time={timestamp}"
    
    response = requests.get(url_with_timestamp, stream=True)
    
    # Проверяем, успешен ли запрос
    if response.status_code == 200:
        # Открываем файл для записи изображения в бинарном режиме
        with open(save_path, 'wb') as file:
            # Записываем содержимое ответа в файл
            for chunk in response.iter_content(1024):  # Загружаем по 1KB за раз
                file.write(chunk)
        print(f'Изображение успешно сохранено как {save_path}')
    else:
        print(f'Не удалось скачать изображение. Код ошибки: {response.status_code}')

colors = ['#E46E6E', '#FFD635', '#7EED56', '#00CCC0', '#51E9F4', '#94B3FF', '#E4ABFF', '#FF99AA', '#FFB470', '#FFFFFF',
          '#BE0039', '#FF9600', '#00CC78', '#009EAA', '#3690EA', '#6A5CFF', '#B44AC0', '#FF3881', '#9C6926', '#898D90',
          '#6D001A', '#BF4300', '#00A368', '#00756F', '#2450A4', '#493AC1', '#811E9F', '#A00357', '#6D482F', '#000000']


# Преобразуем список цветов в массив RGB
colors_rgb = [tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) for c in colors]

def closest_color(rgb_color, colors_rgb):
    """
    Находит ближайший цвет из списка colors_rgb к заданному цвету rgb_color.
    """
    r1, g1, b1 = rgb_color
    # Вычисляем евклидово расстояние между цветами, приведя значения к float для предотвращения переполнения
    def color_distance(c1, c2):
        return ((float(c1[0]) - float(c2[0])) ** 2 + 
                (float(c1[1]) - float(c2[1])) ** 2 + 
                (float(c1[2]) - float(c2[2])) ** 2) ** 0.5

    # Находим ближайший цвет
    closest = min(colors_rgb, key=lambda c: color_distance(rgb_color, c))
    return closest

def rgb_to_hex(rgb_color):
    """
    Преобразует цвет RGB в формат HEX с заглавными буквами.
    """
    return '#{:02X}{:02X}{:02X}'.format(rgb_color[0], rgb_color[1], rgb_color[2])

def image_to_pixel_array(image_path, top_left, bottom_right):
    # Загрузка изображения
    image = Image.open(image_path).convert('RGB')

    new_size = (bottom_right[0]-top_left[0],bottom_right[1]-top_left[1])

    # Изменение размера до new_size
    resized_image = image.resize(new_size)

    # Преобразуем изображение в массив пикселей
    pixel_data = np.array(resized_image)

    # Итоговый массив для хранения данных о каждом пикселе
    pixel_array = []

    # Проходим по каждому пикселю
    for y in range(new_size[1]):  # Высота изображения
        for x in range(new_size[0]):  # Ширина изображения
            rgb_color = tuple(pixel_data[y, x])
            closest_rgb = closest_color(rgb_color, colors_rgb)  # Находим ближайший цвет
            hex_color = rgb_to_hex(closest_rgb) # Преобразуем RGB в HEX
            pixel_array.append([top_left[1]*1024+y*1024 + top_left[0]+(x + 1), hex_color])

    return pixel_array

def all_for_picture(url,x,y,size):
    image_path = url[36:]

    download_image_with_timestamp(url, image_path)
    top_left = (int(x), int(y))  # Начальные координаты обрезки (левый верхний угол)
    bottom_right = (int(x)+size,int(y)+size)  # Конечные координаты обрезки (правый нижний угол)

    result = image_to_pixel_array(image_path, top_left, bottom_right)

    global elements
    elements = result


"""all_for_picture"""

lock = asyncio.Lock()

self_tg_client = SelfTGClient()

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.first_name = None
        self.last_name = None
        self.fullname = None
        self.start_param = None
        self.peer = None
        self.first_run = None
        self.game_service_is_unavailable = False
        self.balance = 0

        self.session_ug_dict = self.load_user_agents() or []

        headers['User-Agent'] = self.check_user_agent()

    async def generate_random_user_agent(self):
        return generate_random_user_agent(device_type='android', browser_type='chrome')

    
    def info(self, message):
        from bot.utils import info
        info(f"<light-yellow>{self.session_name}</light-yellow> | ℹ️ {message}")

    def debug(self, message):
        from bot.utils import debug
        debug(f"<light-yellow>{self.session_name}</light-yellow> | ⚙️ {message}")

    def warning(self, message):
        from bot.utils import warning
        warning(f"<light-yellow>{self.session_name}</light-yellow> | ⚠️ {message}")
        
    def error(self, message):
        from bot.utils import error
        error(f"<light-yellow>{self.session_name}</light-yellow> | 😢 {message}")

    def critical(self, message):
        from bot.utils import critical
        critical(f"<light-yellow>{self.session_name}</light-yellow> | 😱 {message}")

    def success(self, message):
        from bot.utils import success
        success(f"<light-yellow>{self.session_name}</light-yellow> | ✅ {message}")

    def save_user_agent(self):
        user_agents_file_name = "user_agents.json"

        if not any(session['session_name'] == self.session_name for session in self.session_ug_dict):
            user_agent_str = generate_random_user_agent()

            self.session_ug_dict.append({
                'session_name': self.session_name,
                'user_agent': user_agent_str})

            with open(user_agents_file_name, 'w') as user_agents:
                json.dump(self.session_ug_dict, user_agents, indent=4)

            self.success(f"user-agent успешно настроен!")

            return user_agent_str

    def load_user_agents(self):
        user_agents_file_name = "user_agents.json"

        try:
            with open(user_agents_file_name, 'r') as user_agents:
                session_data = json.load(user_agents)
                if isinstance(session_data, list):
                    return session_data

        except FileNotFoundError:
            logger.warning("Не найден файл с user-agents.. Создаём новый.")

        except json.JSONDecodeError:
            logger.warning("Файл с user-agents пустой или имеет неверный формат..")

        return []

    def check_user_agent(self):
        load = next(
            (session['user_agent'] for session in self.session_ug_dict if session['session_name'] == self.session_name),
            None)

        if load is None:
            return self.save_user_agent()

        return load

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            if settings.USE_REF == True and settings.REF_ID is not None:
                ref_id = settings.REF_ID
            else:
                ref_id = 'f7505768028'

            self.start_param = random.choices([ref_id, 'f7505768028'], weights=[90, 10])[0]

            peer = await self.tg_client.resolve_peer('notpixel')
            InputBotApp = types.InputBotAppShortName(bot_id=peer, short_name="app")

            web_view = await self_tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotApp,
                platform='android',
                write_allowed=True,
                start_param=self.start_param
            ), self)

            auth_url = web_view.url

            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            try:
                if self.user_id == 0:
                    information = await self.tg_client.get_me()
                    self.user_id = information.id
                    self.first_name = information.first_name or ''
                    self.last_name = information.last_name or ''
                    self.username = information.username or ''
            except Exception as e:
                print(e)

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            self.error(
                f"Ошибка по время авторизации: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            self.info(f"Proxy IP: {ip}")
        except Exception as error:
            self.error(f"Proxy: {proxy} | Error: {error}")

    async def get_user_info(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get("https://notpx.app/api/v1/users/me", timeout=10, ssl=settings.ENABLE_SSL)

            response.raise_for_status()

            data = await response.json()

            return data
        except Exception as error:
            self.error(f"{self.session_name} | Ошибка при получении user-info: <light-yellow>{error}</light-yellow>")
            return None

    async def get_balance(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL, timeout=10)

            response.raise_for_status()

            data = await response.json()
            self.balance = data['userBalance']
            return data['userBalance']
        except Exception as error:
            self.error(f"Ошибка при попытке получения баланса: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)
            return None

    async def get_templates_coordinates(self, http_client: aiohttp.ClientSession):
        try:
            response_for_template = await http_client.get('https://notpx.app/api/v1/tournament/template/'+str(TEMPLATE_ID), ssl=settings.ENABLE_SSL, timeout=10)
            response_for_template.raise_for_status()
            data_template = await response_for_template.json()
            
            self.info(f"Загружаю шаблон: <cyan>{TEMPLATE_ID}</cyan>")

            await lock.acquire() 
            all_for_picture(data_template['url'], int(data_template['x']),int(data_template['y']), int(data_template['imageSize'])-1)
            lock.release()

            await asyncio.sleep(delay=random.uniform(20, 50))
        except Exception as error:
            self.error(f"Ошибка при попытке загрузки шаблона: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)


    async def draw(self, http_client: aiohttp.ClientSession):
        flag = False
        try:
            response = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL, timeout=10)

            response.raise_for_status()

            data = await response.json()

            charges = data['charges']

            self.balance = data['userBalance']

            
            if charges > 0:
                self.info(f"Energy: <cyan>{charges}</cyan> ⚡️")
            else:
                self.info(f"No energy ⚡️")

            for _ in range(charges):
                    
                while True:

                    el = random.choice(elements)

                    pixelid = el[0]
                    pixelcolor = el[1]
                    payload = {
                        "pixelId": int(pixelid),
                        "newColor": pixelcolor
                    }

                    await lock.acquire() 
                    flag = True
                    resp = await http_client.get(f'https://notpx.app/api/v1/image/get/{pixelid}', ssl=settings.ENABLE_SSL)
                    data = await resp.json()
                    color = data['pixel']['color']
                    
                    if color != pixelcolor:
                        break
                    else:
                        flag = False
                        lock.release()

                draw_request = await http_client.post(
                    'https://notpx.app/api/v1/repaint/start',
                    json=payload,
                    ssl=settings.ENABLE_SSL
                )
                
                x = data['pixel']['x']
                y = data['pixel']['y']
                draw_request.raise_for_status()
                data = await draw_request.json()

                self.success(f"Закрашен пиксель <cyan>{x} {y}</cyan> из <light-blue>{color}</light-blue> в цвет <light-blue>{pixelcolor}</light-blue> + {int(data['balance']-self.balance)}PX 🎨️")
                
                flag = False
                lock.release()

                await asyncio.sleep(delay=random.uniform(5, 10))
                
        except Exception as error:
            if flag:
                lock.release()
            self.error(f"Ошибка при попытке закрасить пиксель: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)

    async def upgrade(self, http_client: aiohttp.ClientSession):
        try:
            while True:
                response = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

                response.raise_for_status()

                data = await response.json()

                boosts = data['boosts']

                for name, level in sorted(boosts.items(), key=lambda item: item[1]):
                    if name not in settings.BOOSTS_BLACK_LIST:
                        try:
                            res = await http_client.get(f'https://notpx.app/api/v1/mining/boost/check/{name}', ssl=settings.ENABLE_SSL)

                            res.raise_for_status()

                            self.success(f"Улучшен boost: <cyan>{name}</<cyan> ⬆️")

                            await asyncio.sleep(delay=random.randint(2, 5))
                        except Exception as error:
                            self.warning(f"Не хватает $PX для улучшений. 💰")

                            await asyncio.sleep(delay=random.randint(5, 10))
                            return

        except Exception as error:
            self.error(f"Ошибка при попытке апгрейда: <light-yellow>{error}</light-yellow>")
            await asyncio.sleep(delay=3)

    async def run_tasks(self, http_client: aiohttp.ClientSession):
        try:
            res = await http_client.get('https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL)

            res.raise_for_status()

            data = await res.json()

            tasks = data['tasks'].keys()

            for task in settings.TASKS_TODO_LIST:
                if task not in tasks:
                    if re.search(':', task) is not None:
                        split_str = task.split(':')
                        social = split_str[0]
                        name = split_str[1]

                        if social == 'channel' and settings.ENABLE_JOIN_TG_CHANNELS:
                            try:
                                if not self.tg_client.is_connected:
                                    await self.tg_client.connect()
                                await self.tg_client.join_chat(task)
                                await self.tg_client.disconnect()
                                await asyncio.sleep(delay=random.randint(3, 5))
                                self.success(f"Успешно присоединились к <cyan>{task}</cyan> channel ✔️")
                            except Exception as error:
                                self.error(f"Ошибка при присоединении к каналу {task}: <light-yellow>{error}</light-yellow>")

                        response = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{social}?name={name}', ssl=settings.ENABLE_SSL)
                    else:
                        response = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{task}', ssl=settings.ENABLE_SSL)

                    response.raise_for_status()

                    data = await response.json()

                    status = data[task]

                    if status:
                        self.success(f"Задача <cyan>{task}</cyan> успешно выполнена!")

                        current_balance = await self.get_balance(http_client=http_client)

                        if current_balance is None:
                            self.info(f"Текущий баланс: Unknown 🔳")
                        else:
                            self.info(f"Текущий баланс: <light-green>{'{:,.3f}'.format(current_balance)}</light-green> 🔳")
                    else:
                        self.warning(f"Требования для выполнения <cyan>{task}</cyan> не выполнены!")

                    await asyncio.sleep(delay=random.randint(3, 7))

        except Exception as error:
            self.error(f"Ошибка при выполнении задачи: <light-yellow>{error}</light-yellow>")

    async def claim_mine(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(f'https://notpx.app/api/v1/mining/status', ssl=settings.ENABLE_SSL, timeout=10)

            response.raise_for_status()

            response_json = await response.json()

            await asyncio.sleep(delay=random.randint(4, 6))

            for _ in range(2):
                try:
                    response = await http_client.get(f'https://notpx.app/api/v1/mining/claim', ssl=settings.ENABLE_SSL)

                    response.raise_for_status()

                    response_json = await response.json()
                except Exception as error:
                    self.info(f"First claiming not always successful, retrying..")
                else:
                    break

            return response_json['claimed']
        except Exception as error:
            self.error(f"Ошибка при получении награды: <light-yellow>{error}</light-yellow>")

            await asyncio.sleep(delay=3)

    async def run(self, proxy: str | None) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = random.randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            self.info(f"Бот будет запущен через <ly>{random_delay} секунд</ly>")
            await asyncio.sleep(random_delay)

        access_token = None
        refresh_token = None
        login_need = True

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)

        access_token_created_time = 0
        token_live_time = random.randint(500, 900)

        while True:
            try:
                if time() - access_token_created_time >= token_live_time:
                    login_need = True

                if login_need:
                    if "Authorization" in http_client.headers:
                        del http_client.headers["Authorization"]

                    tg_web_data = await self.get_tg_web_data(proxy=proxy)

                    http_client.headers['Authorization'] = f"initData {tg_web_data}"

                    access_token_created_time = time()
                    token_live_time = random.randint(500, 900)

                    if self.first_run is not True:
                        self.success("Успешная авторизация!")
                        self.first_run = True

                    login_need = False

                await asyncio.sleep(delay=3)

            except Exception as error:
                self.error(f"Ошибка при попытке авторизации: <light-yellow>{error}</light-yellow>")
                await asyncio.sleep(delay=3)
                break

            try:
                user = await self.get_user_info(http_client=http_client)
                
                await asyncio.sleep(delay=2)

                if user is not None:
                    current_balance = await self.get_balance(http_client=http_client)

                    if current_balance is None:
                        self.info(f"Текущий баланс: Unknown 🔳")
                    else:
                        self.info(f"Текущий баланс: <light-green>{'{:,.3f}'.format(current_balance)}</light-green> 🔳")

                    if settings.ENABLE_AUTO_DRAW:
                        await self.get_templates_coordinates(http_client=http_client)

                    if settings.ENABLE_AUTO_DRAW:
                        await self.draw(http_client=http_client)

                    if settings.ENABLE_AUTO_UPGRADE:
                        status = await self.upgrade(http_client=http_client)
                        if status is not None:
                            self.info(f"Получена награда: <light-green>{status}</light-green> ✔️")

                    if settings.ENABLE_CLAIM_REWARD:
                        reward = await self.claim_mine(http_client=http_client)
                        if reward is not None:
                            self.info(f"Получена награда: <light-green>{'{:,.3f}'.format(reward)}</light-green> 🔳")

                    if settings.ENABLE_AUTO_TASKS:
                        await self.run_tasks(http_client=http_client)

                sleep_time = random.randint(settings.SLEEP_TIME_IN_MINUTES[0], settings.SLEEP_TIME_IN_MINUTES[1])

                self.info(f"АФК {sleep_time} минут до повторного фарма.. 💤")

                await asyncio.sleep(delay=sleep_time*60)

            except Exception as error:
                self.error(f"Неизвестная ошибка: <light-yellow>{error}</light-yellow>")

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        self.error(f"{tg_client.name} | Нерабочая сессия!")
