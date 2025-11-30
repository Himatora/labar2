import os
import django
import sys

# Add the app directory to Python path
sys.path.append('/app')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from tutor.models import LearningCategory

def initialize_data():
    print("🔄 Initializing database with default data...")
    
    # Создаем категории обучения
    categories = [
        "Программирование",
        "Математика", 
        "Английский язык",
        "Физика",
        "Химия",
        "История",
        "Биология"
    ]
    
    created_count = 0
    for cat_name in categories:
        category, created = LearningCategory.objects.get_or_create(name=cat_name)
        if created:
            created_count += 1
            print(f"✅ Created: {category.name}")
        else:
            print(f"📁 Already exists: {category.name}")
    
    print(f"🎉 Database initialized! Created {created_count} new categories.")

if __name__ == "__main__":
    initialize_data()
