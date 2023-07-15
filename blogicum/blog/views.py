"""Функции, отвечающие за вывод приложения blog."""
from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
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
        comment_id = kwargs.get('comment_id')
        post_object = get_object_or_404(Post, pk=post_id)
        if (post_object is not None):
            if (comment_id is not None):
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


def get_posts_with_ct():
    """Функция возвращает публикации,
    учитывая фильтр по текущему времени и дате публикации."""
    return POSTS_PUBLISHED.filter(
        pub_date__lte=timezone.now()
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


def index(request):
    """Функция отображения главной страницы с постами."""
    template = 'blog/index.html'
    posts_queryset = get_posts_with_ct()
    page_obj = init_paginator(request, posts_queryset)
    context = {
        'page_obj': page_obj
        }
    return render(request, template, context)


def post_detail(request, post_id):
    """Функция отображения поста в блоге под конкретным id."""

    post_filter = Q(id=post_id)
    post = POSTS_ALL.filter(post_filter)

    if not post.exists():
        raise Http404()

    if request.user != post.first().author:
        post_filter &= Q(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    post = post.filter(post_filter)

    if not post.exists():
        raise Http404()

    comments = COMMENTS_ALL.filter(post__id=post_id)

    template = 'blog/detail.html'
    context = {
        'post': post.first(),
        'comments': comments,
        'form': CommentForm(None)
    }
    return render(request, template, context)


@check_author
def delete_comment(request, post_id, comment_id):
    template = 'blog/comment.html'

    instance = COMMENTS_ALL.get(
        id=comment_id,
        post__id=post_id
    )
    if instance is None:
        raise Http404(f'Комментарий с id {comment_id} не найден!')

    if (request.method == 'POST'):
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
        post__id=post_id
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
    get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = Post.objects.get(pk=post_id)
        new_comment.save()
    return redirect('blog:post_detail', post_id)


@check_author
def delete_post(request, post_id):
    template = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)
    if (request.method == 'POST'):
        instance.delete()
        return redirect('blog:index')

    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form}

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


def edit_profile(request, login_id):
    template = 'blog/user.html'
    if (login_id != request.user.username):
        return redirect('blog:profile', login_id)
    instance = get_object_or_404(User, username=request.user)
    form = UserEditProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, template, context)


def profile(request, login_id):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, is_active=True, username=login_id)

    post_filter = Q(author=profile)
    if (request.user != profile):
        post_filter &= Q(
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    posts_queryset = POSTS_ALL.filter(post_filter).annotate(
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
    category = Category.objects.values(
        'title',
        'description'
    )

    category = get_object_or_404(
        category,
        slug=category_slug,
        is_published=True
    )
    posts_queryset = get_posts_with_ct().filter(
        category__slug=category_slug
    )
    page_obj = init_paginator(request, posts_queryset)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)
