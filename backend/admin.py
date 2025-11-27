from django.contrib import admin
from tutor.models import Teacher, LearningGoal, LearningCategory, Topic, Student, LessonType, Lesson, Homework, JournalEntry

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    pass

@admin.register(LearningCategory)
class LearningCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass

@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass

@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    pass

@admin.register(JournalEntry)
class JournalAdmin(admin.ModelAdmin):
    pass