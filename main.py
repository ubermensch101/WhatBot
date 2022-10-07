import tkinter as tk
from tkinter import filedialog

from kivy.core.image import Image
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition, NoTransition, CardTransition, RiseInTransition
from kivy.properties import ObjectProperty
from send_message import send_common_message, send_common_image_message
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout

import os
import logging
import sqlite3

logger=logging.getLogger()
logger.disabled=True

os.environ['KIVY_NO_CONSOLELOG'] = '1'


#Error Log-
#You can't have any logging from alright's side, otherwise kivy crashes, have to remove all logging from alright's init file
#For some reason, chrome 103 doesn't work regularly, but it does work on incognito, had to add it in chrome driver options
#There's something called as headless browsers- we can give this as an option once Whatsapp Web is logged in, so that the browser that selenium's working on won't be shown
#Increased timeout error limit from 3s to 20s, 3s was too low, especially for incognito
#Kivy might not work with printing messages/error logs, so un-hashtag the os.environ line above
#Ensure that the excel file is not already open

class LoginWindow(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if self.username.text=="docroom" and self.password.text=="sctpl":
            try:
                conn=sqlite3.connect('sq.db')
                cursor = conn.cursor()
                sql_command = "UPDATE USER SET Logged_In=TRUE"
                cursor.execute(sql_command)
                login_val = cursor.fetchall()
                conn.commit()
                conn.close()
            except:
                garbage_val=0
            sm.current = "home"
        else:
            invalidLogin()
        self.username.text=""
        self.password.text=""


def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()


class PathButton(Button):

    def get_path(self):

        root = tk.Tk()
        root.withdraw()

        file_name=filedialog.askopenfilename()

        if len(file_name)>=4 and (file_name[-4:]=="xlsx" or file_name[-3:]=="xls"):
            return file_name

        return "Not an Excel File!"

    def get_image_path(self):

        root = tk.Tk()
        root.withdraw()

        file_name = filedialog.askopenfilename()

        if len(file_name) >= 4 and (file_name[-3:] == "jpg" or file_name[-3:] == "png" or file_name[-3:] == "gif" or file_name[-4:] == "jpeg"):
            return file_name

        return "Not an Image File!"


class HomeScreen(Screen):

    def onpress_template1(self):
        sm.current="template1"

    def onpress_template2(self):
        sm.current="template2"


class Template1Screen(Screen):
    message=ObjectProperty(None)

    def send_message(self):
        if self.path_label.text!="" and self.path_label.text!="Not an Excel File!":
            try:
                send_common_message(self.path_label.text, self.message.text)
            except:
                sm.current="home"

    def back_to_home(self):
        sm.current="home"


class Template2Screen(Screen):
    message=ObjectProperty(None)

    def send_message(self):
        if self.path_label.text != "" and self.image_path_label.text != "" and self.path_label.text != "Not an Excel File!" and self.image_path_label.text != "Not an Image File!":
            try:
                send_common_image_message(self.path_label.text, self.image_path_label.text, self.message.text)
            except:
                sm.current = "home"
                garbage_val = 0

    def back_to_home(self):
        sm.current="home"


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("my.kv")

sm = ScreenManager(transition=NoTransition())

screens = [LoginWindow(name="login"),HomeScreen(name="home"), Template1Screen(name="template1"), Template2Screen(name="template2")]

for screen in screens:
    sm.add_widget(screen)

try:
    conn=sqlite3.connect('sq.db')
    cursor=conn.cursor()
    sql_command="SELECT Logged_In FROM USER"
    cursor.execute(sql_command)
    login_val=cursor.fetchall()[0][0]
    if login_val==0:
        sm.current="login"
    else:
        sm.current="home"
    conn.commit()
    conn.close()
except:
    sm.current="login"


class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
