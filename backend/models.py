from django.db import models
from slugify import slugify

class Teacher(models.Model):
    full_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name



class LearningCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, blank=True, unique=True)

    def transliterate(self, text):
        cyrillic_to_latin = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
            'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
            'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
            'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
            'я': 'ya', ' ': '-', '_': '-'
        }
        
        # Приводим к нижнему регистру и заменяем символы
        result = []
        for char in text.lower():
            result.append(cyrillic_to_latin.get(char, char))
        
        # Объединяем и оставляем только разрешенные символы
        slug_text = ''.join(result)
        slug_text = slugify(slug_text)  # Дополнительная обработка через slugify
        
        return slug_text

    def save(self, *args, **kwargs):
        if not self.slug:  # Если slug не задан
            self.slug = self.transliterate(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class LearningGoal(models.Model):
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(LearningCategory, related_name='goals', blank=True)
    def __str__(self):
        return self.name  
      
class Student(models.Model):
    full_name = models.CharField(max_length=100)
    grade = models.IntegerField()
    learning_goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE)
    learning_category = models.ForeignKey(LearningCategory, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

class LessonType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(Student, related_name='topics', blank=True)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)

class Homework(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE)
    topics = models.ManyToManyField('Topic')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ДЗ для урока {self.lesson.id}"

class HomeworkResult(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='results')
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=20, choices=[('EASY', 'Легкий'), ('MEDIUM', 'Средний'), ('HARD', 'Сложный')])
    correct_count = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)
    percentage = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    def save(self, *args, **kwargs):
        if self.total_count > 0:
            self.percentage = (self.correct_count / self.total_count) * 100
        else:
            self.percentage = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.topic.name} ({self.difficulty}): {self.percentage}%"

class JournalEntry(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    good_results = models.TextField()
    bad_results = models.TextField()
    covered_topics = models.JSONField(default=dict)  # Храним результаты по темам в JSON
    working_on = models.TextField()
    recommended_lessons = models.IntegerField()
    recommendation_reason = models.TextField()

    def __str__(self):
        return f"Запись для {self.student.full_name} от {self.created_at}"