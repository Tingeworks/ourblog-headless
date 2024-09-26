from django.contrib import admin
from blog.models import Author, Tag, Category, Article
from unfold.admin import ModelAdmin

@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    pass

@admin.register(Tag)
class TagsAdmin(ModelAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass

@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    pass