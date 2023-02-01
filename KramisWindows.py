import subprocess
import os
import requests

from MongoDB import database
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window


from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu


from kivy.config import Config


cluster = ""
collection = ""
dataB = ""
bot_token = ""

db = database(cluster, collection, dataB)


class StartScreen(Screen):

    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.userExists(), 1 / 60)

    def on_enter(self, *args):
        self.userExists()

    def userExists(self):
        try:
            if db.containsID(getMachineID()) and hasName() and hasChatID():
                self.manager.current = "Home"
                print("1")
            elif db.containsID(getMachineID()) and (not hasName() or not hasChatID()):
                self.manager.current = "Credential"
                print("2")
            else:
                db.add_element(getMachineID(), name=None, connection=None, mood=None, chatID=None)
                self.manager.current = "Credential"
                print("3")
        except Exception as e:
            print(e)



class EnterCredentialsScreen(Screen):
    nameInput = ObjectProperty(None)
    chatInput = ObjectProperty(None)
    go_to_settings = ObjectProperty(None)


    def submitName(self):
        db.update_element(getMachineID(), "name", self.nameInput.text)
        db.update_element(getMachineID(), "chatID", self.chatInput.text)
        self.chatInput.text = ""
        self.nameInput.text = ""
        self.manager.current = "Home"



class EnterNameScreen(Screen):
    nameInput = ObjectProperty(None)

    def submitName(self):
        db.update_element(getMachineID(), "name", self.nameInput.text)
        self.nameInput.text = ""
        self.manager.transition.direction = "right"
        self.manager.current = "Settings"


class EnterChatID(Screen):
    idInput = ObjectProperty(None)

    def submitID(self):
        db.update_element(getMachineID(), "chatID", self.idInput.text)
        self.idInput.text = ""
        self.manager.transition.direction = "right"
        self.manager.current = "Settings"


class ConnectScreen(Screen):
    code_input = ObjectProperty(None)

    def submitCode(self):
        if db.containsID(str(self.code_input.text)):
            db.update_element(getMachineID(), "connection", self.code_input.text)
            db.update_element(self.code_input.text, "connection", getMachineID())

            self.code_input = ""
            toast("Connected")
            self.manager.transition.direction = "left"
            self.manager.current = "Partner"
        else:
            toast("Partner does not exist")



class PartnerScreen(Screen):
    partner_mood = ObjectProperty(None)
    partner_name = ObjectProperty(None)


    def on_pre_enter(self, *args):


        if not hasConnection():
            self.manager.transition.direction = "left"
            self.manager.current = "Connect"
        else:
            self.partner_chatID = getPartnerChatID()
            self.username = db.get_element(getMachineID(), "name")
            self.partner_mood.source = "Mood/" + getPartnersMood()
            self.partner_name.text = getPartnerName()


    def open_dropdown(self):
        text = ["Hug", "Kiss", "Touch", "Tickle", "Punch"]

        self.menu_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "Hug",
                "on_release": lambda x="callback": self.option_callback("hug")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Kiss",
                "on_release": lambda x="callback": self.option_callback("kiss")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Touch",
                "on_release": lambda x="callback": self.option_callback("touch")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Tickle",
                "on_release": lambda x="callback": self.option_callback("tickle")
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Punch",
                "on_release": lambda x="callback": self.option_callback("punch")
            }
        ]

        self.request_dropdown = MDDropdownMenu(
            caller=self.ids.menu_,
            items=self.menu_list,
            width_mult=2,
            max_height="240px",
            hor_growth="left"
        )
        self.request_dropdown.open()


    def option_callback(self, requested_action):
        print(requested_action)
        send_notify(self.partner_chatID, self.username + " wants a " + requested_action)
        self.request_dropdown.dismiss()
        toast("Request sent")


    def sendKiss(self):
        send_notify(self.partner_chatID, self.username + " sent you a kiss 💋")
        toast("Sent")

    def sendTickle(self):
        send_notify(self.partner_chatID, self.username + " tickled you 👉👈")
        toast("Sent")

    def sendTouch(self):
        send_notify(self.partner_chatID, self.username + " touched you 👉")
        toast("Sent")

    def sendPunch(self):
        send_notify(self.partner_chatID, self.username + " hit you in yo face 👊 🖕")
        toast("Sent")

    def sendHug(self):
        send_notify(self.partner_chatID, self.username + " hugged you ❤")
        toast("Sent")



