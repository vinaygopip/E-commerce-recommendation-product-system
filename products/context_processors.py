from .models import Category

def categories_context(request):
    return {
        'nav_categories': Category.objects.all().order_by('name')
    }
