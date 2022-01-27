import jsonpickle
import abc
from my_framework.templator import render


class Subject:

    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)


class Observer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def update(self, subject):
        pass


class SmsNotifier(Observer):

    def update(self, subject):
        print(f'К курсу присоединился новый студент {subject.student[-1]}')


class EmailNotifier(Observer):

    def update(self, subject):
        print(f'К курсу присоединился новый студент {subject.student[-1]}')


class Serializer:

    def __init__(self, _object):
        self._object = _object

    def json_dump(self):
        return jsonpickle.dumps(self._object)

    @staticmethod
    def json_load(data):
        return jsonpickle.loads(data)


class BaseView:
    template_name = None

    def get_template_name(self):
        return self.template_name

    def get_context(self):
        return {}

    def render_page(self):
        template_name = self.get_template_name()
        data = self.get_context()
        return '200 OK', render(template_name=template_name, **data)

    def __call__(self, request):
        return self.render_page()


class ListView(BaseView):
    template_name = None
    context_objects = 'objects_list'
    queryset = []

    def get_context_objects(self):
        return self.context_objects

    def get_queryset(self):
        return self.queryset

    def get_context(self):
        queryset = self.get_queryset()
        context_objects = self.get_context_objects()
        context = {context_objects: queryset}
        return context


class CreateView(BaseView):

    @staticmethod
    def get_request_data(request):
        return request['data']

    def __call__(self, request):
        if request['method'] == 'POST':
            data = self.get_request_data(request)
            self.create_object(data)
            return self.render_page()
        else:
            return super().__call__(request)

    def create_object(self, data):
        pass
