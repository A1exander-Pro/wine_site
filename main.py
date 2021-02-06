from http.server import HTTPServer, SimpleHTTPRequestHandler
import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas
import collections

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')


def get_year_string():
    date_today = datetime.datetime.now()
    founded_date = datetime.datetime(year=1920, month=1, day=1)
    delta = date_today - founded_date
    years_with_you = delta.days // 365
    remainder = years_with_you % 10
    if remainder == 1 and not years_with_you % 100 == 11:
        return f'Уже {years_with_you} год с вами'
    elif 1 < remainder < 5 and not 11 <= years_with_you % 100 <= 19:
        return f'Уже {years_with_you} года с вами'
    elif remainder == 0 or 5 <= remainder or 11 <= years_with_you % 100 <= 19:
        return f'Уже {years_with_you} лет с вами'


exel_db = pandas.read_excel('wine3.xlsx', sheet_name='Лист1',
                            usecols=['Категория', 'Название', 'Сорт',
                                     'Цена', 'Картинка', 'Акция'],
                            na_values=['N/A', 'NA'], keep_default_na=False)

bottles = exel_db.to_dict(orient='records')

assortment = collections.defaultdict(list)

for bottle in bottles:
    for category in bottle:
        category = bottle['Категория']
    assortment[category].append(bottle)

rendered_page = template.render(
    years_with_you=get_year_string(),
    assortment=assortment
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

template = env.get_template('template.html')
server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()
