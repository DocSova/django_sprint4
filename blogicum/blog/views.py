"""Функции, отвечающие за вывод приложения blog."""
from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator

from blog.models import Post, Category, Comment
from blog.forms import UserEditProfileForm, PostForm, CommentForm

POSTS_PAGE_LIMIT = 10
POSTS_ALL = Post.objects.select_related(
    'author',
    'category',
    'location'
)
COMMENTS_ALL = Comment.objects.select_related('post')
POSTS_PUBLISHED = POSTS_ALL.filter(
    is_published=True,
    category__is_published=True
)


def check_author(view_func):
    """Функция-декоратор для проверки, является ли
    текущий пользователь автором поста или комментария."""
    def wrapper(request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        if not request.user.is_authenticated:
            return redirect('blog:post_detail', post_id)

        comment_id = kwargs.get('comment_id')
        post_object = get_object_or_404(Post, pk=post_id)
        if comment_id is not None:
            comment_object = get_object_or_404(
                COMMENTS_ALL,
                id=comment_id,
                post__id=post_id
            )
            if (comment_object.author != request.user):
                return redirect('blog:post_detail', post_id)
        elif (post_object.author != request.user):
            return redirect('blog:post_detail', post_id)

        return view_func(request, *args, **kwargs)
    return wrapper


def init_paginator(request, queryset):
    """Функция инициализирует пагинатор
    и возвращает посты текущей страницы."""
    paginator = Paginator(queryset, POSTS_PAGE_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_posts_with_current_time():
    """Функция возвращает публикации,
    учитывая фильтр по текущему времени и дате публикации."""
    return POSTS_PUBLISHED.filter(
        pub_date__lte=timezone.now()
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


def index(request):
    """Функция отображения главной страницы с постами."""
    template = 'blog/index.html'
    posts_queryset = get_posts_with_current_time()
    page_obj = init_paginator(request, posts_queryset)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Функция отображения поста в блоге под конкретным id."""

    post = get_object_or_404(POSTS_ALL, id=post_id)

    if ((request.user != post.author)
       and (not (post.pub_date <= timezone.now())
       or not post.is_published or not post.category.is_published)):
        raise Http404(f'Пост с id {post_id} не найден!')

    comments = post.comments.all()

    template = 'blog/detail.html'
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm()
    }
    return render(request, template, context)


@check_author
def delete_comment(request, post_id, comment_id):
    template = 'blog/comment.html'

    instance = get_object_or_404(
        COMMENTS_ALL,
        id=comment_id,
        post_id=post_id
    )

    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id)

    context = {
        'comment': instance
    }

    return render(request, template, context)


@check_author
def edit_comment(request, post_id, comment_id):
    template = 'blog/comment.html'
    instance = get_object_or_404(
        COMMENTS_ALL,
        id=comment_id,
        post_id=post_id
    )

    form = CommentForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    context = {
        'comment': instance,
        'form': form
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
    return redirect('blog:post_detail', post_id)


@check_author
def delete_post(request, post_id):
    template = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')

    context = {'instance': instance}

    return render(request, template, context)


@check_author
def edit_post(request, post_id):
    template = 'blog/create.html'
    instance = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=instance
    )
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(request, template, context)


@login_required
def create_post(request):
    template = 'blog/create.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {'form': form}

    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('blog:profile', request.user.username)

    return render(request, template, context)


@login_required
def edit_profile(request, username):
    template = 'blog/user.html'
    if username != request.user.username:
        return redirect('blog:profile', username)
    user_data = get_object_or_404(User, username=username)
    form = UserEditProfileForm(request.POST or None, instance=user_data)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, is_active=True, username=username)

    posts_queryset = POSTS_ALL.filter(author=profile)
    if request.user != profile:
        posts_queryset = posts_queryset.filter(category__is_published=True,
                                               pub_date__lte=timezone.now())
    posts_queryset = posts_queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    page_obj = init_paginator(request, posts_queryset)
    context = {
        'page_obj': page_obj,
        'profile': profile,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    """Функция отображения постов в категории."""
    template = 'blog/category.html'

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts_queryset = get_posts_with_current_time().filter(
        category_id=category.id
    )
    page_obj = init_paginator(request, posts_queryset)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)
