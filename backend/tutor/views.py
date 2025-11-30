from rest_framework import viewsets, filters, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *
from .serializers import *
import logging

logger = logging.getLogger(__name__)

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info(f"Создание учителя: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f"Обновление учителя: {request.data}")
        return super().update(request, *args, **kwargs)

class LearningGoalViewSet(viewsets.ModelViewSet):
    queryset = LearningGoal.objects.all()
    serializer_class = LearningGoalSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        if category_id:
            return self.queryset.filter(categories__id=category_id)
        return self.queryset

class LearningCategoriesViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LearningCategory.objects.all()
    serializer_class = LearningCategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['slug']
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info(f"Создание категории обучения: {request.data}")
        return super().create(request, *args, **kwargs)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['learning_category']
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Создание ученика: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f"Обновление ученика: {request.data}")
        return super().update(request, *args, **kwargs)

class LessonTypeViewSet(viewsets.ModelViewSet):
    queryset = LessonType.objects.all()
    serializer_class = LessonTypeSerializer
    permission_classes = [AllowAny]

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'students']
    permission_classes = [AllowAny]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['student']
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        logger.info(f"Запрос уроков: {request.query_params}")
        return super().list(request, *args, **kwargs)

class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson', 'lesson__student']  # Поддержка фильтрации по lesson__student

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        homework = serializer.save()

        results = request.data.get('results', [])
        for result in results:
            HomeworkResult.objects.create(
                homework=homework,
                topic_id=result['topic_id'],
                difficulty=result['difficulty'],
                correct_count=result.get('correct_count', 0),
                total_count=result.get('total_count', 0)
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        homework = self.get_object()
        results = homework.results.all()
        serializer = HomeworkResultSerializer(results, many=True)
        return Response(serializer.data)

class HomeworkResultViewSet(viewsets.ModelViewSet):
    queryset = HomeworkResult.objects.all()
    serializer_class = HomeworkResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['homework__lesson']

class JournalViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student')
        if student_id:
            return self.queryset.filter(student_id=student_id)
        return self.queryset

    @action(detail=False, methods=['post'])
    def generate(self, request):
        student_id = request.data.get('student_id')
        lessons_count = int(request.data.get('lessons_count', 5))

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"detail": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        # Получаем последние уроки для студента
        lessons = Lesson.objects.filter(student=student).order_by('-date')[:lessons_count]
        if not lessons:
            return Response({"detail": "No lessons found for this student"}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем ID уроков
        lesson_ids = lessons.values_list('id', flat=True)

        # Получаем домашние задания для этих уроков
        homeworks = Homework.objects.filter(lesson__in=lesson_ids)
        homework_ids = homeworks.values_list('id', flat=True)

        # Получаем результаты ДЗ и берем только последние для каждой комбинации topic_id и difficulty
        results = HomeworkResult.objects.filter(homework__in=homework_ids).order_by('topic_id', 'difficulty', '-created_at')
        latest_results = {}
        for result in results:
            key = f"{result.topic_id}-{result.difficulty}"
            if key not in latest_results:
                latest_results[key] = result

        # Собираем данные для журнала
        good_results_list = []
        bad_results_list = []
        covered_topics = []
        bad_topics = []

        for result in latest_results.values():
            topic_entry = f"{result.topic.name} {result.difficulty.lower()} уровня"
            topic_data = {
                "topic_id": result.topic.id,
                "topic_name": result.topic.name,
                "difficulty": result.difficulty,
                "percentage": result.percentage
            }
            covered_topics.append(topic_data)
            if result.percentage == 100:
                good_results_list.append(topic_entry)
            else:
                bad_results_list.append(topic_entry)
                bad_topics.append(topic_entry)

        # Формируем первый блок: Хорошие и плохие результаты
        if good_results_list and bad_results_list:
            good_results = (
                f"У ученика такая оценка, т.к. в ходе обучения он хорошо освоил следующие темы: "
                f"{', '.join(good_results_list)}. "
                f"Но при этом ещё плохо понимает следующие темы: {', '.join(bad_results_list)}."
            )
        elif good_results_list:
            good_results = (
                f"У ученика такая оценка, т.к. в ходе обучения он хорошо освоил следующие темы: "
                f"{', '.join(good_results_list)}."
            )
        elif bad_results_list:
            good_results = (
                f"У ученика такая оценка, т.к. в ходе обучения он плохо освоил следующие темы: "
                f"{', '.join(bad_results_list)}."
            )
        else:
            good_results = "У ученика нет результатов по домашним заданиям."

        # Формируем второй блок: Пройденные темы
        covered_topics_names = [f"{t['topic_name']} {t['difficulty'].lower()} уровня" for t in covered_topics]
        covered_topics_text = (
            f"В ходе занятий были пройдены следующие темы: {', '.join(covered_topics_names)}."
            if covered_topics_names else "В ходе занятий темы не были пройдены."
        )

        # Формируем третий блок: Работаем над и рекомендации
        working_on = (
            f"Мы продолжаем работать над: {', '.join(bad_topics)}." if bad_topics
            else "Все темы освоены на 100%."
        )
        recommended_lessons = max(1, len(bad_topics))  # Минимум 1 урок, больше при проблемах
        recommendation_reason = (
            f"Я советую такой объем занятий, т.к. ученик ещё не освоил {', '.join(bad_topics)}."
            if bad_topics else "Я советую такой объем занятий для поддержания текущего уровня знаний."
        )

        # Создаем запись в журнале
        journal_entry = JournalEntry.objects.create(
            student=student,
            good_results=good_results,
            bad_results=covered_topics_text,  # Храним список всех тем
            covered_topics=covered_topics_text,
            working_on=working_on,
            recommended_lessons=recommended_lessons,
            recommendation_reason=recommendation_reason
        )

        serializer = self.get_serializer(journal_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)