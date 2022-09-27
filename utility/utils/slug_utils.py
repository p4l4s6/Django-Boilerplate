from django.utils.crypto import get_random_string
from django.utils.text import slugify


def generate_unique_slug(slug_content, instance):
    slug = slugify(slug_content)
    KClass = instance.__class__
    while KClass.objects.filter(slug=slug).exists():
        slug = slug + "-" + get_random_string(length=5)
    return slug
