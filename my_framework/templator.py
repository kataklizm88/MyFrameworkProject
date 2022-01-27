from jinja2 import FileSystemLoader
from jinja2.environment import Environment


def render(template_name, folder='templates', **kwargs):
    """
    :param template_name: имя шаблона
    :param folder: папка в которой ищем шаблон
    :param kwargs: параметры
    :return:
    """
    enc = Environment()
    enc.loader = FileSystemLoader(folder)
    template = enc.get_template(template_name)
    return template.render(**kwargs)
