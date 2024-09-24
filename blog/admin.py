from django.contrib import admin
from blog.models import Author, Tags, Category, Article


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass