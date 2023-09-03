from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.properties import BooleanProperty, StringProperty, NumericProperty,\
    ObjectProperty
from kivy.event import EventDispatcher
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

# Additional dependencies
import certifi
from json import dumps
import os.path
import pyrebase
from datetime import datetime

# For Snackbar
from kivymd.uix.snackbar import Snackbar
from App.accordion import Accordion, AccordionItem
from App.specialbuttons import LabelButton, ImageButton
from model.model_optimization import ModelOptimization

# KivyMD imports
from kivymd.toast import toast

# Python imports
import sys
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from App.config import settings

sys.path.append("/".join(x for x in __file__.split("/")[:-1]))

# Load the kv files
folder = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(folder + "/signinscreen.kv")
Builder.load_file(folder + "/signupscreen.kv")
Builder.load_file(folder + "/welcomescreen.kv")
Builder.load_file(folder + "/loadingpopup.kv")
Builder.load_file(folder + "/firebaseloginscreen.kv")
Builder.load_file(folder + "/inputscreen.kv")
Builder.load_file(folder + "/inventoryscreen.kv")
Builder.load_file(folder + "/analysisscreen.kv")
Builder.load_file(folder + "/sessionscreen.kv")
Builder.load_file(folder + "/drawingspace.kv")
Builder.load_file(folder + "/profilescreen.kv")

