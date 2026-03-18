from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# ---------- DATABASE PATH ----------
# For now (safe on Render without disk)
DB_PATH = 'database.db'

# ---------- INIT DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            status TEXT
        )
    ''')

    # Insert default books if empty
    c.execute("SELECT COUNT(*) FROM books")
    count = c.fetchone()[0]

    if count == 0:
        books = [
            ("The Alchemist", "Paulo Coelho"),
            ("Atomic Habits", "James Clear"),
            ("Rich Dad Poor Dad", "Robert Kiyosaki"),
            ("Think and Grow Rich", "Napoleon Hill"),
            ("Ikigai", "Hector Garcia"),
            ("The Power of Now", "Eckhart Tolle"),
            ("Deep Work", "Cal Newport"),
            ("Zero to One", "Peter Thiel"),
            ("Start with Why", "Simon Sinek"),
            ("The 7 Habits", "Stephen Covey"),

            ("Harry Potter 1", "J.K. Rowling"),
            ("Harry Potter 2", "J.K. Rowling"),
            ("Harry Potter 3", "J.K. Rowling"),
            ("Harry Potter 4", "J.K. Rowling"),
            ("Harry Potter 5", "J.K. Rowling"),

            ("C Programming", "Dennis Ritchie"),
            ("Data Structures", "Mark Allen Weiss"),
            ("Operating System", "Galvin"),
            ("Computer Networks", "Andrew Tanenbaum"),
            ("DBMS", "Korth"),

            ("Python Crash Course", "Eric Matthes"),
            ("Clean Code", "Robert Martin"),
            ("Code Complete", "Steve McConnell"),
            ("Design Patterns", "Erich Gamma"),
            ("Refactoring", "Martin Fowler"),

            ("The Hobbit", "J.R.R. Tolkien"),
            ("Lord of the Rings", "J.R.R. Tolkien"),
            ("Game of Thrones", "George R.R. Martin"),
            ("Dune", "Frank Herbert"),
            ("The Witcher", "Andrzej Sapkowski"),

            ("Wings of Fire", "A.P.J Abdul Kalam"),
            ("Ignited Minds", "A.P.J Abdul Kalam"),
            ("My Experiments with Truth", "Mahatma Gandhi"),
            ("Discovery of India", "Jawaharlal Nehru"),
            ("India After Gandhi", "Ramachandra Guha"),

            ("Sapiens", "Yuval Noah Harari"),
            ("Homo Deus", "Yuval Noah Harari"),
            ("21 Lessons", "Yuval Noah Harari"),
            ("Thinking Fast and Slow", "Daniel Kahneman"),
            ("Outliers", "Malcolm Gladwell"),

            ("The Lean Startup", "Eric Ries"),
            ("Hooked", "Nir Eyal"),
            ("Rework", "Jason Fried"),
            ("Good to Great", "Jim Collins"),
            ("Blue Ocean Strategy", "Kim & Mauborgne")
        ]

        for book in books:
            c.execute(
                "INSERT INTO books (title, author, status) VALUES (?, ?, ?)",
                (book[0], book[1], "Available")
            )

    conn.commit()
    conn.close()


# Call once at startup
init_db()

# ---------- HOME + SEARCH ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    search = request.form.get('search')

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if search:
        c.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?)",
                  ('%' + search + '%',))
    else:
        c.execute("SELECT * FROM books")

    books = c.fetchall()
    conn.close()

    return render_template('index.html', books=books)


# ---------- ADD ----------
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, status) VALUES (?, ?, ?)",
                  (title, author, "Available"))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_book.html')


# ---------- DELETE ----------
@app.route('/delete/<int:id>')
def delete_book(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


# ---------- EDIT ----------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        c.execute("UPDATE books SET title=?, author=? WHERE id=?",
                  (title, author, id))
        conn.commit()
        conn.close()
        return redirect('/')

    c.execute("SELECT * FROM books WHERE id=?", (id,))
    book = c.fetchone()
    conn.close()

    return render_template('edit_book.html', book=book)


# ---------- ISSUE ----------
@app.route('/issue/<int:id>')
def issue_book(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE books SET status='Issued' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


# ---------- RETURN ----------
@app.route('/return/<int:id>')
def return_book(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT status FROM books WHERE id=?", (id,))
    result = c.fetchone()

    if result and result[0] == "Issued":
        c.execute("UPDATE books SET status='Available' WHERE id=?", (id,))
        conn.commit()

    conn.close()
    return redirect('/')


# ---------- RUN ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)