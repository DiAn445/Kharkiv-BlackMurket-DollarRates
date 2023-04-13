from flask import Flask, render_template, url_for
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import re
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from scipy.ndimage import median_filter
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.static_folder = 'static'
bootstrap = Bootstrap(app)
# app.config['JSON_AS_ASCII'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:44454644ass@localhost/my_database'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
title = 'Kharkiv Dollar Rates'

# BeautifulSoup object
url = urlopen("https://finance.i.ua/market/harkov/usd/?").read().decode('utf-8')
bs = BeautifulSoup(url, 'html.parser')


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     rates_info = db.Column(db.String(120))
#     graph = db.Column(db.String(120), unique=True)
#
#     def __init__(self, rates_info, graph):
#         self.name = rates_info
#         self.email = graph
#
#
# with app.app_context():
#     db.create_all()


class Parser:
    _data = []
    _strings = []

    @classmethod
    def fill_attrs(cls):
        result = []
        for i in bs.find(lambda tag: tag.name == 'table'):
            for j in i.find_all_next('tbody'):
                for tr in j.find_all_next('tr'):
                    result.append(tr)
        for i in result:
            pattern = r'[?]'
            if len(cls._strings) == 10:
                break
            cls._strings.append(
                f"Время: {str(i.find_next('time').next)}, Курс: {str(i['data-ratio'])}, Сума: {str(round(float(i['data-amount'])))} Инфо: {re.sub(pattern, '', i.find_all_next('td')[5].text)}")
            cls._data.append([i.find_next('time').next, round(float(i['data-ratio']), 2)])

    @classmethod
    def get_data(cls):
        cls.fill_attrs()
        return cls._data

    @classmethod
    def get_strings(cls):
        cls.fill_attrs()
        return sorted(cls._strings, key=lambda x: (int(x[7:9]), int(x[10:12])), reverse=True)


# Creating DataFrame and graph
df = pd.DataFrame(Parser.get_data(), columns=['Time', 'Rates'])
sns.set_style("darkgrid")
ax = sns.barplot(x="Time", y="Rates", data=df)
ax.set_ylim(30, 43)
median_y = median_filter(df['Rates'].median(), size=10)
plt.axhline(y=median_y, color='r', linestyle='--')

# Saving graph into buffer
output = BytesIO()
FigureCanvas(plt.gcf()).print_png(output)
image_data = base64.b64encode(output.getvalue()).decode('utf-8')


@app.route('/')
def pageone():
    print(url_for('pageone'))
    return render_template('mainpage.html', image_data=image_data, data=Parser.get_strings(), title=title)


if __name__ == '__main__':
    app.run(debug=True)
