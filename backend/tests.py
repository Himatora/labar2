from django.test import TestCase

import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Teacher, LearningCategory, LearningGoal

class StudentLoadTests(TestCase):
    ENDPOINT = '/api/students/'
    NUM_REQUESTS = 1500  # Количество запросов
    CONCURRENT_WORKERS = 10  # Количество параллельных потоков

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username="testuser", password="password")
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Создаем необходимые связанные объекты
        self.teacher = Teacher.objects.create(
            full_name="Test Teacher",
            subject="Mathematics"
        )

        self.category = LearningCategory.objects.create(
            name="Test Category"
        )

        self.goal = LearningGoal.objects.create(
            name="Test Goal"
        )
        self.goal.categories.add(self.category)

    def make_request(self, req_num):
        start = time.time()
        try:
            student_data = {
                'full_name': f'Student {req_num}',
                'grade': req_num % 12 + 1,  # Группы от 1 до 12
                'learning_goal': self.goal.id,
                'learning_category': self.category.id,
                'teacher': self.teacher.id
            }
            response = self.client.post(self.ENDPOINT, student_data, format='json')
            latency = time.time() - start
            return {
                'status': response.status_code,
                'latency': latency,
                'success': response.status_code == 201,
                'error': None
            }
        except Exception as e:
            return {
                'status': None,
                'latency': time.time() - start,
                'success': False,
                'error': str(e)
            }

    def run_advanced_load_test(self):
        start_time = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=self.CONCURRENT_WORKERS) as executor:
            futures = [executor.submit(self.make_request, i) for i in range(self.NUM_REQUESTS)]
            for i, future in enumerate(futures):
                result = future.result()
                results.append(result)
                print(f"Request {i+1}/{self.NUM_REQUESTS} - "
                      f"Status: {result['status'] or 'Error'} - "
                      f"Latency: {result['latency']:.3f}s")

        total_time = time.time() - start_time
        successful = sum(1 for r in results if r['success'])
        failed = self.NUM_REQUESTS - successful
        latencies = [r['latency'] for r in results if r['success']]

        print("\nAdvanced Load Test Results:")
        print(f"Total requests: {self.NUM_REQUESTS}")
        print(f"Concurrent workers: {self.CONCURRENT_WORKERS}")
        print(f"Successful requests: {successful}")
        print(f"Failed requests: {failed}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Requests per second: {self.NUM_REQUESTS / total_time:.2f}")
        if latencies:
            print(f"Average latency: {statistics.mean(latencies):.3f}s")
            print(f"Median latency: {statistics.median(latencies):.3f}s")
            print(f"Min latency: {min(latencies):.3f}s")
            print(f"Max latency: {max(latencies):.3f}s")
            print(f"90th percentile: {statistics.quantiles(latencies, n=10)[-1]:.3f}s")

    def test_load(self):
        """Основной тестовый метод для создания студентов"""
        self.run_advanced_load_test()
from django.test import TestCase
from django.contrib.auth.models import User
import datetime
from .models import *

class TeacherModelTests(TestCase):
    def test_teacher_creation(self):
        """
        Тест создания экземпляра Teacher и строкового представления.
        """
        teacher = Teacher.objects.create(full_name="Иванов Иван Иванович", subject="Математика")
        self.assertEqual(str(teacher), "Иванов Иван Иванович")
        self.assertEqual(teacher.full_name, "Иванов Иван Иванович")
        self.assertEqual(teacher.subject, "Математика")

class LearningCategoryModelTests(TestCase):
    def test_learning_category_creation(self):
        """
        Тест создания экземпляра LearningCategory и автоматического slug.
        """
        category = LearningCategory.objects.create(name="Математика")
        self.assertEqual(str(category), "Математика")
        self.assertEqual(category.name, "Математика")
        self.assertTrue(category.slug)  # Проверяем, что slug создан автоматически

class LearningGoalModelTests(TestCase):
    def setUp(self):
        self.category = LearningCategory.objects.create(name="Математика")

    def test_learning_goal_creation(self):
        """
        Тест создания экземпляра LearningGoal и связей с категориями.
        """
        goal = LearningGoal.objects.create(name="Изучить алгебру")
        goal.categories.add(self.category)
        self.assertEqual(str(goal), "Изучить алгебру")
        self.assertEqual(goal.name, "Изучить алгебру")
        self.assertIn(self.category, goal.categories.all())

