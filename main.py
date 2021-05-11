from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from modules.books import Books


class Library(MDApp):

    def build(self):
        self.theme_cls.primary_palette = "Gray"
        builder = Builder.load_file('main.kv')
        self.books = Books()
        builder.ids.navigation.ids.tab_manager.screens[0].add_widget(self.books)
        return builder


Library().run()
