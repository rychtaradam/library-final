from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Global Variables

SQLITE = 'sqlite'
MYSQL = 'mysql'

Base = declarative_base()


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=70))
    year = Column(Integer)

    # Foreign keys
    author = Column(Integer, ForeignKey('author.id'))
    genre = Column(String, ForeignKey('genres.name'))


class Genre(Base):
    __tablename__ = 'genres'

    name = Column(String(length=20), primary_key=True)

    book = relationship(Book, uselist=False, backref='genres')


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))


class Db:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}',
        MYSQL: 'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@localhost/{DB}'
    }

    def __init__(self, dbtype='sqlite', username='', password='', dbname='books'):
        dbtype = dbtype.lower()

        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname, USERNAME=username, PASSWORD=password)
            self.engine = create_engine(engine_url, echo=False)
        else:
            print('DBType is not found in DB_ENGINE')

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def read_all(self, order=Book.name):
        try:
            result = self.session.query(Book).order_by(order).all()
            return result
        except:
            return False

    def read_by_id(self, id):
        try:
            result = self.session.query(Book).get(id)
            return result
        except:
            return False

    def read_authors(self):
        try:
            result = self.session.query(Author).all()
            return result
        except:
            return False

    def create(self, book):
        try:
            self.session.add(book)
            self.session.commit()
            return True
        except:
            return False

    def update(self):
        try:
            self.session.commit()
            return True
        except:
            return False

    def delete(self, id):
        try:
            book = self.read_by_id(id)
            self.session.delete(book)
            self.session.commit()
            return True
        except:
            return False

    def create_author(self, author):
        try:
            self.session.add(author)
            self.session.commit()
            return True
        except:
            return False
