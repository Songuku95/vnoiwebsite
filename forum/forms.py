from datetime import datetime
from django import forms
from forum.models import Post, Topic


class PostForm(forms.ModelForm):

    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'size': '80'}))

    class Meta:
        model = Post
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.topic = kwargs.pop('topic', None)
        self.forum = kwargs.pop('forum', None)
        super(PostForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.forum = self.instance.topic.forum
        self.fields.keyOrder = [
            'title', 'content',
        ]


class PostCreateForm(PostForm):

    def __init__(self, *args, **kwargs):
        super(PostCreateForm, self).__init__(*args, **kwargs)
        if self.topic:
            self.fields['title'].required = False
            self.topic_post = False
        else:
            self.topic_post = True

    def save(self, commit=True):
        if not self.topic:
            # if this post create new topic, create this corresponding topic
            topic = Topic(forum=self.forum,
                          created_by=self.user,
                          title=self.cleaned_data['title'],)
            topic.save()
            self.topic = topic
        else:
            topic = self.topic

        post = Post(topic=topic,
                    created_by=self.user,
                    topic_post=True,
                    content=self.cleaned_data['content'])
        post.topic = topic
        if commit:
            post.save()
            if self.topic_post:
                topic.post = post
                topic.save()

        return post


class PostUpdateForm(PostForm):
    def __init__(self, *args, **kwargs):
        super(PostUpdateForm, self).__init__(*args, **kwargs)
        self.initial['title'] = self.instance.topic.title
        if not self.instance.topic_post:
            self.fields['title'].required = False

    def save(self, commit=True):
        post = self.instance
        post.updated_at = datetime.now()
        if commit:
            post.save()
