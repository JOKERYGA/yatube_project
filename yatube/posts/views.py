from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Comment, Follow
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm


User = get_user_model()

@cache_page(20, key_prefix='index_page')
def index(request):
    posts_list = Post.objects.all().order_by("-pub_date")
    # Если порядок сортировки определен в классе Meta модели,
    # запрос будет выглядить так:
    # post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(posts_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    # Получаем объект группы по переданному slug или возвращаем ошибку 404, если группа не найдена
    group = get_object_or_404(Group, slug=slug)
    group_posts = Post.objects.filter(group=group).order_by("-pub_date")
    
    paginator = Paginator(group_posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "group_posts": group_posts,
        "page_obj": page_obj
        }
    return render(request, "posts/group_list.html", context)


@login_required
def profile(request, username):
    """персональная страница автора"""
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user).order_by("-pub_date")
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "page_obj": page_obj}

    return render(request, "posts/profile.html", context)

@login_required
def post_detail(request, post_id):
    """страница отдельного поста"""
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()

    context = {"post": post, "form": form, "comments": comments}
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:index")
    else:
        form = PostForm()
    return render(request, "posts/create_post.html", {"form": form})

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("posts:post_detail", post_id=post_id)
    else:
        form = PostForm(instance=post)

    context = {
        "form": form,
        "is_edit": True,
        "post": post,
    }

    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)

    comments = post.comments.all()
    return render(request, 'posts/post_detail.html', {'post': post, 'form': form, 'comments': comments})


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Проверяем, имеет ли текущий пользователь право удалять комментарий
    if request.user == comment.author:
        comment.delete()

    # После удаления комментария перенаправляем пользователя на страницу, откуда он пришел
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def follow_index(request):
    """Посты авторов, на которых подписан текущий пользователь"""
    # Получаем подписки текущего пользователя
    following = Follow.objects.filter(user=request.user)
    # Получаем посты от авторов, на которых подписан текущий пользователь
    posts = Post.objects.filter(
        author__in=[follow.author for follow in following]
        )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {"page_obj": page_obj}
    
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    # Получаем пользователя, на которого хочет подписаться текущий пользователь
    author = get_object_or_404(User, user=username)
    # Проверяем, не пытается ли текущий пользователь подписаться на самого себя
    if request.author == author:
        return redirect('posts:profile', username=username)
    # Проверяем, не подписан ли уже текущий пользователь на этого автора
    if Follow.objects.filter(user=request.user, author=author).exists():
        return redirect('posts:profile', username=username)
    # Создаем запись о подписке
    Follow.objects.create(user=request.user, author=author)
    return redirect(request.META.get("HTTP_REFERER"))
    #redirect("posts:profile", username=username)

@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    # Получаем пользователя, от которого хочет отписаться текущий пользователь
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)