class HomeScreen(Screen):
    greeting_name = ObjectProperty(None)
    current_mood = ObjectProperty(None)
    dropdown = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.greeting_name.text = "Hi, " + db.get_element(getMachineID(), "name")
        if hasMood():
            self.current_mood.source = os.getcwd() + "/Mood/" + db.get_element(getMachineID(), "mood")
        else:
            self.current_mood.source = os.getcwd() + "/Mood/Happy.png"
            db.update_element(getMachineID(), "mood", "Happy.png")


    def showMoods(self):
        self.my_dialog = MDDialog(title="What's your mood?", size_hint=[0.6, 0.3], overlay_color=(1, 1, 1, 0), type="custom",
                             buttons=[
                                 MDIconButton(
                                     icon="Mood/Blank.png", on_press=self.updateMood
                                 ),
                                 MDIconButton(
                                     icon="Mood/Drool.png", on_press=self.updateMood
                                 ),
                                 MDIconButton(
                                     icon="Mood/Happy.png", on_press=self.updateMood
                                 ),
                                 MDIconButton(
                                     icon="Mood/Sad.png", on_press=self.updateMood
                                 ),
                                 MDIconButton(
                                     icon="Mood/Sleepy.png", on_press=self.updateMood
                                 ),
                                 MDIconButton(
                                     icon="Mood/BigSmile.png", on_press=self.updateMood
                                 )
                             ])
        self.my_dialog.open()


    def updateMood(self, instance):
        self.current_mood.source = instance.icon
        db.update_element(getMachineID(), "mood", instance.icon[5:])
        if hasConnection():
            self.notifyMood(self.getMood(instance.icon[5:]))
        else:
            toast("Connect to partner to notify her/him")
        self.my_dialog.dismiss()


    def notifyMood(self, instance):
        partner_chatID = getPartnerChatID()
        username = db.get_element(getMachineID(), "name")
        print(instance)
        if instance == "Happy":
            send_notify(partner_chatID, username + " is feeling happy 😄")
        elif instance == "Sad":
            send_notify(partner_chatID, username + " is feeling sad 😢")
        elif instance == "Sleepy":
            send_notify(partner_chatID, username + " is kinda ZzZzzleepy 😴")
        elif instance == "Drool":
            print("sending drool")
            send_notify(partner_chatID, username + " is droooling for u 😚")
        elif instance == "Blank":
            send_notify(partner_chatID, username + " is not good but not terrible 😶")
        else:
            send_notify(partner_chatID, username + " is super happy 😆")

        toast("Notified partner")

    def getMood(self, instance):
        mood = ""
        for i in range(len(instance)):

            if instance[i] == ".":
                return mood
            else:
                mood += instance[i]



class SettingsScreen(Screen):
    partner_name = ObjectProperty(None)
    username = ObjectProperty(None)
    user_id = ObjectProperty(None)
    chat_id = ObjectProperty(None)

    def on_pre_enter(self, *args):
        if hasConnection():
            self.partner_name.text = getPartnerName()
        else:
            self.partner_name.text = "None"

        self.username.text = db.get_element(getMachineID(), "name")
        self.user_id.text = getMachineID()
        self.chat_id.text = db.get_element(getMachineID(), "chatID")


    def edit_partner(self):
        self.partner_popup = MDDialog(title="Partner configuration", size_hint=[0.6, 0.3], overlay_color=(1, 1, 1, 0),
                                  buttons=[
                                      MDFillRoundFlatButton(
                                          text="Remove partner", on_press=self.remove_and_reload
                                      )
                                  ])
        self.partner_popup.open()

    def remove_and_reload(self, instance):
        if hasConnection():
            removePartner()
        self.partner_name.text = "None"
        self.partner_popup.dismiss()
        self.manager.current = "Settings"

    def delete_account(self):
        if hasConnection():
            removePartner()

        db.delete_query(getMachineID())
        toast("Account deleted")
        self.manager.current = "Start"



class WindowManager(ScreenManager):
    enter_name_screen = ObjectProperty(None)
    connect_screen = ObjectProperty(None)
    home_screen = ObjectProperty(None)



class AlarmApp(MDApp):

    def build(self):
        kv = Builder.load_file(os.path.realpath("my.kv"))
        Window.size = (350, 500)
        print(db.containsID(getMachineID()))
        return kv



def getMachineID():     #Returns unique ID of machine
    current_machine_id = str(subprocess.check_output('wmic csproduct get uuid'), 'utf-8').split('\n')[1].strip()
    return current_machine_id


def hasName():          #Returns boolean for if user has a name
    return db.get_element(getMachineID(), "name") is not None and not ""


def hasChatID():
    return db.get_element(getMachineID(), "chatID") is not None and not ""


def hasConnection():
    return db.get_element(getMachineID(), "connection") is not None and not ""


def hasMood():
    return db.get_element(getMachineID(), "mood") is not None and not ""


def getPartnersMood():
    return db.get_element(db.get_element(getMachineID(), "connection"), "mood")


def getPartnerName():
    return db.get_element(db.get_element(getMachineID(), "connection"), "name")


def getPartnerChatID():
    return db.get_element(db.get_element(getMachineID(), "connection"), "chatID")


def removePartner():
    db.update_element(db.get_element(getMachineID(), "connection"), "connection", None)
    db.update_element(getMachineID(), "connection", None)


def send_notify(chatID, bot_message):
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + bot_message
   requests.get(send_text)


if __name__ == "__main__":
    AlarmApp().run()
