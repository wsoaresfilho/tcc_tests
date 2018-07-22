from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.listview import ListView
from functools import partial

from basics import BD

# Inicializando o BD
BD = BD()

class LoginScreen(GridLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        #Labels and inputs
        self.cols = 2
        self.add_widget(Label(text='Username:', font_size=26))
        self.username = TextInput(multiline=False, font_size=26)
        self.add_widget(self.username)
        self.add_widget(Label(text='Password:', font_size=26))
        self.password = TextInput(password=True, multiline=False, font_size=26)
        self.add_widget(self.password)
        #Button
        addbtn = Button(text='Adicione um usuario', font_size=26)
        btncallback = partial(self.add_user)
        addbtn.bind(on_press=btncallback)
        self.add_widget(addbtn)
        #List with data
        self.listview = ListView()
        self.add_widget(self.listview)
        self.build_userslist()

    def build_userslist(self):
        self.remove_widget(self.listview)
        list_users = BD.selectAll()
        self.listview = ListView(item_strings=["ID: {}, Name: {}, Pass: {}".format(user[0], user[1], user[2]) for user in list_users])
        self.add_widget(self.listview)

    def add_user(self, instance):
        user = self.username
        pwd = self.password
        print("User: {}, Password: {}".format(user.text, pwd.text))
        BD.insert(user.text, pwd.text)
        self.build_userslist()
        user.text = ""
        pwd.text = ""
        

class MyApp(App):

    def build(self):
        self.title = 'Um pequeno form...'
        return LoginScreen()


if __name__ == '__main__':
    MyApp().run()
    BD.close()