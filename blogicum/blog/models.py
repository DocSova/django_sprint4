from django.db import models
from django.contrib.auth import get_user_model

ADMIN_MODEL_TITLE_CUT = 20
ADMIN_MODEL_COMMENT_CUT = 50

User = get_user_model()


def get_formatted_description(title, letter_count):
    return (f'{title[:letter_count]}'
            f'{title[letter_count:] and ".."}')


class BaseModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    def __str__(self):
        return get_formatted_description(self.title, ADMIN_MODEL_TITLE_CUT)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(BaseModel):
    name = models.CharField(
        'Название места',
        max_length=256
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return get_formatted_description(self.name, ADMIN_MODEL_TITLE_CUT)


class Post(BaseModel):
    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=('Если установить дату и время в будущем '
                   '— можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='locations',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='categories',
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='blog_images',
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return get_formatted_description(self.title, ADMIN_MODEL_TITLE_CUT)


class Comment(BaseModel):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return get_formatted_description(self.text, ADMIN_MODEL_COMMENT_CUT)
