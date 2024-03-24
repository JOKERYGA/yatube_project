from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .forms import PostForm


User = get_user_model()


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
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


# groups = Group.objects.all()
def group_posts(request, slug):
    # Получаем объект группы по переданному slug или возвращаем ошибку 404, если группа не найдена
    group = get_object_or_404(Group, slug=slug)
    group_posts = Post.objects.filter(group=group).order_by("-pub_date")[:10]
    context = {"group": group, "group_posts": group_posts}
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

    context = {"post": post}
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", username=request.user.username)

        return render(request, "posts/create_post.html", {"form": form})
    else:
        form = PostForm()
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
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