# Pyrebase
firebaseConfig = {
    "apiKey": settings.apiKey,
    "authDomain": settings.authDomain,
    "databaseURL": settings.databaseURL,
    "projectId": settings.projectId,
    "storageBucket": settings.storageBucket,
    "messagingSenderId": settings.messagingSenderId,
    "appId": settings.appId,
    "measurementId": settings.measurementId,
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# Windows dictionary
windows = {}
windows_ids = []
app = App.get_running_app()
# Temporary window while incomplete
window_temp = {"type": 1, "side": {"length": [None], "profile": [None]},
               "quantity": 0}


def binary_search_iterative(arr, x):
    """Returns index of x in given array arr if present, else returns -1"""
    low = 0
    high = len(arr) - 1
    mid = 0

    while low <= high:
        mid = (high + low) // 2

        # means x is present at mid
        if arr[mid] == x:
            return mid

        # if x is greater, ignore left half
        elif arr[mid] > x:
            high = mid - 1

        # If x is smaller, ignore right half
        else:
            low = mid + 1

    # Element not present
    return -1


class ProfileUnique(BoxLayout):
    local_id = StringProperty("")
    id_token = StringProperty("")

    def __init__(self, **kwargs):
        super(ProfileUnique, self).__init__(**kwargs)

    def add_profile(self):
        x1 = self.name.text
        x2 = self.length.text

        # For non-empty cells
        if x1 != "" and x2 != "":
            if x1 not in app.profile_lib:
                # Create the row if it is not created yet
                self.parent.add_widget(ProfileUniqueCreated(
                    x1, x2, self.local_id, self.id_token), index=0)
                # Add into the library of profiles
                app.profile_lib[x1] = x2
                # Add profile to database
                db.child("users").child(self.local_id).child("Profiles").\
                    child(x1).set(x2, self.id_token)

            else:
                # Alert
                Snackbar(text=f"Profile: {x1} exists!").open()
        else:
            Snackbar(text="Profile properties missing!").open()

    def clear_inputs(self, text_inputs):
        for text_input in text_inputs:
            text_input.text = ""


class ProfileUniqueCreated(BoxLayout):
    x1 = StringProperty("")
    x2 = StringProperty("")
    local_id = StringProperty("")
    id_token = StringProperty("")

    def __init__(self, x1, x2, local_id, id_token, **kwargs):
        super(ProfileUniqueCreated, self).__init__(**kwargs)
        self.x1 = x1
        self.x2 = x2
        self.local_id = local_id
        self.id_token = id_token

    def remove_row(self):
        self.parent.remove_widget(self)
        app.profile_lib.pop(self.x1, None)
        db.child("users").child(self.local_id).child("Profiles").\
            child(self.x1).remove(self.id_token)


class ProfileScreen(Screen):
    local_id = StringProperty("")
    id_token = StringProperty("")
    profiles_shown = False

    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        if not self.profiles_shown:
            profiles = db.child("users").child(self.local_id).\
                child("Profiles").get(self.id_token)

            if profiles.each():
                for profile in profiles.each():
                    x1 = profile.key()
                    x2 = profile.val()
                    # Create the row if it is not created yet
                    self.ids.grid.add_widget(ProfileUniqueCreated(
                        x1, x2, self.local_id, self.id_token), index=0)
                    # Add into the library of profiles
                    app.profile_lib[x1] = x2
            self.profiles_shown = True


class SessionRow(Screen):
    label = StringProperty("")
    session_id = StringProperty("")

    def __init__(self, date, **kwargs):
        super(SessionRow, self).__init__(**kwargs)
        self.session_id = date
        self.label = date[1:3] + "-" + date[3:5] + "-" + date[5:9] + ", " \
            + date[9:11] + ":" + date[11:13] + ":" + date[13:]


class SessionScreen(Screen):
    local_id = StringProperty("")
    id_token = StringProperty("")
    session = StringProperty("")

    def __init__(self, **kwargs):
        super(SessionScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        # Get all existing sessions
        sessions = db.child("users").child(self.local_id).get(self.id_token)
        cnt = 0
        for session in sessions.each():
            if session.key() != "Profiles":
                # add session date, and Continue button
                self.ids.grid.add_widget(SessionRow(session.key()), index=cnt)
                cnt += 1
            else:
                # Get profile library
                profiles = session.val()
                app.profile_lib.update(profiles)

    def on_pre_leave(self, *args):
        self.ids.grid.clear_widgets()

    def get_windows_ids(self):
        global windows_ids

        window_db = db.child("users").child(self.local_id).\
            child(self.session).child("Windows").get(self.id_token)
        if window_db.each() is not None:
            for window in window_db.each():
                if window.val() is not None:
                    windows_ids.append(str(window.key()))

    def generate_session(self):
        now = datetime.now()
        self.session = now.strftime("s%d%m%Y%H%M%S")

    def continue_session(self, session_id):
        """
        Use current session ID.
        Update global variable windows_ids.
        """
        self.session = session_id
        self.get_windows_ids()


class SignInScreen(Screen):
    def go_back(self):
        self.parent.transition = SlideTransition(direction="right")
        self.parent.current = self.parent.current = "welcome_screen"
        self.parent.transition = SlideTransition(direction="left")


class SignUpScreen(Screen):
    def go_back(self):
        self.parent.transition = SlideTransition(direction="right")
        self.parent.current = self.parent.current = "welcome_screen"
        self.parent.transition = SlideTransition(direction="left")


class WelcomeScreen(Screen):
    pass


class InputScreen(Screen):
    drawing_space = ObjectProperty(None)
    local_id = StringProperty("")
    id_token = StringProperty("")

    id_window = 1
    edge_id = StringProperty("(1)")
    input_type = StringProperty("Length")
    input_filter_type = StringProperty("float")
    session = StringProperty("")

    # Dropdown list for profile selection, default to typical profile name,
    # with 6.0 m
    dropdown_menu = ObjectProperty()

    def on_pre_enter(self, *args):
        self.dropdown_menu = DropDown()
        for key in app.profile_lib.keys():
            btn = Button(text=key, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.dropdown_menu.select(
                btn.text))
            self.dropdown_menu.add_widget(btn)

        self.ids.dropdown_list.bind(on_release=self.dropdown_menu.open)
        self.dropdown_menu.bind(on_select=lambda instance, x: setattr(
            self.ids.dropdown_list, 'text', x))
        self.dropdown_menu.bind(on_select=self.dropdown_menu.dismiss)

        # Front layer showing the windows
        try:
            frontlayer = app.windowtypebackdrop.ids.frontlayer
            frontlayer.clear_widgets()
            # Draw the window figure, if it has not been drawn
            frontlayer.add_widget(Image(source=".img/window1.png",
                                        allow_stretch=False, keep_ratio=True))
        except Exception:
            pass

    def clear_inputs(self, text_inputs):
        for text_input in text_inputs:
            text_input.text = ""

    def add_edge(self, length):
        if length.text != "":

            if self.edge_id.strip("()") in app.edges:
                # Add edge
                app.edges[self.edge_id.strip("()")] = length.text

                # Add data to current window
                window_temp["side"]["length"].append(length.text)
                window_temp["side"]["profile"].append(
                    self.ids.dropdown_list.text)
                Snackbar(text=f"Edge: {self.edge_id} with length of"
                         " {length.text} added!").open()

                # Go to next edge
                new_edge_id = str(f"({int(self.edge_id.strip('()')) + 1})")
                if new_edge_id.strip("()") in app.edges:
                    self.edge_id = new_edge_id
                else:
                    self.edge_id = "Quantity"
                    self.input_type = "qnt"
                    self.input_filter_type = "int"
            else:
                # All edges added, add quantity and then window to database
                # and reset Input Screen
                # here length means quantity
                window_temp["quantity"] = length.text
                Snackbar(text=f"Window: {self.id_window} with Quantity:"
                         " {length.text} added!").open()

                # Add window type to database
                window_temp["type"] = app.window_type

                # Reset edge_id label
                self.reset_inputs()

                # Finally, add the window into the database
                self.add_window()

        else:
            Snackbar(text="Window information missing!").open()

    def reset_inputs(self):
        self.edge_id = "(1)"
        self.input_type = "Length"
        self.input_filter_type = "float"
        app.edges = {"1": 0, "2": 0}

    def clear_global_variables(self):
        global windows_ids

        windows_ids = []
        self.id_window = 1

    def add_window(self):
        global window_temp, windows_ids, windows

        # Note: at the moment not expecting a large database of windows per
        # session per user,
        # so optimized search is not done
        while str(self.id_window) in windows_ids:
            # Increment windows_id while in existing database
            self.id_window += 1

        windows[self.id_window] = window_temp

        # Add window into the database
        db.child("users").child(self.local_id).child(
            self.session).child("Windows").child(str(self.id_window)). \
            set(windows[self.id_window], self.id_token)

        # Add the window id
        windows_ids.append(str(self.id_window))

        # Reset the current window
        window_temp.clear()
        window_temp = {"type": 1, "length": [0], "quantity": 0}

        # Increment window ID
        self.id_window += 1


class Content(BoxLayout):

    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)


class WindowRow(Screen):
    id_window = NumericProperty()
    edge = StringProperty("")
    local_id = StringProperty("")
    id_token = StringProperty("")
    dialog = None
    label = StringProperty("(1)")
    session = StringProperty("")
    profile = StringProperty("")

    def __init__(self, session, id_window, local_id, id_token, edge, label,
                 profile, **kwargs):
        super(WindowRow, self).__init__(**kwargs)
        self.session = session
        self.id_window = id_window
        self.edge = str(edge)
        self.local_id = local_id
        self.id_token = id_token
        self.label = f"({label})"
        self.profile = profile

    def update_info(self):
        self.dialog = MDDialog(
            title="Update Info",
            size_hint=(.5, None),
            type="custom",
            content_cls=Content(),

            buttons=[
                MDFlatButton(text="Cancel",
                             text_color=app.theme_cls.primary_color,
                             on_release=self.close_dialog),
                MDFlatButton(text="Update",
                             text_color=app.theme_cls.primary_color,
                             on_release=self.info_updated)
            ]
        )
        self.dialog.get_normal_height()
        self.dialog.open()

    def info_updated(self, inst):
        if self.dialog.content_cls.ids.t1.text != "":
            # Update first input
            self.edge = self.dialog.content_cls.ids.t1.text
            # Update the database
            if self.id_window != 0:
                # Update as long as it is not the current window
                db.child("users").child(self.local_id).child(
                    self.session).child("Windows").child(str(self.id_window)).\
                    child("side").child("length").child(
                    self.label.strip("()")).set(self.edge, self.id_token)

            else:
                # Update the temporary window dictionary
                label_id = int(self.label.strip("()"))
                window_temp["side"]["length"][label_id] = self.edge

        self.dialog.dismiss()
        self.dialog = None

    def close_dialog(self, inst):
        self.dialog.dismiss()
        self.dialog = None


class WindowInfo(Screen):
    window = None
    id_window = None
    quantity = NumericProperty()
    quantity_text = StringProperty("")
    dialog = None
    item = None
    local_id = StringProperty("")
    id_token = StringProperty("")
    disable_button = BooleanProperty(False)
    window_icon_source = StringProperty(".img/window1.png")
    session = StringProperty("")

    def __init__(self, session, window, local_id, id_token, item, **kwargs):
        super(WindowInfo, self).__init__(**kwargs)
        try:
            # Windows from the Firebase database
            self.window = window.val()
            self.id_window = window.key()
            self.disable_button = False
        except Exception:
            # The current window
            self.window = window_temp
            self.id_window = "0"
            self.disable_button = True

        self.session = session
        self.local_id = local_id
        self.id_token = id_token
        self.quantity = int(self.window["quantity"])
        self.quantity_text = f"Qnt {self.quantity}"
        self.item = item

        # Window types
        window_type = int(self.window["type"])
        if window_type == 1:
            self.window_icon_source = ".img/window1.png"
        elif window_type == 2:
            self.window_icon_source = ".img/window2.png"
        elif window_type == 3:
            self.window_icon_source = ".img/window3.png"
        elif window_type == 4:
            self.window_icon_source = ".img/window4.png"
        else:
            print("Wrong window type!")

    def show_alert_dialog(self):
        self.dialog = MDDialog(
            title="Delete Window",
            text="Are you sure?",
            size_hint=(.5, None),
            buttons=[
                MDFlatButton(text="Cancel",
                             text_color=app.theme_cls.primary_color,
                             on_release=self.close_dialog),
                MDFlatButton(text="Delete",
                             text_color=app.theme_cls.primary_color,
                             on_release=self.dismiss_callback)
            ]
        )
        self.dialog.get_normal_height()
        self.dialog.open()

    def dismiss_callback(self, inst):
        """Delete the Window by its ID"""
        self.parent.parent.parent.parent.parent.remove_widget(self.item)
        windows_ids.remove(str(self.id_window))
        db.child("users").child(self.local_id).child(
            self.session).child("Windows").child(self.id_window).\
            remove(self.id_token)
        self.dialog.dismiss()
        self.dialog = None

    def close_dialog(self, inst):
        """Close the popup dialog"""
        self.dialog.dismiss()
        self.dialog = None

    def change_screen(self, screen_name, direction='forward', mode=''):
        # Change screen to display window information
        app.change_screen(screen_name, direction=direction, mode=mode)

        # Get WindowInfoScreen object
        screen = app.root.ids.firebase_login_screen.ids.window_info_screen

        # Add quantity line
        screen.ids.quantity_layout.add_widget(
            WindowQuantity(self.session, self.id_window, self.quantity,
                           self.local_id, self.id_token))

        # Add the Window edges into the grid
        cnt = 0
        for edge in self.window["side"]["length"]:
            if edge is not None:
                profile = self.window["side"]["profile"][cnt]
                screen.ids.grid.add_widget(
                    WindowRow(self.session, self.id_window, self.local_id,
                              self.id_token, edge, cnt, profile), index=0)
            cnt += 1

        # Add the window image into the grid
        screen.ids.window_image_grid.add_widget(
            Image(source=self.window_icon_source,
                  allow_stretch=False, keep_ratio=True))


class WindowQuantity(Screen):
    dialog = None
    id_window = None
    quantity = StringProperty("0")
    local_id = StringProperty("")
    id_token = StringProperty("")
    session = StringProperty("")

    def __init__(self, session, id_window, quantity, local_id, id_token,
                 **kwargs):
        super(WindowQuantity, self).__init__(**kwargs)
        self.session = session
        self.id_window = id_window
        self.quantity = str(quantity)
        self.local_id = local_id
        self.id_token = id_token

    def update_quantity(self):
        self.dialog = MDDialog(
            title="Define Quantity",
            size_hint=(.5, None),
            type="custom",
            content_cls=MDTextField(hint_text="Quantity", input_filter="int"),

            buttons=[
                MDFlatButton(text="Cancel",
                             text_color=app.theme_cls.primary_color,
                             on_release=self.close_dialog),
                MDFlatButton(text="Update",
                             text_color=app.theme_cls.primary_color,
                             on_release=self.quantity_updated)
            ]
        )
        self.dialog.get_normal_height()
        self.dialog.open()

    def quantity_updated(self, inst):
        global window_temp

        if self.dialog.content_cls.text != "":
            # Update quantity of windows
            self.quantity = self.dialog.content_cls.text
            quantity = int(self.dialog.content_cls.text)
            # Update Firebase database
            db.child("users").child(self.local_id).child(
                self.session).child("Windows").child(str(self.id_window)).\
                child("quantity").set(quantity, self.id_token)

        self.dialog.dismiss()
        self.dialog = None

    def close_dialog(self, inst):
        """Close the popup dialog"""
        self.dialog.dismiss()
        self.dialog = None


class WindowInfoScreen(Screen):
    pass


class InventoryScreen(Screen):
    local_id = StringProperty("")
    id_token = StringProperty("")
    windows_displayed = []
    session = StringProperty("")
    windows_db = ObjectProperty()
    outputs = None

    def clear_inputs(self, text_inputs):
        for text_input in text_inputs:
            text_input.text = ""

    def go_back(self):
        self.parent.transition = SlideTransition(direction="left")
        self.parent.current = self.parent.current = "analysis_screen"
        self.parent.transition = SlideTransition(direction="right")

    def show_windows(self):
        global window_temp

        # Get all the window information for the user
        self.windows_db = db.child("users").child(self.local_id).child(
            self.session).child("Windows").get(self.id_token)

        # Add Accordion to display available windows
        acc = Accordion(orientation="vertical")
        self.ids.scroll_view.add_widget(acc)

        if self.windows_db.val() is not None:
            for window in self.windows_db.each():
                if window.val() is not None:
                    window_id = str(window.key())
                    item = AccordionItem(title=f"Window {window_id}")
                    item.add_widget(WindowInfo(
                        self.session, window, self.local_id, self.id_token,
                        item))
                    acc.add_widget(item)

        # Add the current window
        item = AccordionItem(title="Window temp")
        item.add_widget(WindowInfo(self.session, window_temp,
                        self.local_id, self.id_token, item))
        acc.add_widget(item)

    def run_analysis(self):
        # Get the window database
        window_db = self.windows_db.val()

        # Get the profiles database
        profiles = app.profile_lib

        # Call the Model Optimization object
        model = ModelOptimization(tol=0.0)

        # Run the optimization function
        self.outputs = model.get_solutions(window_db, profiles)


class OutputContent(GridLayout):
    rows = 1

    def __init__(self, profile, out, **kwargs):
        super(OutputContent, self).__init__(**kwargs)

        # Add first widget as profile name and its value
        self.add_widget(MDLabel(text=f"{profile}: {app.profile_lib[profile]}"))

        # Quantity of this unique cut
        self.add_widget(MDLabel(text=f"Qnt: {out['count']}"))

        # Waste amount
        self.add_widget(MDLabel(text=f"Waste: {out['waste']}"))

        # The cuts
        for j in out:
            if j != "waste" and j != "count":
                self.add_widget(MDLabel(text=f"{j}: {out[j]}"))


class AnalysisScreen(Screen):

    def on_pre_enter(self, *args):
        # Clear widgets if any were created
        self.ids.grid.clear_widgets()
        # Get the outputs and present them
        outputs = app.root.ids.firebase_login_screen.ids.\
            inventory_screen.outputs

        # Each row is a unique cut of a profile
        if outputs is not None:
            for profile_name in outputs:
                for i in outputs[profile_name]:
                    out = outputs[profile_name][i]
                    self.ids.grid.add_widget(
                        OutputContent(profile_name, out), index=0)

    def clear_widgets(self, *args):
        self.ids.grid.clear_widgets()

    def clear_inputs(self, text_inputs):
        for text_input in text_inputs:
            text_input.text = ""

    def go_back(self):
        self.parent.transition = SlideTransition(direction="right")
        self.parent.current = self.parent.current = "inventory_screen"
        self.parent.transition = SlideTransition(direction="left")
        # app.root.ids.firebase_login_screen.ids.inventory_screen.show_windows()


class FirebaseLoginScreen(Screen, EventDispatcher):
    """Use this widget as a complete module to incorporate Firebase user
    authentication in your app. To use this module, instantiate the login
    screen in the KV language like so:
    FirebaseLoginScreen:
        web_api_key: "your_firebase_web_api_key"
        debug: True # Not necessary, but will print out debug information
        on_login_success:
            # do something here

    NOTES:
    1) You MUST set the web api key or it is impossible for the login screen to
    function properly.
    2) You probably want to wrap the firebaseloginscreen in a ScreenManager.
    3) You probably want to switch screens to a Screen in your project once the
    user has logged in (write that code in the on_login_success function shown
    in the example above).
    """
    # Firebase Project meta info - MUST BE CONFIGURED BY DEVELOPER
    web_api_key = StringProperty()  # From Settings tab in Firebase project

    # Firebase Authentication Credentials - what developers want to retrieve
    refresh_token = StringProperty("")
    localId = StringProperty("")
    idToken = StringProperty("")

    # Properties used to send events to update some parts of the UI
    login_success = BooleanProperty(False)  # Called upon successful sign in
    login_state = StringProperty("")
    sign_up_msg = StringProperty()
    email_exists = BooleanProperty(False)
    email_not_found = BooleanProperty(False)
    remember_user = BooleanProperty(True)
    require_email_verification = BooleanProperty(True)

    debug = False
    popup = Factory.LoadingPopup()
    popup.background = folder + "/transparent_image.png"

    def log_out(self):
        """
        Clear the user's refresh token, marked them as not signed in, and
        go back to the welcome screen.
        """
        with open(self.refresh_token_file, 'w') as f:
            f.write('')
        self.login_state = 'out'
        self.login_success = False
        self.refresh_token = ''
        self.ids.screen_manager.current = 'welcome_screen'
        # Clear text fields
        self.ids.sign_in_screen.ids.email.text = ''
        self.ids.sign_in_screen.ids.password.text = ''
        self.ids.sign_up_screen.ids.email.text = ''
        self.ids.sign_up_screen.ids.password.text = ''

    def on_web_api_key(self, *args):
        """
        When the web api key is set, look for an existing account in local
        memory.
        """
        # Try to load the users info if they've already created an account
        self.refresh_token_file = App.get_running_app().user_data_dir + \
            "/refresh_token.txt"
        if self.debug:
            print("Looking for a refresh token in:", self.refresh_token_file)
        if self.remember_user:
            print("REMEMBER USER IS TRUE")
            if os.path.exists(self.refresh_token_file):
                self.load_saved_account()

    def sign_up(self, email, password):
        """
        Sign the user up with their email and password.
        """
        if self.debug:
            print("Attempting to create a new account: ", email, password)
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" \
            + self.web_api_key
        signup_payload = dumps(
            {"email": email, "password": password,
             "returnSecureToken": "true"})

        UrlRequest(signup_url, req_body=signup_payload,
                   on_success=self.successful_sign_up,
                   on_failure=self.sign_up_failure,
                   on_error=self.sign_up_error, ca_file=certifi.where())

    def successful_sign_up(self, request, result):
        if self.debug:
            print("Successfully signed up a user: ", result)
        self.hide_loading_screen()
        self.refresh_token = result['refreshToken']
        self.localId = result['localId']
        self.idToken = result['idToken']

        if self.require_email_verification:
            self.send_verification_email(result['email'])
            self.ids.screen_manager.current = 'sign_in_screen'

        else:
            self.save_refresh_token(self.refresh_token)
            self.login_state = 'in'
            self.login_success = True

    def sign_in_success(self, urlrequest, log_in_data):
        """Collects info from Firebase upon successfully registering a
        new user.
        """
        if self.debug:
            print("Successfully signed in a user: ", log_in_data)
        # User's email/password exist, but are they verified?
        self.hide_loading_screen()
        self.refresh_token = log_in_data['refreshToken']
        self.localId = log_in_data['localId']
        self.idToken = log_in_data['idToken']
        self.save_refresh_token(self.refresh_token)
        if self.require_email_verification:
            self.check_if_user_verified_email()
        else:
            self.login_state = 'in'
            self.login_success = True

    def sign_up_failure(self, urlrequest, failure_data):
        """Displays an error message to the user if their attempt to log in was
        invalid.
        """
        self.hide_loading_screen()
        self.email_exists = False  # Triggers hiding the sign in button
        msg = failure_data['error']['message'].replace("_", " ").capitalize()
        toast(msg)
        if msg == "Email exists":
            self.email_exists = True
        if self.debug:
            print("Couldn't sign the user up: ", failure_data)

    def sign_up_error(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Sign up Error: ", args)

    def sign_in(self, email, password):
        """Called when the "Log in" button is pressed.

        Sends the user's email and password in an HTTP request to the Firebase
        Authentication service.
        """
        if self.debug:
            print("Attempting to sign user in: ", email, password)
        sign_in_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" \
            + self.web_api_key
        sign_in_payload = dumps(
            {"email": email, "password": password, "returnSecureToken": True})

        UrlRequest(sign_in_url, req_body=sign_in_payload,
                   on_success=self.sign_in_success,
                   on_failure=self.sign_in_failure,
                   on_error=self.sign_in_error, ca_file=certifi.where())

    def sign_in_failure(self, urlrequest, failure_data):
        """Displays an error message to the user if their attempt to create an
        account was invalid.
        """
        self.hide_loading_screen()
        self.email_not_found = False  # Triggers hiding the sign in button
        msg = failure_data['error']['message'].replace("_", " ").capitalize()
        toast(msg)
        if msg == "Email not found":
            self.email_not_found = True
        if self.debug:
            print("Couldn't sign the user in: ", failure_data)

    def sign_in_error(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Sign in error", args)

    def reset_password(self, email):
        """Called when the "Reset password" button is pressed.

        Sends an automated email on behalf of your Firebase project to the user
        with a link to reset the password. This email can be customized to say
        whatever you want. Simply change the content of the template by going
        to Authentication (in your Firebase project) -> Templates ->
        Password reset
        """
        if self.debug:
            print("Attempting to send a password reset email to: ", email)
        reset_pw_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key=" + \
                       self.web_api_key
        reset_pw_data = dumps(
            {"email": email, "requestType": "PASSWORD_RESET"})

        UrlRequest(reset_pw_url, req_body=reset_pw_data,
                   on_success=self.successful_reset,
                   on_failure=self.sign_in_failure,
                   on_error=self.sign_in_error, ca_file=certifi.where())

    def successful_reset(self, urlrequest, reset_data):
        """Notifies the user that a password reset email has been sent to them.
        """
        self.hide_loading_screen()
        if self.debug:
            print("Successfully sent a password reset email", reset_data)
        toast("Reset password instructions sent to your email.")

    def save_refresh_token(self, refresh_token):
        """Saves the refresh token in a local file to enable automatic sign in
        next time the app is opened.
        """
        if self.debug:
            print("Saving the refresh token to file: ",
                  self.refresh_token_file)
        with open(self.refresh_token_file, "w") as f:
            f.write(refresh_token)

    def load_refresh_token(self):
        """Reads the refresh token from local storage.
        """
        if self.debug:
            print("Loading refresh token from file: ", self.refresh_token_file)
        with open(self.refresh_token_file, "r") as f:
            self.refresh_token = f.read()

    def load_saved_account(self):
        """Uses the refresh token to get the user's idToken and localId by
        sending it as a request to Google/Firebase's REST API.

        Called immediately when a web_api_key is set and if the refresh token
        file exists.
        """
        if self.debug:
            print("Attempting to log in a user automatically using a "
                  "refresh token.")
        self.load_refresh_token()
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" \
            + self.web_api_key
        refresh_payload = dumps(
            {"grant_type": "refresh_token", "refresh_token":
             self.refresh_token})
        UrlRequest(refresh_url, req_body=refresh_payload,
                   on_success=self.successful_account_load,
                   on_failure=self.failed_account_load,
                   on_error=self.failed_account_load, ca_file=certifi.where())

    def successful_account_load(self, urlrequest, loaded_data):
        """Sets the idToken and localId variables upon successfully loading an
        account using the refresh token.
        """
        self.hide_loading_screen()
        if self.debug:
            print("Successfully logged a user in automatically using "
                  "the refresh token")
        self.idToken = loaded_data['id_token']
        self.localId = loaded_data['user_id']
        self.login_state = 'in'
        self.login_success = True

    def failed_account_load(self, *args):
        self.hide_loading_screen()
        if self.debug:
            print("Failed to load an account.", args)

    def sign_out(self):
        self.localId = ''
        self.idToken = ''
        self.clear_refresh_token_file()
        self.ids.screen_manager.current = 'welcome_screen'
        toast("Signed out")

    def clear_refresh_token_file(self):
        with open(self.refresh_token_file, 'w') as f:
            f.write('')

    def display_loading_screen(self, *args):
        self.popup.open()

    def hide_loading_screen(self, *args):
        self.popup.dismiss()

    def check_if_user_verified_email(self):
        """If :populate_realtime_db_with_id: is True, a verified=True record will
        be placed in this user's record.
        """

        if self.debug:
            print("Attempting to check if the user signed in has"
                  " verified their email")
        check_email_verification_url = "https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=" + self.web_api_key
        check_email_verification_data = dumps(
            {"idToken": self.idToken})

        UrlRequest(check_email_verification_url,
                   req_body=check_email_verification_data,
                   on_success=self.got_verification_info,
                   on_failure=self.could_not_get_verification_info,
                   on_error=self.could_not_get_verification_info,
                   ca_file=certifi.where())

    def could_not_get_verification_info(self, request, result):
        if self.debug:
            print("could_not_get_verification_info", request, result)
        self.hide_loading_screen()
        toast("Failed to check email verification status.")

    def got_verification_info(self, request, result):
        if self.debug:
            print("got_verification_info", request, result)
        if result['users'][0]['emailVerified']:
            self.login_state = 'in'
            self.login_success = True
        else:
            toast("Your email is not verified yet.\n Please check your email.")

    def send_verification_email(self, email):
        """Sends a verification email.

        Sends an automated email on behalf of your Firebase project to the user
        with a link to verify their email. This email can be customized to say
        whatever you want. Simply change the content of the template by going
        to Authentication (in your Firebase project) -> Templates ->
        Email Address Verification

        This email verification can only be sent after a user has signed up.
        The email will contain a code that must be entered back into the
        app.
        """
        if self.debug:
            print("Attempting to send a email verification email to: ", email)
        verify_email_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key=" \
            + self.web_api_key
        verify_email_data = dumps(
            {"idToken": self.idToken, "requestType": "VERIFY_EMAIL"})

        UrlRequest(verify_email_url, req_body=verify_email_data,
                   on_success=self.successful_verify_email_sent,
                   on_failure=self.unsuccessful_verify_email_sent,
                   on_error=self.unsuccessful_verify_email_sent,
                   ca_file=certifi.where())

    def unsuccessful_verify_email_sent(self, *args):
        toast("Couldn't send email verification email")

    def successful_verify_email_sent(self, *args):
        toast("A verification email has been sent. \nPlease check your email.")
