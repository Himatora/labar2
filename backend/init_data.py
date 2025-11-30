import os
import django
import sys

# Добавляем текущую директорию в Python path
sys.path.append('/app')

# Указываем правильное имя модуля настроек
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # Только 'settings' без 'app.'

try:
    django.setup()
    
    from tutor.models import LearningCategory
    
    print("🔄 Initializing database with default data...")
    
    categories = [
        "Программирование",
        "Математика", 
        "Английский язык",
        "Физика",
        "Химия"
    ]
    
    for cat_name in categories:
        category, created = LearningCategory.objects.get_or_create(name=cat_name)
        if created:
            print(f"✅ Created: {category.name}")
        else:
            print(f"📁 Already exists: {category.name}")
    
    print("🎉 Default categories created!")

except Exception as e:
    print(f"❌ Error in init_data.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
