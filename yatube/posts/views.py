from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Follow
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .utils import paginator

User = get_user_model()
SECONDS_IN_CACHE = 20
# Извиняюсь, это я так криво сократил SECONDS)


@cache_page(SECONDS_IN_CACHE, key_prefix='index_page')
def index(request):
    title = 'Последние обновления на сайте'
    post_list = Post.objects.select_related('group', 'author')
    return render(
        request, 'posts/index.html',
        {'page_obj': paginator(post_list, request),
         'title': title},
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    group_list = group.posts.select_related('author')
    return render(
        request, 'posts/group_list.html',
        {'page_obj': paginator(group_list, request),
         'group': group},
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
    else:
        following = False
    context = {'author': author,
               'posts': posts,
               'following': following,
               'page_obj': paginator(posts, request)}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('group', 'author'),
                             id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(
        request, 'posts/post_detail.html',
        {'post': post, 'form': form, 'comments': comments})


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post.objects.select_related('group', 'author'),
                             id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('posts:post_detail', post_id=post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    # Приделал сюда еще select_related для оптимизации запросов. Но я все равно
    # не совсем понимаю, как работает фильтр author__following__user=...
    # Ну точнее понимаю так, что ORM перебирает все посты по одному, т.е.
    # берет каждый пост, по FK поля author получает объект User, из этого
    # объекта по обратной связи following получает объект модели Follow, в этом
    # объекте по FK получает объект поля User и сравнивает его с request.user
    #
    # Я пытался сделать так еще, по идее меньше нагрузки на БД: из модели
    # Follow получаем объекты, где поле user=request.user из этих объектов
    # получаем список значений поля author, далее выводим все посты, фильтруя
    # то, что значение поля author модели Post есть в списке подписанных
    # авторов, что-то типо Post.objects.filter(author__in = [authors])
    return render(
        request, 'posts/follow.html',
        {'posts': posts,
         'page_obj': paginator(posts, request)}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    following_author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=following_author).delete()
    return redirect('posts:profile', username)
