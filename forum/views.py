from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from forum.forms import PostCreateForm, PostUpdateForm
from forum.models import Topic, Forum, Post


def index(request):
    forums = Forum.objects.all()
    return render(request, 'forum/forum_index.html', {'forums': forums})


def topic_list(request, forum_id):
    forum = get_object_or_404(Forum, pk=forum_id)
    topics = Topic.objects.filter(forum_id=forum_id)
    return render(request, "forum/topic_list.html", {'forum': forum,
                                                     'topics': topics})


def topic_retrieve(request, forum_id, topic_id):
    forum = get_object_or_404(Forum, pk=forum_id)
    topic = get_object_or_404(Topic, pk=topic_id)
    posts = topic.posts.all()
    return render(request, "forum/topic_retrieve.html", {'forum': forum,
                                                         'topic': topic,
                                                         'posts': posts})


def list(request):
    return HttpResponse("this is list!")


@login_required
def post_create(request, forum_id=None, topic_id=None, template="forum/post_create.html"):

    topic = forum = None

    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    if topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)
        forum = topic.forum

    # TODO check permission

    if request.POST:
        # if a request is submitted, handle this request
        form = PostCreateForm(request.POST, user=request.user, forum=forum, topic=topic)
        if form.is_valid():
            post = form.save()
            if post.topic_post:
                return HttpResponseRedirect(reverse("forum:topic_retrieve", args=(forum.id, post.topic_id,)))
            else:
                return "sucessfully!"
    else:
        form = PostCreateForm()
        return render(request, template, {'form': form, 'forum': forum, 'topic': topic})


@login_required
def post_update(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # TODO: check permission

    if request.POST:
        form = PostUpdateForm(instance=post, user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../')
    else:
        form = PostUpdateForm(instance=post)
        return render(request, "forum/post_update.html", {'form': form})


@login_required
def topic_create(request, forum_id=None, template="forum/topic_create.html"):
    return post_create(request, forum_id, template=template)
