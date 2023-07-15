from django.db import models
from django.contrib.auth import get_user_model

ADMIN_MODEL_TITLE_CUT = 20
ADMIN_MODEL_COMMENT_CUT = 50

User = get_user_model()


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
        return (f'{self.title[:ADMIN_MODEL_TITLE_CUT]}'
                f'{self.title[ADMIN_MODEL_TITLE_CUT:] and ".."}')

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
        return (f'{self.name[:ADMIN_MODEL_TITLE_CUT]}'
                f'{self.name[ADMIN_MODEL_TITLE_CUT:] and ".."}')


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
    image = models.ImageField('Изображение', upload_to='blog_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return (f'{self.title[:ADMIN_MODEL_TITLE_CUT]}'
                f'{self.title[ADMIN_MODEL_TITLE_CUT:] and ".."}')

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
        return (f'{self.text[:ADMIN_MODEL_COMMENT_CUT]}'
                f'{self.text[ADMIN_MODEL_COMMENT_CUT:] and ".."}')
