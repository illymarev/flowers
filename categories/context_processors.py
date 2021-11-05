from .models import Category


def categories_links(request):
    flower_categories = Category.objects.filter(is_plant=False)
    plant_categories = Category.objects.filter(is_plant=True)
    context = {
        'flower_categories': flower_categories,
        'plant_categories': plant_categories,
    }
    return context
