from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """
    Модели группы.
    """
    title = models.CharField('Название группы',
                             help_text='Заполните данные группы',
                             max_length=200)
    slug = models.SlugField('Короткая ссылка',
                            help_text='Придумайте короткую ссылку',
                            max_length=50, unique=True)
    description = models.TextField('Описание группы',
                                   help_text='Заполните описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Модели публикации.
    """
    text = models.TextField('Текст публикации',
                            help_text='Введите текст публикации')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Укажите автора публикации'
    )

    group = models.ForeignKey(
        Group,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text=('Выберите, относится ли публикация '
                   'к какой-либо группе, или оставьте поле пустым')
    )

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        # return self.text
        return '{text}, {date:%Y-%m-%d}, {author}, {group}'.format(
            text=self.text[:15],
            date=self.pub_date,
            author=self.author.username,
            group=self.group
        )