class StudentModelTests(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Иванов Иван Иванович", subject="Математика")
        self.category = LearningCategory.objects.create(name="Математика")
        self.goal = LearningGoal.objects.create(name="Изучить алгебру")
        self.goal.categories.add(self.category)

    def test_student_creation(self):
        """
        Тест создания экземпляра Student и связей.
        """
        student = Student.objects.create(
            full_name="Петров Петр Петрович",
            grade=5,
            learning_goal=self.goal,
            learning_category=self.category,
            teacher=self.teacher
        )
        self.assertEqual(str(student), "Петров Петр Петрович")
        self.assertEqual(student.full_name, "Петров Петр Петрович")
        self.assertEqual(student.grade, 5)
        self.assertEqual(student.learning_goal, self.goal)
        self.assertEqual(student.learning_category, self.category)
        self.assertEqual(student.teacher, self.teacher)

class LessonTypeModelTests(TestCase):
    def test_lesson_type_creation(self):
        """
        Тест создания экземпляра LessonType.
        """
        lesson_type = LessonType.objects.create(name="Индивидуальный")
        self.assertEqual(str(lesson_type), "Индивидуальный")
        self.assertEqual(lesson_type.name, "Индивидуальный")

class TopicModelTests(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Иванов Иван Иванович", subject="Математика")
        self.category = LearningCategory.objects.create(name="Математика")
        self.goal = LearningGoal.objects.create(name="Изучить алгебру")
        self.goal.categories.add(self.category)
        self.student = Student.objects.create(
            full_name="Петров Петр Петрович",
            grade=5,
            learning_goal=self.goal,
            learning_category=self.category,
            teacher=self.teacher
        )

    def test_topic_creation(self):
        """
        Тест создания экземпляра Topic и связей со студентами.
        """
        topic = Topic.objects.create(name="Квадратные уравнения")
        topic.students.add(self.student)
        self.assertEqual(str(topic), "Квадратные уравнения")
        self.assertEqual(topic.name, "Квадратные уравнения")
        self.assertIn(self.student, topic.students.all())

class LessonModelTests(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Иванов Иван Иванович", subject="Математика")
        self.category = LearningCategory.objects.create(name="Математика")
        self.goal = LearningGoal.objects.create(name="Изучить алгебру")
        self.goal.categories.add(self.category)
        self.student = Student.objects.create(
            full_name="Петров Петр Петрович",
            grade=5,
            learning_goal=self.goal,
            learning_category=self.category,
            teacher=self.teacher
        )
        self.lesson_type = LessonType.objects.create(name="Индивидуальный")
        self.topic = Topic.objects.create(name="Квадратные уравнения")
        self.topic.students.add(self.student)

    def test_lesson_creation(self):
        """
        Тест создания экземпляра Lesson.
        """
        lesson = Lesson.objects.create(
            student=self.student,
            lesson_type=self.lesson_type,
            topic=self.topic,
            comment="Хороший урок"
        )
        self.assertEqual(lesson.student, self.student)
        self.assertEqual(lesson.lesson_type, self.lesson_type)
        self.assertEqual(lesson.topic, self.topic)
        self.assertTrue(lesson.date)
        self.assertEqual(lesson.comment, "Хороший урок")

class HomeworkModelTests(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Иванов Иван Иванович", subject="Математика")
        self.category = LearningCategory.objects.create(name="Математика")
        self.goal = LearningGoal.objects.create(name="Изучить алгебру")
        self.goal.categories.add(self.category)
        self.student = Student.objects.create(
            full_name="Петров Петр Петрович",
            grade=5,
            learning_goal=self.goal,
            learning_category=self.category,
            teacher=self.teacher
        )
        self.lesson_type = LessonType.objects.create(name="Индивидуальный")
        self.topic = Topic.objects.create(name="Квадратные уравнения")
        self.topic.students.add(self.student)
        self.lesson = Lesson.objects.create(
            student=self.student,
            lesson_type=self.lesson_type,
            topic=self.topic,
            comment="Хороший урок"
        )

    def test_homework_creation(self):
        """
        Тест создания экземпляра Homework.
        """
        homework = Homework.objects.create(lesson=self.lesson)
        homework.topics.add(self.topic)
        self.assertEqual(str(homework), f"ДЗ для урока {self.lesson.id}")
        self.assertEqual(homework.lesson, self.lesson)
        self.assertIn(self.topic, homework.topics.all())
        self.assertTrue(homework.created_at)

class HomeworkResultModelTests(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Иванов Иван Иванович", subject="Математика")
        self.category = LearningCategory.objects.create(name="Математика")
        self.goal = LearningGoal.objects.create(name="Изучить алгебру")
        self.goal.categories.add(self.category)
        self.student = Student.objects.create(
            full_name="Петров Петр Петрович",
            grade=5,
            learning_goal=self.goal,
            learning_category=self.category,
            teacher=self.teacher
        )
        self.lesson_type = LessonType.objects.create(name="Индивидуальный")
        self.topic = Topic.objects.create(name="Квадратные уравнения")
        self.topic.students.add(self.student)
        self.lesson = Lesson.objects.create(
            student=self.student,
            lesson_type=self.lesson_type,
            topic=self.topic,
            comment="Хороший урок"
        )
        self.homework = Homework.objects.create(lesson=self.lesson)
        self.homework.topics.add(self.topic)

    def test_homework_result_creation(self):
        """
        Тест создания экземпляра HomeworkResult и автоматического расчета процентов.
        """
        result = HomeworkResult.objects.create(
            homework=self.homework,
            topic=self.topic,
            difficulty="MEDIUM",
            correct_count=8,
            total_count=10
        )
        self.assertEqual(str(result), "Квадратные уравнения (MEDIUM): 80.0%")
        self.assertEqual(result.homework, self.homework)
        self.assertEqual(result.topic, self.topic)
        self.assertEqual(result.difficulty, "MEDIUM")
        self.assertEqual(result.correct_count, 8)
        self.assertEqual(result.total_count, 10)
        self.assertEqual(result.percentage, 80.0)
        self.assertTrue(result.created_at)

class JournalEntryModelTests(TestCase):
    def setUp(self):
        self.teacher = Teacher.objects.create(full_name="Иванов Иван Иванович", subject="Математика")
        self.category = LearningCategory.objects.create(name="Математика")
        self.goal = LearningGoal.objects.create(name="Изучить алгебру")
        self.goal.categories.add(self.category)
        self.student = Student.objects.create(
            full_name="Петров Петр Петрович",
            grade=5,
            learning_goal=self.goal,
            learning_category=self.category,
            teacher=self.teacher
        )

    def test_journal_entry_creation(self):
        """
        Тест создания экземпляра JournalEntry.
        """
        entry = JournalEntry.objects.create(
            student=self.student,
            good_results="Хорошо решает уравнения",
            bad_results="Плохо понимает текстовые задачи",
            covered_topics={"Квадратные уравнения": "80%"},
            working_on="Текстовые задачи",
            recommended_lessons=3,
            recommendation_reason="Для закрепления материала"
        )
        self.assertEqual(str(entry), f"Запись для {self.student.full_name} от {entry.created_at}")
        self.assertEqual(entry.student, self.student)
        self.assertEqual(entry.good_results, "Хорошо решает уравнения")
        self.assertEqual(entry.bad_results, "Плохо понимает текстовые задачи")
        self.assertEqual(entry.covered_topics, {"Квадратные уравнения": "80%"})
        self.assertEqual(entry.working_on, "Текстовые задачи")
        self.assertEqual(entry.recommended_lessons, 3)
        self.assertEqual(entry.recommendation_reason, "Для закрепления материала")
        self.assertTrue(entry.created_at)

class TutoringSystemIntegrationTests(TestCase):
    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = APIClient()
        
        # Создаем пользователя для аутентификации
        self.user = User.objects.create_user(
            username='tutor',
            password='password123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Создаем базовые объекты
        self.teacher = Teacher.objects.create(
            full_name="Иванова Мария Сергеевна",
            subject="Математика"
        )
        
        self.category = LearningCategory.objects.create(
            name="Математика"
        )
        
        self.goal = LearningGoal.objects.create(
            name="Подготовка к ЕГЭ"
        )
        self.goal.categories.add(self.category)
        
        self.student = Student.objects.create(
            full_name="Петров Алексей",
            grade=11,
            learning_goal=self.goal,
            learning_category=self.category,
            teacher=self.teacher
        )
        
        self.lesson_type = LessonType.objects.create(
            name="Индивидуальный"
        )
        
        self.topic = Topic.objects.create(
            name="Квадратные уравнения"
        )
        self.topic.students.add(self.student)

    def test_student_filter_by_category(self):
        """Тест фильтрации студентов по категории обучения"""
        category2 = LearningCategory.objects.create(name="Физика")
        student2 = Student.objects.create(
            full_name="Сидорова Анна",
            grade=10,
            learning_goal=self.goal,
            learning_category=category2,
            teacher=self.teacher
        )
        
        response = self.client.get(
            reverse('student-list'),
            {'learning_category': self.category.id}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], self.student.full_name)