from PyQt6.QtCore import QSize
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QButtonGroup, \
    QHBoxLayout, QSpacerItem, QFrame, QMenu


class QHLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Raised)


class LocaleAction(QAction):
    def __init__(self, name, code):
        super().__init__(f'&{name}')
        self.code = code
        self.setCheckable(True)


class StateButton(QPushButton):
    COLOR_TEXT_ACTIVE = (41, 176, 1)
    COLOR_TEXT_INACTIVE = (173, 26, 1)
    COLOR_ACTIVE = (117, 217, 87)
    COLOR_INACTIVE = (219, 84, 59)

    def __init__(self):
        super().__init__()

        self.setCheckable(True)
        self.setFixedSize(QSize(100, 30))

        self.setStyleSheet(
            f"""
            QPushButton {{
                border: 2px solid;
                color: rgb{self.COLOR_TEXT_INACTIVE};
                background-color: rgba{self.get_inactive_color(0.25)};
                border-color: rgba{self.get_inactive_color(0.25)};
            }}

            QPushButton::hover {{
                background-color: rgba{self.get_inactive_color(0.5)};
            }}
            
            /* QPushButton::pressed {{
                background-color: rgba{self.get_inactive_color(0.7)};
            }} */

            QPushButton::checked {{
                color: rgb{self.COLOR_TEXT_ACTIVE};
                background-color: rgba{self.get_active_color(0.25)};
                border-color: rgba{self.get_active_color(0.25)};
            }}
            
            QPushButton::checked::hover {{
                background-color: rgba{self.get_active_color(0.5)};
            }}
            
            /* QPushButton::checked::pressed {{
                background-color: rgba{self.get_active_color(0.7)};
            }} */
            """
        )

    def get_active_color(self, alpha: float):
        return self.COLOR_ACTIVE + (alpha,)

    def get_inactive_color(self, alpha: float):
        return self.COLOR_INACTIVE + (alpha,)


