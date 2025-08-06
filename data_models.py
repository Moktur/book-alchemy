from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable= False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    def __repr__(self):
        return f"<Author {self.name} (ID: {self.id})>"

    def __str__(self):
        return f"{self.name}"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books',lazy=True))


    def __repr__(self):
        return f"<Book '{self.title}' by Author ID {self.author_id}>"

    def __str__(self):
        return f"{self.title} ({self.publication_year})"

