import requests
import csv
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, InputRequired

app = Flask("__name__")
app.config['SECRET_KEY'] = 'moj_klucz'
boot = Bootstrap(app)
choices = ['USD', 'AUD', 'CAD', 'EUR', 'HUF', 'CHF', 'GBP', 'JPY', 'CZK', 'DKK', 'NOK', 'SEK', 'XDR']


class CurrencyForm(FlaskForm):
    currency_choice = SelectField("Wybierz walutę.", choices=choices)
    currency_value = StringField("Wpisz kwotę jaką chcesz wymienić na PLN.", validators=[DataRequired()])
    submit_button = SubmitField("Oblicz kwotę")


@app.route("/", methods=["POST", "GET"])
def index():
    # Tworzy lub aktualizowe walutowy plik
    write_to_csv()
    # Tworzy formularze
    form = CurrencyForm()
    # Sprawdza czy poprawne dane zostaly wprowadzone do formularzy
    if form.validate_on_submit():
        # Tworzy zmienna ktora odpowiada wybranej walucie z formularza
        curr_choice = form.currency_choice.data
        # Tworzy zmienna ktora odpowiada wartości wywbranej waluty (ile hajsu) z formularza
        curr_value = form.currency_value.data
        # Przeliczamy na PLN
        currency_pln_value = float(curr_value) * get_currency_ask_value(curr_choice)

        return render_template('calculator.html', form=form, currency_pln_value=currency_pln_value)
    return render_template("calculator.html", form=form)


def get_data():
    response = requests.get("http://api.nbp.pl/api/exchangerates/tables/C?format=json")
    if response.status_code == 200:
        print(f"Wszystko okej status code wynosi 200")
        data = response.json()
        return data[0]['rates']


def write_to_csv():
    # Pobiera dane z internetu
    nasze_dane = get_data()
    # Deklaracja nagłówków plików
    headers = ["currency", "code", "bid", "ask"]
    file = open("moj_plik.csv", "w")
    # Zapisuje dane w pliku
    zapisywacz = csv.DictWriter(file, fieldnames=headers)
    zapisywacz.writeheader()
    zapisywacz.writerows(nasze_dane)
    file.close()


def get_currency_ask_value(currency_code):
    with open("moj_plik.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for line in csv_reader:
            if line['code'] == currency_code:
                return float(line['ask'])


if __name__ == '__main__':
    app.run()
