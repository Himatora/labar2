from rest_framework import serializers
from .models import *

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'subject']



class LearningCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningCategory
        fields = ['id', 'name', 'slug']

class LearningGoalSerializer(serializers.ModelSerializer):
    categories = LearningCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=LearningCategory.objects.all(), many=True, write_only=True, source='categories'
    )

    class Meta:
        model = LearningGoal
        fields = ['id', 'name', 'categories', 'category_ids']

class StudentSerializer(serializers.ModelSerializer):
    learning_goal_id = serializers.PrimaryKeyRelatedField(
        queryset=LearningGoal.objects.all(), source='learning_goal', write_only=True
    )
    learning_category_id = serializers.PrimaryKeyRelatedField(
        queryset=LearningCategory.objects.all(), source='learning_category', write_only=True
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(), source='teacher', write_only=True
    )
    learning_goal = LearningGoalSerializer(read_only=True)
    learning_category = LearningCategorySerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    grade = serializers.IntegerField(default=1)

    class Meta:
        model = Student
        fields = [
            'id', 'full_name', 'grade',
            'learning_goal', 'learning_goal_id',
            'learning_category', 'learning_category_id',
            'teacher', 'teacher_id'
        ]

class LessonTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonType
        fields = ['id', 'name']

class TopicSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), many=True, required=False
    )

    class Meta:
        model = Topic
        fields = ['id', 'name', 'students']

class LessonSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    lesson_type = LessonTypeSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )
    lesson_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LessonType.objects.all(), source='lesson_type', write_only=True
    )
    topic_id = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(), source='topic', write_only=True
    )

    class Meta:
        model = Lesson
        fields = ['id', 'student', 'student_id', 'lesson_type', 'lesson_type_id', 'topic', 'topic_id', 'date', 'comment']
        
class HomeworkResultSerializer(serializers.ModelSerializer):
    topic_id = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), source='topic')

    class Meta:
        model = HomeworkResult
        fields = ['id', 'topic_id', 'difficulty', 'correct_count', 'total_count', 'percentage','created_at']

class HomeworkSerializer(serializers.ModelSerializer):
    lesson_id = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all(), source='lesson')
    topic_ids = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all(), many=True, source='topics')
    results = HomeworkResultSerializer(many=True, read_only=True)

    class Meta:
        model = Homework
        fields = ['id', 'lesson_id', 'topic_ids', 'created_at', 'results']
        


class JournalEntrySerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source='student', write_only=True
    )

    class Meta:
        model = JournalEntry
        fields = ['id', 'student', 'student_id', 'created_at', 'good_results', 'bad_results', 'covered_topics', 'working_on', 'recommended_lessons', 'recommendation_reason']