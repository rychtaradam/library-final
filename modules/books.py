from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
from modules.db import Db, Book, Author, Genre


class AuthorContent(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)


class AuthorDialog(MDDialog):
    def __init__(self, *args, **kwargs):
        super(AuthorDialog, self).__init__(
            type="custom",
            content_cls=AuthorContent(),
            title='Nový autor',
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zrušit', on_release=self.cancel_dialog)
            ]
        )

    def save_dialog(self, *args):
        author = Author()
        author.name = self.content_cls.ids.author_name.text
        app.books.database.create_author(author)
        self.dismiss()

    def cancel_dialog(self, *args):
        self.dismiss()


class BookContent(BoxLayout):
    def __init__(self, id, *args, **kwargs):
        super().__init__(**kwargs)
        if id:
            book = vars(app.books.database.read_by_id(id))
        else:
            book = {"id": "", "name": "Název knihy", "year": "", "author": "Autor", "genre": ""}

        self.ids.book_name.text = book['name']
        authors = app.books.database.read_authors()
        menu_items = [{"viewclass": "OneLineListItem", "text": f"{author.name}",
                       "on_release": lambda x=f"{author.name}": self.set_item(x)} for author in authors]
        self.menu_authors = MDDropdownMenu(
            caller=self.ids.author_item,
            items=menu_items,
            position="center",
            width_mult=5,
        )
        self.ids.author_item.set_item(book['author'])
        self.ids.author_item.text = book['author']

    def set_item(self, text_item):
        self.ids.author_item.set_item(text_item)
        self.ids.author_item.text = text_item
        self.menu_authors.dismiss()


class BookDialog(MDDialog):
    def __init__(self, id, *args, **kwargs):
        super(BookDialog, self).__init__(
            type="custom",
            content_cls=BookContent(id=id),
            title='Záznam knihy',
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zrušit', on_release=self.cancel_dialog)
            ]
        )
        self.id = id

    def save_dialog(self, *args):
        book = {'name': self.content_cls.ids.book_name.text, 'author': self.content_cls.ids.author_item.text}
        if self.id:
            book["id"] = self.id
            app.books.update(book)
        else:
            app.books.create(book)
        self.dismiss()

    def cancel_dialog(self, *args):
        self.dismiss()


class MyItem(TwoLineAvatarIconListItem):
    def __init__(self, item, *args, **kwargs):
        super(MyItem, self).__init__()
        self.id = item['id']
        self.text = item['name']
        self.secondary_text = item['author']
        self._no_ripple_effect = True
        self.image = ImageLeftWidget()
        self.image.source = "images/book.png"
        self.add_widget(self.image)
        self.icon = IconRightWidget(icon="delete", on_release=self.on_delete)
        self.add_widget(self.icon)

    def on_press(self):
        self.dialog = BookDialog(id=self.id)
        self.dialog.open()

    def on_delete(self, *args):
        yes_button = MDFlatButton(text='Ano', on_release=self.yes_button_release)
        no_button = MDFlatButton(text='Ne', on_release=self.no_button_release)
        self.dialog_confirm = MDDialog(type="confirmation", title='Smazání záznamu',
                                       text="Chcete opravdu smazat tento záznam?", buttons=[yes_button, no_button])
        self.dialog_confirm.open()

    def yes_button_release(self, *args):
        app.books.delete(self.id)
        self.dialog_confirm.dismiss()

    def no_button_release(self, *args):
        self.dialog_confirm.dismiss()


class Books(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(Books, self).__init__(orientation="vertical")
        global app
        app = App.get_running_app()
        scrollview = ScrollView()
        self.list = MDList()
        self.database = Db(dbtype='sqlite', dbname='books.db')
        self.rewrite_list()
        scrollview.add_widget(self.list)
        self.add_widget(scrollview)
        button_box = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        new_book_btn = MDFillRoundFlatIconButton()
        new_book_btn.text = "Nová kniha"
        new_book_btn.icon = "plus"
        new_book_btn.icon_color = [0.9, 0.9, 0.9, 1]
        new_book_btn.text_color = [0.9, 0.9, 0.9, 1]
        new_book_btn.md_bg_color = [0, 0.5, 0.8, 1]
        new_book_btn.font_style = "Button"
        new_book_btn.pos_hint = {"center_x": .5}
        new_book_btn.on_release = self.on_create_book
        button_box.add_widget(new_book_btn)

        new_author_btn = MDFillRoundFlatIconButton()
        new_author_btn.text = "Nový autor"
        new_author_btn.icon = "plus"
        new_author_btn.icon_color = [0.9, 0.9, 0.9, 1]
        new_author_btn.text_color = [0.9, 0.9, 0.9, 1]
        new_author_btn.md_bg_color = [0.8, 0.5, 0, 1]
        new_author_btn.font_style = "Button"
        new_author_btn.pos_hint = {"center_x": .6}
        new_author_btn.on_release = self.on_create_author
        button_box.add_widget(new_author_btn)

        new_genre_btn = MDFillRoundFlatIconButton()
        new_genre_btn.text = "Nový žánr"
        new_genre_btn.icon = "plus"
        new_genre_btn.icon_color = [0.9, 0.9, 0.9, 1]
        new_genre_btn.text_color = [0.9, 0.9, 0.9, 1]
        new_genre_btn.md_bg_color = [0.8, 0.5, 0, 1]
        new_genre_btn.font_style = "Button"
        new_genre_btn.pos_hint = {"center_x": .6}
        new_genre_btn.on_release = self.on_create_genre
        button_box.add_widget(new_genre_btn)
        self.add_widget(button_box)

    def rewrite_list(self):
        self.list.clear_widgets()
        books = self.database.read_all()
        for book in books:
            print(vars(book))
            self.list.add_widget(MyItem(item=vars(book)))

    def on_create_book(self, *args):
        self.dialog = BookDialog(id=None)
        self.dialog.open()

    def on_create_author(self, *args):
        self.dialog = AuthorDialog()
        self.dialog.open()

    def on_create_genre(self, *args):
        self.dialog = AuthorDialog()
        self.dialog.open()

    def create(self, book):
        create_book = Book()
        create_book.name = book['name']
        create_book.author = book['author']
        self.database.create(create_book)
        self.rewrite_list()

    def update(self, book):
        update_book = self.database.read_by_id(book['id'])
        update_book.name = book['name']
        update_book.author = book['author']
        self.database.update()
        self.rewrite_list()

    def delete(self, id):
        self.database.delete(id)
        self.rewrite_list()
