from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Apply Listview  using generic to display posts
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail

# Create your views here.
def post_list(request):
    #posts = Post.objects.all()
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts})


def	post_detail(request, year, month, day, post):
    #print("\n\n\n\n",post,post,year,month,day)
    post	=	get_object_or_404(Post,	slug=post, status='published',
    publish__year=year,publish__month=month,publish__day=day)

    # List for active comments in this post
    comments = post.comments.filter(active = True)
    new_comment = None
    if request.method == 'POST':
        # comment was posted
        comment_form = CommentForm(data = request.POST)
        if comment_form.is_valid():
            # Create Comment object don't save to database
            new_comment = comment_form.save(commit = False)

            # Assign the current post to commit
            new_comment.post= post

            # save the comment to database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post':post,'comments':comments, 'new_comment':new_comment,'comment_form':comment_form})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name= 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # Retrive post by Id
    post = get_object_or_404(Post, id= post_id, status = 'published')
    sent = False
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form fields passed validation
            cd = form.cleaned_data
            # ...Send Mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you rendering "{}"'.format(cd['name'],cd['email'],post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'apssdcsip@gmail.com', [cd['to']])
            sent = True
    
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form':form, 'sent':sent})