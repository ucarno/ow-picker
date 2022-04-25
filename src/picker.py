import atexit
import json
import logging
from threading import Thread
from time import sleep

import pyautogui
from PIL import ImageGrab
from PyQt6.QtWidgets import QApplication
import keyboard

from constants import HERO_ROLES, LOCALES, ROLE_POINTS, POINT_CHECK_INDEXES, POINT_COLOR
from gui import GUI
from utils import get_foreground_window_title, get_file_content


class Locale:
    def __init__(self, code: str, translations: dict):
        self.code = code
        self._translations = translations
        self.name = self._translations['locale_name']
        self.ui = self._translations['ui']
        self.heroes = self._translations['heroes']


class Config:
    def __init__(self):
        try:
            self._config = json.loads(open('config.json', 'r', encoding='utf-8').read())
        except FileNotFoundError:
            self._config = {'hero': 'ana', 'language': 'en', 'hotkey': 'ctrl+w'}

    @property
    def hero(self):
        return self._config['hero']

    @hero.setter
    def hero(self, value):
        self._config['hero'] = value

    @property
    def language(self):
        return self._config['language']

    @language.setter
    def language(self, value):
        self._config['language'] = value

    @property
    def hotkey(self):
        return self._config['hotkey']

    @hotkey.setter
    def hotkey(self, value):
        self._config['hotkey'] = value

    def save(self):
        with open('config.json', 'w+', encoding='utf-8') as f:
            json.dump(self._config, f)
            f.close()


_locales = {
    loc: Locale(
        code=loc,
        translations=json.loads(get_file_content(f'resources/translations/{loc}.json'))
    ) for loc in LOCALES
}


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s | %(asctime)s] - %(message)s',
    datefmt='%H:%M:%S'
)


class Hero:
    def __init__(self, hero_id: str, role: str, locales):
        self.id = hero_id
        self.role = role
        self._locales = locales

    def get_localized_name(self, locale: str):
        return self._locales[locale].heroes[self.id]


class Picker:
    def __init__(self):
        self.state = False

        self.heroes = {}
        for role, heroes_list in HERO_ROLES.items():
            for hero in heroes_list:
                self.heroes[hero] = Hero(hero, role, _locales)

        self.config = Config()
        atexit.register(self.at_exit)

        self.hotkey_thread = Thread(target=keyboard.wait, daemon=True)
        self.picker_thread = Thread(target=self.picker_loop, daemon=True)

        self.heroes_points = {}
        self.role_points_to_check = tuple()
        self.set_heroes_points()

        self.gui_app = QApplication([])
        self.gui = GUI(
            state_callback=self.on_gui_state_change,
            heroes=list(self.heroes.values()),
            hero_default=self.config.hero,
            hero_callback=self.on_gui_hero_change,
            locale_callback=self.on_gui_locale_change,
            locales=_locales,
            locale_code=self.config.language
        )

    def set_heroes_points(self):
        role_points = ROLE_POINTS[self.heroes[self.config.hero].role]
        self.role_points_to_check = [role_points[i] for i in POINT_CHECK_INDEXES]

        for role, role_points in ROLE_POINTS.items():
            role_heroes = list(sorted(
                filter(lambda hero: hero.role == role, self.heroes.values()),
                key=lambda hero: hero.get_localized_name(self.config.language)
            ))
            for h, point in zip(role_heroes, role_points):
                self.heroes_points[h.id] = point

    @property
    def is_game_open(self) -> bool:
        return get_foreground_window_title() == 'Overwatch'

    def picker_loop(self):
        while True:
            if self.state and self.is_game_open:
                image = ImageGrab.grab()
                check_result = tuple(image.getpixel((x, y)) == POINT_COLOR for x, y in self.role_points_to_check)
                if check_result.count(True) >= 2:
                    logging.info('Hero selection screen caught! Selecting hero...')
                    pyautogui.doubleClick(*self.heroes_points[self.config.hero], interval=0.0001)
                    self.state = False
                    self.gui.set_state(False)
            sleep(0.001)

    def start_gui(self):
        self.gui.init_ui()
        self.gui.show()
        self.gui_app.exec()

    def start(self):
        self.picker_thread.start()
        self.hotkey_thread.start()
        self.register_hotkey()

        self.start_gui()

    def set_state(self, state: bool):
        self.state = state
        self.gui.state_button.blockSignals(True)
        self.gui.set_state(self.state)
        self.gui.state_button.blockSignals(False)

    def unregister_hotkey(self):
        logging.info(f'Unregistering hotkey \'{self.config.hotkey}\'')
        keyboard.remove_hotkey(self.config.hotkey)

    def register_hotkey(self):
        logging.info(f'Registering hotkey \'{self.config.hotkey}\'')
        keyboard.add_hotkey(self.config.hotkey, self.on_hotkey)

    def on_hotkey(self):
        logging.info(f'(Hotkey) State switched to {not self.state}')
        self.set_state(not self.state)

    def on_gui_locale_change(self, language_code: str):
        logging.info(f'(GUI) Locale set to `{language_code}`')
        self.config.language = language_code
        self.set_heroes_points()

    def on_gui_hero_change(self, hero: Hero):
        logging.info(f'(GUI) Hero switched to `{hero.id}`')
        self.config.hero = hero.id

    def on_gui_hotkey_change(self, hotkey: str):
        logging.info(f'(GUI) Hotkey changed to \'{hotkey}\'')
        self.unregister_hotkey()
        self.config.hotkey = hotkey
        self.register_hotkey()

    def on_gui_state_change(self, state: bool):
        logging.info(f'(GUI) Received global state {state}')
        self.state = state

    def at_exit(self):
        logging.info('Saving config and exiting...')
        self.config.save()
        logging.info('Bye!')
