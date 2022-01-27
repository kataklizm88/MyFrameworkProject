import copy
import quopri
import sqlite3
from patterns.behavior_patterns import Subject
from patterns.unit_of_work_pattern import DomainObject


class User:

    def __init__(self, name):
        self.name = name


class Student(User, DomainObject):

    def __init__(self, name):
        self.courses = []
        super().__init__(name)


class Teacher(User):
    pass


class UserFactory:
    types = {
        'student': Student,
        'teacher': Teacher
    }

    @classmethod
    def create(cls, user_type, name):
        return cls.types[user_type](name)


class CourseType:

    def clone(self):
        return copy.deepcopy(self)


class Course(CourseType, Subject):

    def __init__(self, name, language):
        self.name = name
        self.language = language
        self.language.courses.append(self)
        self.students = []
        super().__init__()

    def __getitem__(self, item):
        return self.students[item]

    def add_student(self, student):
        self.students.append(student)
        student.courses.append(self)
        self.notify()


class CourseOnline(Course):
    pass


class CourseOffline(Course):
    pass


class CourseFactory:
    types = {
        'online': CourseOnline,
        'offline': CourseOffline
    }

    @classmethod
    def create_course(cls, course_type, name, language):
        return cls.types[course_type](name, language)


class Language:
    id = 0

    def __init__(self, name, language):
        self.id = Language.id
        Language.id += 1
        self.name = name
        self.language = language
        self.courses = []

    def courses_count(self):
        number = len(self.courses)
        if self.language:
            number += self.language.course_count()
        return number


class Engine:

    def __init__(self):
        self.teachers = []
        self.students = []
        self.languages = []
        self.courses = []

    @staticmethod
    def create_user(user_type, name):
        return UserFactory.create(user_type, name)

    @staticmethod
    def create_language(name, language=None):
        return Language(name, language)

    @staticmethod
    def create_course(course_type, name, language):
        return CourseFactory.create_course(course_type, name, language)

    def find_language_by_id(self, id):
        for language in self.languages:
            if language.id == id:
                return language
            else:
                raise Exception(f' No such language {id}')

    def get_course(self, name):
        for course in self.courses:
            if course.name == name:
                return course
            else:
                return None

    def get_student(self, name):
        for student in self.students:
            if student.name == name:
                return student
            else:
                return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')


class Singleton(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=Singleton):

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log', text)


class StudentMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'student'

    def all(self):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name = item
            student = Student(name)
            student.id = id
            result.append(student)
        return result

    def find_by_id(self, id):
        statement = f"SELECT id, name FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()
        if result:
            return Student(*result)
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        # Где взять obj.id? Добавить в DomainModel? Или добавить когда берем объект из базы
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = sqlite3.connect('patterns.sqlite')


class MapperRegistry:
    mappers = {
        'student': StudentMapper,
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Student):
            return StudentMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
