from kivy.app import App
from kivy.uix.button import Button
from functools import partial

def btnaction(title, text, instance):
    print('The button <%s> is being pressed' % instance.text)
    print('Title: %s' %title)
    print('Text: %s' %text)

class TestApp(App):
    def build(self):
        self.title='Primeiro App com Kivy!'
        self.text='Testing text'
        btn = Button(text='Hello World!!!', font_size=20)
        btncallback = partial(btnaction, self.title, self.text)
        btn.bind(on_press=btncallback)
        return btn

if __name__ == '__main__':
    TestApp().run()