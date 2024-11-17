
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.http import Http404
#from django.http import HttpRequest
from django.core.mail import send_mail

from django.views.generic import ListView

from django.views.decorators.http import require_POST

from .forms import EmailPostForm, CommentForm
from .models import Post
from taggit.models import Tag


class PostListView(ListView):
    """
    Alternative post list view
    """
    # use queryset to retrieve all objects.
    # alternative would be declaring the model model=Post and
    # django would retrieve all the posts
    queryset = Post.objects.all()
    # assign the results of the queryset, defaul variable is object_list
    context_object_name = 'posts'
    #define the pagination with by three objects per page
    paginate_by = 3
    # use custom template
    template_name = 'blog/post/list.html'
    
    
# recommend posts via email

def post_share(request, post_id):
    #Retrieve post by id
    post = get_object_or_404(
        Post,
        id = post_id,
        status = Post.Status.PUBLISHED
    )
    sent = False
    
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form field passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )
    
def post_list(request, tag_slug=None):
    
    # Retrieve only the published posts
    post_list = Post.published.all() 
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
         posts = paginator.page(page_number)
    except EmptyPage:
        # if page_number is out of range get last page results
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # if page_number is not an integer get the first page
        posts = paginator.page(1)
   
    # collect variables to be sendt to template into dictionary
    ctx = {
        'title': 'Published Posts',
        'posts': posts,
        'tag': tag,
    }
    
    return render(
        request,
        'blog/post/list.html',
        ctx
    )

def post_detail(request, year, month, day, post):
    
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day)
    
    # List of active comments for this post 
    comments = post.comments.filter(active=True)
    # form for users to comment
    form = CommentForm()
    
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form
        }
        
    )
    





@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    #A comment was posted 
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment 
        comment.post = post
        # save the comment to the database
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )