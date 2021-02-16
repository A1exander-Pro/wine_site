import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pandas
import collections


def get_year_string():
    years_with_you = datetime.datetime.now().year - 1920
    remainder = years_with_you % 10
    if remainder == 1 and not years_with_you % 100 == 11:
        return f'Уже {years_with_you} год с вами'
    elif 1 < remainder < 5 and not 11 <= years_with_you % 100 <= 19:
        return f'Уже {years_with_you} года с вами'
    elif remainder == 0 or 5 <= remainder or 11 <= years_with_you % 100 <= 19:
        return f'Уже {years_with_you} лет с вами'


def create_parser():
    parser = argparse.ArgumentParser(
        description='Использует выбранный файл с номенклатурой винодельни'
    )
    parser.add_argument('file_name', help='файл', type=str)
    return parser


def get_assortment(file_name):
    alcohol_nomenclature = pandas.read_excel(file_name, sheet_name='Лист1',
                                             usecols=['Категория', 'Название', 'Сорт',
                                                      'Цена', 'Картинка', 'Акция'],
                                             na_values=['N/A', 'NA'], keep_default_na=False)

    alcohol_assortment = alcohol_nomenclature.to_dict(orient='records')
    assortment = collections.defaultdict(list)

    for bottle in alcohol_assortment:
        category = bottle['Категория']
        assortment[category].append(bottle)
    sorted_assortment = dict(sorted(assortment.items()))
    return sorted_assortment


def get_render_page(file_name, template):
    rendered_page = template.render(
        years_with_you=get_year_string(),
        assortment=get_assortment(file_name)
    )
    return rendered_page


if __name__ == '__main__':
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    parser = create_parser()
    args = parser.parse_args()
    file_name = args.file_name
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(get_render_page(file_name, template))
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

