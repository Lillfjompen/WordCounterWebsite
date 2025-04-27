from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os  # Glömde importera os för att använda miljövariabler

# Skapa appen och konfigurera databasen
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definiera Word-modellen
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(120), unique=True, nullable=False)
    count = db.Column(db.Integer, default=0)

# Funktion för att skapa databasen
def create_db():
    with app.app_context():
        db.create_all()

# Route för huvudsidan
@app.route("/", methods=["GET", "POST"])
def index():
    message = "Enter a word."
    if request.method == "POST":
        word_input = request.form['word_input']
        word_in_db = Word.query.filter_by(word=word_input).first()

        if word_in_db:
            word_in_db.count += 1
            db.session.commit()
            message = f"The word '{word_input}' has been written {word_in_db.count} times."
        else:
            new_word = Word(word=word_input, count=1)
            db.session.add(new_word)
            db.session.commit()
            message = f"The word '{word_input}' has been written 1 time."

    return render_template('index.html', message=message)

# Starta applikationen
if __name__ == "__main__":
    create_db()  # Skapa databasen när appen startar
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))  # Kör appen på rätt port