class GUI(QMainWindow):
    def __init__(self, state_callback, heroes, hero_default, hero_callback, locale_callback, locales, locale_code):
        super().__init__()

        self.setWindowTitle('Overwatch Auto Picker')
        self.setFixedSize(QSize(825, 426))
        # self.setStyleSheet('background-color: #2b2b2b;')  # dark mode

        self.state = False
        self.state_callback = state_callback
        self.state_button = StateButton()
        self.state_button.toggled.connect(self.on_state_change)

        self.locales = locales
        self.locale_code = locale_code
        self.locale_callback = locale_callback

        self.heroes = heroes
        self.buttons = [HeroButton.from_hero(
            hero=h,
            locales=self.locales,
            is_checked=h.id == hero_default
        ) for h in self.heroes]
        self.hero_callback = hero_callback

        self.hero_button_group = QButtonGroup()
        self.hero_button_group.buttonToggled.connect(self.on_hero_change)
        self.hero_button_group.setExclusive(True)

        for btn in self.buttons:
            self.hero_button_group.addButton(btn)

        self.init_menu()

    def init_menu(self):
        menu_bar = self.menuBar()
        locale_menu = QMenu("&Language", self)

        locale_action_group = QActionGroup(locale_menu)
        locale_action_group.setExclusive(True)

        actions = [LocaleAction(loc.name, loc.code) for loc in sorted(self.locales.values(), key=lambda i: i.name)]
        for a in actions:
            a.setChecked(a.code == self.locale_code)
            locale_action_group.addAction(a)
            locale_menu.addAction(a)

        locale_action_group.triggered.connect(self.on_locale_change)
        menu_bar.addMenu(locale_menu)

    def init_ui(self):
        main_layout = QVBoxLayout()

        tank_layout = QHBoxLayout()
        attack_0_layout = QHBoxLayout()
        attack_1_layout = QHBoxLayout()
        support_layout = QHBoxLayout()

        main_layout.addLayout(tank_layout)
        main_layout.addSpacerItem(QSpacerItem(0, 16))

        main_layout.addLayout(attack_0_layout)
        main_layout.addSpacerItem(QSpacerItem(0, 10))

        main_layout.addLayout(attack_1_layout)
        main_layout.addSpacerItem(QSpacerItem(0, 16))

        main_layout.addLayout(support_layout)
        main_layout.addSpacerItem(QSpacerItem(0, 16))

        main_layout.addWidget(QHLine())
        main_layout.addSpacerItem(QSpacerItem(0, 12))
        # main_layout.addStretch()
        main_layout.setSpacing(0)

        layouts = [
            tank_layout,
            attack_0_layout,
            attack_1_layout,
            support_layout
        ]
        for lo in layouts:
            lo.addStretch()
            lo.setSpacing(8)

        buttons = {
            role: sorted(
                filter(lambda button: button.hero.role == role, self.buttons),
                key=lambda button: button.hero.get_localized_name(self.locale_code)
            ) for role in ('tank', 'attack', 'support')
        }
        for btn in self.buttons:
            btn.set_tooltip(self.locale_code)

        for btn in buttons['tank']:
            tank_layout.addWidget(btn)

        for btn in buttons['attack'][:9]:
            attack_0_layout.addWidget(btn)

        for btn in buttons['attack'][9:]:
            attack_1_layout.addWidget(btn)

        for btn in buttons['support']:
            support_layout.addWidget(btn)

        for lo in layouts:
            lo.addStretch()

        main_layout.addWidget(self.state_button)
        self.set_state(self.state)

        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)

    def get_current_locale(self):
        return self.locales[self.locale_code]

    def set_state(self, state: bool):
        self.state = state
        text_key = 'state_active' if state else 'state_inactive'
        new_text = self.get_current_locale().ui[text_key] + ('!' if state else '...')
        self.state_button.setText(new_text)
        self.state_button.setChecked(state)

    def on_state_change(self, state):
        self.state_callback(state)
        self.set_state(state)

    def on_hero_change(self, button: 'HeroButton', value: bool):
        if value:
            self.hero_callback(button.hero)

    def on_locale_change(self, action: LocaleAction):
        new_code = action.code
        if new_code != self.locale_code:
            self.locale_code = new_code
            self.init_ui()
            self.locale_callback(new_code)


class HeroButton(QPushButton):
    BACKGROUND_COLOR = (255, 255, 255)

    def __init__(self, hero, locales, is_checked: bool = False):
        super().__init__()
        self.hero = hero
        self._locales = locales

        self.setFixedSize(QSize(75, 68))
        self.setCheckable(True)
        self.setChecked(is_checked)

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-image: url({self.get_portrait_path()});
                background-color: rgba{self.get_background_color(0.25)};
                border: 2px solid;
                border-color: rgba{self.get_background_color(0.25)};
            }}

            QPushButton::hover {{
                background-color: rgba{self.get_background_color(0.5)};
            }}
            
            /* QPushButton::pressed {{
                background-color: rgba{self.get_background_color(0.7)};
            }} */

            QPushButton::checked {{
                background-color: rgba{self.get_background_color(1.0)};
            }}
            """
        )

    @staticmethod
    def from_hero(hero, locales, is_checked: bool = False):
        return {
            'tank': TankHeroButton,
            'attack': AttackHeroButton,
            'support': SupportHeroButton
        }[hero.role](hero, locales, is_checked)

    def get_portrait_path(self):
        return f'resources/portraits/{self.hero.id}.webp'

    def set_tooltip(self, locale: str):
        self.setToolTip(self.hero.get_localized_name(locale))

    def get_background_color(self, alpha: float = 1.0):
        return self.BACKGROUND_COLOR + (alpha,)


class TankHeroButton(HeroButton):
    BACKGROUND_COLOR = (94, 129, 255)


class AttackHeroButton(HeroButton):
    BACKGROUND_COLOR = (255, 137, 137)


class SupportHeroButton(HeroButton):
    # BACKGROUND_COLOR = (141, 212, 97)
    BACKGROUND_COLOR = (219, 211, 75)
