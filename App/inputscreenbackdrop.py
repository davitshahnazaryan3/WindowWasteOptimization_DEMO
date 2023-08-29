from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
import kivy.utils
from kivy.uix.scrollview import ScrollView

KV = ('''
#:import Window kivy.core.window.Window
#:import IconLeftWidget kivymd.uix.list.IconLeftWidget
#:import C kivy.utils.get_color_from_hex

<MyBackdropBackLayer@ScrollView>


<MyBackdropFrontLayer@Screen>


<InputBackdrop>
    MDBackdrop:
        id: backdrop
        left_action_items: [['transfer-down', lambda x: self.open()]]
        on_open: app.create_window_list()
        title: "Select Window Type"
        radius_left: "25dp"
        radius_right: "0dp"
        header_text: "Window Selected:"

        MDBackdropBackLayer:
            MyBackdropBackLayer:
                id: container

        MDBackdropFrontLayer:
            MyBackdropFrontLayer:
                id: frontlayer
''')


class InputBackdrop(Screen):
    pass


class InputScreenBackDropLayout(FloatLayout):
    def run(self):
        Builder.load_string(KV)
        return InputBackdrop()
