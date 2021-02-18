import argparse
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
    years_with_you = datetime.datetime.now().year - 1920
    remainder = years_with_you % 10
    if remainder == 1 and not years_with_you % 100 == 11:
        return f'Уже {years_with_you} год с вами'
    elif 1 < remainder < 5 and not 11 <= years_with_you % 100 <= 19:
        return f'Уже {years_with_you} года с вами'
    elif remainder == 0 or 5 <= remainder or 11 <= years_with_you % 100 <= 19:
        return f'Уже {years_with_you} лет с вами'


def parse_file_name():
    parser = argparse.ArgumentParser(
        description='Использует выбранный файл с номенклатурой винодельни'
    )
    parser.add_argument('file_name', help='файл', type=str)
    args = parser.parse_args()
    file_name = args.file_name
    return file_name


def get_assortment():
    alcohol_nomenclature = pandas.read_excel(parse_file_name(), sheet_name='Лист1',
                                             usecols=['Категория', 'Название', 'Сорт',
                                                      'Цена', 'Картинка', 'Акция'],
                                             na_values=['N/A', 'NA'], keep_default_na=False)

    sorted_nomenclature = alcohol_nomenclature.sort_values(by=['Категория'])
    alcohol_assortment = sorted_nomenclature.to_dict(orient='records')
    assortment = collections.defaultdict(list)

    for bottle in alcohol_assortment:
        category = bottle['Категория']
        assortment[category].append(bottle)
    return assortment


rendered_page = template.render(
    years_with_you=get_year_string(),
    assortment=get_assortment()
)

if __name__ == '__main__':
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

