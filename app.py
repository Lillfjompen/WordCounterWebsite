from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # För sessioner
db = SQLAlchemy(app)

# Modell för användare
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)

# Modell för ord
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    count = db.Column(db.Integer, nullable=False, default=1)
    first_writer = db.Column(db.String(100), nullable=True)

# Skapa databas och tabeller om de inte finns
with app.app_context():
    db.create_all()

# Funktion för att få ordningstal
def get_ordinal(n):
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

# Route för huvudsidan
@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""

    if request.method == 'POST':
        if 'username' not in session:  # Om användarnamnet inte är lagrat i sessionen
            username = request.form['username']
            existing_user = User.query.filter_by(username=username).first()

            if existing_user:  # Om användarnamnet redan finns
                message = "Username is already taken. Please choose another one."
            else:
                new_user = User(username=username)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username  # Spara användarnamnet i sessionen

        word_input = request.form['word'].lower()

        # Kontrollera om ordet är giltigt
        if word_input in english_words:  # Lägg till din lista med engelska ord här
            # Kolla om ordet finns i databasen
            word_in_db = Word.query.filter_by(word=word_input).first()

            if word_in_db:
                # Om ordet redan finns, öka räknaren
                word_in_db.count += 1
                db.session.commit()

                # Om första skribenten inte är satt, sätt den
                if word_in_db.first_writer is None:
                    word_in_db.first_writer = session['username']
                    db.session.commit()

                number = word_in_db.count
                ordinal = get_ordinal(number)
                message = f"You were the {ordinal} person to write '{word_input}'."
            else:
                # Om ordet inte finns, lägg till det i databasen
                new_word = Word(word=word_input, count=1, first_writer=session['username'])
                db.session.add(new_word)
                db.session.commit()

                message = f"You were the first to write '{word_input}' and have earned a trophy!"

        else:
            message = f"'{word_input}' is not a valid English word. Please try again."

    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
