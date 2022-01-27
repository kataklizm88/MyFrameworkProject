from my_framework.templator import render
from patterns.structure_patterns import Route, Debug
from patterns.creational_patterns import Engine, Logger, MapperRegistry
from patterns.behavior_patterns import Serializer, ListView, CreateView
from patterns.unit_of_work_pattern import UnitOfWork

site = Engine()
logger = Logger('main')
UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)
routes = {}


@Route(routes=routes, url='/')
class Index:
    @Debug('index')
    def __call__(self, request):
        return '200 OK', render('index.html', objects_list=site.languages)


@Route(routes=routes, url='/register/')
class Register:
    @Debug('register')
    def __call__(self, request):
        return '200 OK', render('register.html', data=request.get('data', None))


class NotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


@Route(routes=routes, url='/create-language/')
class CreateLanguage:
    @Debug('create_language')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            language_id = data.get('language_id')
            language = None
            if language_id:
                language = site.find_language_by_id(int(language_id))
            new_language = site.create_language(name, language)
            site.languages.append(new_language)
            return '200 OK', render('index.html', objects_list=site.languages)
        else:
            languages = site.languages
            return '200 OK', render('create_language.html', languages=languages)


@Route(routes=routes, url='/courses-list/')
class CoursesList:
    @Debug('courses_list')
    def __call__(self, request):
        logger.log('Список курсов')
        try:
            language = site.find_language_by_id(int(request['request_params']['id']))
            return '200 OK', render('courses_list.html', objects_list=language.courses, name=language.name,
                                    id=language.id)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@Route(routes=routes, url='/create-course/')
class CreateCourse:
    language_id = -1

    @Debug('create_course')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']
            name = data['name']
            name = site.decode_value(name)
            language = None
            if self.language_id != -1:
                language = site.find_language_by_id(int(self.language_id))
                course = site.create_course('offline', name, language)
                site.courses.append(course)
            return '200 OK', render('courses_list.html', objects_list=language.courses,
                                    name=language.name, id=language.id)
        else:
            try:
                self.language_id = int(request['request_params']['id'])
                language = site.find_language_by_id(int(self.language_id))
                return '200 OK', render('create_course.html', name=language.name, id=language.id)
            except KeyError:
                return '200 OK', 'No categories have been added yet'


@Route(routes=routes, url='/language-list/')
class LanguageList:
    @Debug('language_list')
    def __call__(self, request):
        logger.log('Список категорий')
        return '200 OK', render('category_list.html', objects_list=site.languages)


@Route(routes=routes, url='/copy-course/')
class CopyCourse:
    @Debug('copy_course')
    def __call__(self, request):
        request_params = request['request_params']
        try:
            name = request_params['name']
            old_course = site.get_course(name)
            if old_course:
                new_name = f'copy_{name}'
                new_course = old_course.clone()
                new_course.name = new_name
                site.courses.append(new_course)
            return '200 OK', render('courses_list.html', objects_list=site.courses)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@Route(routes=routes, url='/all_courses_list/')
class AllCoursesList:
    @Debug('all_courses_list')
    def __call__(self, request):
        try:
            return '200 OK', render('all_courses_list.html', objects_list=site.courses)
        except KeyError:
            return '200 OK', 'No courses have been added yet'


@Route(routes=routes, url='/student-list/')
class StudentListView(ListView):
    template_name = 'student_list.html'
    queryset = site.students

    def get_queryset(self):
        mapper = MapperRegistry.get_current_mapper('student')
        return mapper.all()


@Route(routes=routes, url='/student-create/')
class StudentCreateView(CreateView):
    template_name = 'student_create.html'

    def create_object(self, data):
        student = data['name']
        student = site.decode_value(student)
        new_student = site.create_user('student', student)
        site.students.append(new_student)
        new_student.mark_new()
        UnitOfWork.get_current().commit()


@Route(routes=routes, url='/student-add/')
class AddStudentToCourseCreateView(CreateView):
    template_name = 'student_add.html'

    def get_context(self):
        context = super().get_context()
        context['students'] = site.students
        context['courses'] = site.courses
        return context

    def create_object(self, data):
        course_name = data['course_name']
        course_name = site.decode_value(course_name)
        course = site.get_course(course_name)
        student_name = data['student_name']
        student_name = site.decode_value(student_name)
        student = site.get_student(student_name)
        course.add_student(student)


@Route(routes=routes, url='/api/')
class StudentsApi:
    @Debug(name='StudentsApi')
    def __call__(self, request):
        return '200 OK', Serializer(site.students).json_dump()
