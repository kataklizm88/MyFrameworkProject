from time import time

class Route:

    def __init__(self, routes, url):
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        self.routes[self.url] = cls()

class Debug:

    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        def timeit(method):
            def timed(*args, **kw):
                begin = time()
                result = method(*args, **kw)
                finish = time()
                timework = finish - begin
                print(f'Обработка страницы {self.name} заняла {timework:2.2f} ms')
                return result
            return timed
        return timeit(cls)
