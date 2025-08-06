from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book
from datetime import datetime
from sqlalchemy import or_

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir,'data/library.sqlite')}"

db.init_app(app)

with app.app_context():
    db.create_all()

app.secret_key = "supersecretkey"


@app.route('/', methods=['GET'])
def home():
    sort_by = request.args.get('sort', 'title')
    search_query = request.args.get('q', '').strip()

    query = db.session.query(Book).join(Author)

    # Apply search if provided
    if search_query:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search_query}%"),
                Author.name.ilike(f"%{search_query}%")
            )
        )

    # Apply sorting
    if sort_by == 'author':
        query = query.order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    books = query.all()

    return render_template('home.html', books=books, sort_by=sort_by, search_query=search_query)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date_str = request.form['birthdate']
        date_of_death_str = request.form['date_of_death']

        # Feldprüfung
        if not name or not birth_date_str:
            flash("Please fill in all required fields.", "error")
            return render_template('add_author.html')

        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None

            new_author = Author(
                name=name,
                birth_date=birth_date,
                date_of_death=date_of_death
            )
            db.session.add(new_author)
            db.session.commit()
            flash("Author added successfully!", "success")
            return redirect(url_for('add_author'))  # Sauberer Redirect
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding author: {e}", "error")

    # Wenn GET oder Fehler, zeige einfach das Formular
    return render_template('add_author.html')


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author  # Access the related author

    try:
        db.session.delete(book)
        db.session.commit()

        # Check if author has no other books left
        if not author.books:
            db.session.delete(author)
            db.session.commit()
            flash(f"Book '{book.title}' and author '{author.name}' deleted successfully.", "success")
        else:
            flash(f"Book '{book.title}' deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting book: {e}", "error")

    return redirect(url_for('home'))


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form.get('author_id')

        if not title or not publication_year or not author_id:
            flash("Please fill in all required fields.", "error")
            return render_template('add_book.html', authors=Author.query.all())

        try:
            new_book = Book(
                title=title,
                publication_year=publication_year,
                author_id=author_id
            )
            db.session.add(new_book)
            db.session.commit()
            flash("Book added successfully!", "success")
            return redirect(url_for('add_book'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding book: {e}", "error")
            return render_template('add_book.html', authors=Author.query.all())

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)