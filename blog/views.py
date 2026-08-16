from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Post, BlogCategory
from .forms import CommentForm

POSTS_PER_PAGE = 6


def blog_list(request):
    posts = Post.objects.filter(is_published=True).select_related('author', 'category')
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = posts.filter(category=selected_category)

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'categories': BlogCategory.objects.all(),
        'selected_category': selected_category,
        'recent_posts': Post.objects.filter(is_published=True)[:3],
    }
    return render(request, 'blog/blog.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    comments = post.comments.filter(is_approved=True)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been submitted and will appear once approved.')
            return redirect(post.get_absolute_url())
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'name': request.user.get_full_name() or request.user.username, 'email': request.user.email}
        form = CommentForm(initial=initial)

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'recent_posts': Post.objects.filter(is_published=True).exclude(pk=post.pk)[:3],
    }
    return render(request, 'blog/post_detail.html', context)
