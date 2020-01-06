from modeltranslation.translator import register, TranslationOptions
from page.models import Page


@register(Page)
class TranslatedPage(TranslationOptions):
    fields = ('name', 'title', 'content')
