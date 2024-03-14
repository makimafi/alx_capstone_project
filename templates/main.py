from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"

db.init_app(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


with app.app_context():
    db.create_all()


# all_books = []


@app.route('/')
def home():
    result = db.session.execute(db.select(Book).order_by(Book.name)).scalars()
    all_books = result

    return render_template("index.html", books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        author = request.form.get('author')
        rating = request.form.get('rating')

        new_book = Book(name=name, author=author, rating=rating)
        db.session.add(new_book)
        db.session.commit()
        # form_data = {"name": name, "author": author, "rating": rating}
        # all_books.append(form_data)
        return redirect(url_for('home'))

    return render_template("add.html")


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        book_id = request.form.get("id")
        with app.app_context():
            book_to_update = db.get_or_404(Book, book_id)
            book_to_update.rating = request.form.get('new_rating')
            db.session.commit()
        return redirect(url_for('home'))
    book_id = request.args.get('id')
    book_selected = db.get_or_404(Book, book_id)
    return render_template("edit.html", book=book_selected)


@app.route('/delete/<int:id>')
def delete(id):
    book_id = id
    with app.app_context():

        book_to_delete = db.get_or_404(Book, book_id)
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)