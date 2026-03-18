from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# -------- Database Setup --------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------- HOME + SEARCH --------
@app.route('/', methods=['GET', 'POST'])
def index():
    search = request.form.get('search')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if search:
        c.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?)", 
          ('%' + search + '%',))
    else:
        c.execute("SELECT * FROM books")

    books = c.fetchall()
    conn.close()

    return render_template('index.html', books=books)


# -------- ADD --------
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO books (title, author, status) VALUES (?, ?, ?)",
                  (title, author, "Available"))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_book.html')


# -------- DELETE --------
@app.route('/delete/<int:id>')
def delete_book(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


# -------- EDIT --------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    conn = sqlite3.connect('database.db')
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


# -------- ISSUE --------
@app.route('/issue/<int:id>')
def issue_book(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE books SET status='Issued' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


# -------- RETURN --------
@app.route('/return', methods=['GET', 'POST'])
def return_book():
    message = ""

    if request.method == 'POST':
        book_id = request.form['book_id']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Check if book exists
        c.execute("SELECT status FROM books WHERE id=?", (book_id,))
        result = c.fetchone()

        if result:
            if result[0] == "Available":
                message = "⚠️ Book is already available"
            else:
                c.execute("UPDATE books SET status='Available' WHERE id=?", (book_id,))
                conn.commit()
                message = "✅ Book returned successfully"
        else:
            message = "❌ Book not found"

        conn.close()

    return render_template('return.html', message=message)
# -------- RUN -------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)