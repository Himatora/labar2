"""
URL configuration for app project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tutor.views import (
    TeacherViewSet,  
    LearningGoalViewSet, 
    LearningCategoriesViewSet,  
    StudentViewSet, 
    LessonTypeViewSet,  
    TopicViewSet, 
    LessonViewSet,  
    HomeworkViewSet,  
    JournalViewSet,  
    HomeworkResultViewSet,
)

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'learning-goals', LearningGoalViewSet)
router.register(r'learning-categories', LearningCategoriesViewSet)
router.register(r'students', StudentViewSet)
router.register(r'lesson-types', LessonTypeViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'homework', HomeworkViewSet)
router.register(r'homework-results', HomeworkResultViewSet)
router.register(r'journal', JournalViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]