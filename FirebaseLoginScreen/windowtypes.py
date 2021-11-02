from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.scrollview import ScrollView
from kivymd.uix.list import OneLineAvatarListItem, ImageLeftWidget, MDList
import kivy.utils
from functools import partial


class WindowTypes(GridLayout):
    rows = 1

    def __init__(self, **kwargs):
        super().__init__()

        with self.canvas.before:
            self.canvas_color = Color(rgb=kivy.utils.get_color_from_hex("64E6F8"))
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.scroll = ScrollView()
        self.list_view = MDList()

        # At the moment there are only 4 types of windows
        for i in range(4):
            # i = window_type
            try:
                image = ImageLeftWidget(source=f".img/icon_window{i+1}.png")
                onelineavataritem = OneLineAvatarListItem(text=f"Type {i+1}",
                                                          on_release=partial(App.get_running_app().update_window_type_image, i+1))
                onelineavataritem.add_widget(image)
                self.list_view.add_widget(onelineavataritem)

            except Exception as e:
                print(e)

        self.scroll.add_widget(self.list_view)
        self.add_widget(self.scroll)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
