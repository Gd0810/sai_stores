from .models import ProductCategory

def category_context(request):
    categories = ProductCategory.objects.all()
    return {'categories': categories}
