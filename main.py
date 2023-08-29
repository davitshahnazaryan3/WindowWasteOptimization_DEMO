from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, ObjectProperty,\
    NumericProperty, DictProperty
from kivy.uix.screenmanager import NoTransition, CardTransition
from App.inputscreenbackdrop import InputScreenBackDropLayout
from App.windowtypes import WindowTypes
from kivy.uix.image import Image
from App.config import settings


Window.size = (500, 750)

LabelBase.register(name="Roboto",
                   fn_regular="Roboto/Roboto-Regular.ttf",
                   fn_bold="Roboto/Roboto-Medium.ttf",
                   fn_italic="Roboto/Roboto-MediumItalic.ttf")
Window.clearcolor = get_color_from_hex("#101216")


class Main(MDApp):
    # User information
    user_idToken = StringProperty("")
    local_id = StringProperty("")
    # Title of project
    title = "Euro Optimization"
    # Profile library, default for user
    profile_lib = {"Typical": 6.0}

    # Number of edges of selected window, defaulting to 2 for Window type 1
    edges = DictProperty({"1": 0, "2": 0})

    # Backdrop layout for window type selection and display
    windowtypebackdrop = ObjectProperty(None)
    window_type = NumericProperty(1)

    # Dialog for popup
    dialog = None

    # Wep API key
    web_api_key = settings.wep_api_key

    def on_start(self):
        # Instantiate window type backdrop layout
        self.windowtypebackdrop = InputScreenBackDropLayout().run()
        self.root.ids.firebase_login_screen.ids.input_screen.ids\
            .window_backdrop.add_widget(self.windowtypebackdrop)

    def sign_out(self):
        self.show_alert_dialog()

    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Are you sure?",
                text="All progress will be saved.",
                size_hint=(.5, None),
                buttons=[
                    MDFlatButton(text="Cancel",
                                 text_color=self.theme_cls.primary_color,
                                 on_release=self.close_dialog),
                    MDFlatButton(text="Log Out",
                                 text_color=self.theme_cls.primary_color,
                                 on_release=self.dismiss_callback)
                ]
            )
        self.dialog.get_normal_height()
        self.dialog.open()

    def dismiss_callback(self, inst):
        self.root.ids.firebase_login_screen.log_out()
        self.root.current = 'firebase_login_screen'
        self.dialog.dismiss()

    def close_dialog(self, inst):
        self.dialog.dismiss()

    def change_screen(self, screen_name, direction='forward', mode=''):
        screen_manager = self.root.ids.firebase_login_screen.ids.screen_manager

        if direction == 'None':
            screen_manager.transition = NoTransition()
            screen_manager.current = screen_name
            return

        screen_manager.transition = CardTransition(
            direction=direction, mode=mode)
        screen_manager.current = screen_name

    def create_window_list(self):
        window_list = self.windowtypebackdrop.ids.container

        window_list.clear_widgets()

        windows_types = WindowTypes()
        window_list.add_widget(windows_types)

    def update_window_type_image(self, window_type, widget):
        self.window_type = window_type

        # Clear existing image in front layer
        try:
            self.windowtypebackdrop.ids.frontlayer.clear_widgets()
            # Update with new image
            self.windowtypebackdrop.ids.frontlayer.add_widget(
                Image(source=f".img/window{window_type}.png",
                      allow_stretch=False, keep_ratio=True))
            if window_type == 1:
                self.edges = {"1": 0, "2": 0}
            elif window_type == 2:
                self.edges = {"1": 0, "2": 0, "3": 0}
            elif window_type == 3:
                self.edges = {"1": 0, "2": 0, "3": 0}
            elif window_type == 4:
                self.edges = {"1": 0, "2": 0, "3": 0, "4": 0}
            else:
                print("Wrong Window type")
        except Exception:
            # Defaulting to Window type 1
            self.edges = {"1": 0, "2": 0}


if __name__ == '__main__':
    Main().run()
