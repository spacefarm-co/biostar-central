"""
Model definitions.

Note: some models are denormalized by design, this greatly simplifies (and speeds up) 
the queries necessary to fetch a certain entry.

"""
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class UserProfile( models.Model ):
    """
    Stores user options

    >>> user, flag = User.objects.get_or_create(first_name='Jane', last_name='Doe', username='jane', email='jane')
    >>> prof = user.get_profile()
    >>> prof.json = dict( message='Hello world' )
    >>> prof.save()
    """
    user  = models.ForeignKey(User, unique=True)
    score = models.IntegerField(default=0, blank=True)
    json  = models.TextField(default="", null=True)
    last_visited = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    """
    A posting is the basic content generated by a user
    
    >>> user, flag = User.objects.get_or_create(first_name='Jane', last_name='Doe', username='jane', email='jane')
    >>> post, flag = Post.objects.get_or_create(author=user, bbcode='[i]A[i]')
    >>> post.html
    u'<em>A</em>'
    """
    author = models.ForeignKey(User)
    
    bbcode = models.TextField() # all user input is in bbcode
    html  = models.TextField() # this is generated from the bbcode when saving the model
    views = models.IntegerField(default=0, blank=True)
    score = models.IntegerField(default=0, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    lastedit_date = models.DateTimeField(auto_now=True)
    lastedit_user = models.ForeignKey(User, related_name='editor')
    
    def get_vote(self, user, vote_type):
        if user.is_anonymous():
            return None
        try:
            return self.votes.get(author=user, type=vote_type)
        except Vote.DoesNotExist:
            return None

class Question(models.Model):
    """
    A Question is Post with title and tags
    
    >>> user, flag = User.objects.get_or_create(first_name='Jane', last_name='Doe', username='jane', email='jane')
    >>> post, flag = Post.objects.get_or_create(author=user, bbcode='[i]A[i]')
    >>> question, flag = Question.objects.get_or_create(post=post, title='Test questions')
    >>> question.tags.add("snp", "codon", "microarray")
    """
    title   = models.TextField()
    answer_count = models.IntegerField(default=0, blank=True)
    post = models.ForeignKey(Post)
    tags = TaggableManager()

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers')
    post = models.ForeignKey(Post)

class Comment(models.Model):
    parent = models.ForeignKey(Post, related_name='comments')
    post = models.ForeignKey(Post, related_name='content')

VOTE_UP = 0
VOTE_DOWN = 1

VOTE_TYPES = ((VOTE_UP, 'Upvote'), (VOTE_DOWN, 'Downvote'))
POST_SCORE = { VOTE_UP:1, VOTE_DOWN:-1 }
USER_REP = { VOTE_UP:10, VOTE_DOWN:-2 }

class Vote(models.Model):
    """
    >>> user, flag = User.objects.get_or_create(first_name='Jane', last_name='Doe', username='jane', email='jane')
    >>> post, flag = Post.objects.get_or_create(author=user, bbcode='[i]A[i]')
    >>> vote = Vote(author=user, post=post, type=VOTE_UP)
    >>> vote.score()
    1
    """
    author = models.ForeignKey(User)
    post = models.ForeignKey(Post, related_name='votes')
    type = models.IntegerField(choices=VOTE_TYPES)
    
    def score(self):
        return POST_SCORE.get(self.type, 0)
    
    def reputation(self):
        return USER_REP.get(self.type, 0)
       

#
# Adding data model related signals
#
from django.db.models import signals
from biostar.libs import postmarkup

def create_profile(sender, instance, created, *args, **kwargs):
    "Post save hook for creating user profiles"
    if created:
        UserProfile.objects.create( user=instance )

def create_post(sender, instance, *args, **kwargs):
    "Pre save post information"
    # this converts the bbcode into HTML
    parse = postmarkup.create(use_pygments=False)
    instance.html = parse(instance.bbcode)
    if not hasattr(instance, 'lastedit_user'):
        instance.lastedit_user = instance.author

def vote_created(sender, instance, created, *args, **kwargs):
    "Updates score and reputation on vote creation "
    if created:
        post = instance.post
        prof = instance.post.author.get_profile()
        post.score += instance.score()
        prof.score += instance.reputation()
        post.save()
        prof.save()

def vote_deleted(sender, instance,  *args, **kwargs):
    "Updates score and reputation on vote deletion"
    post = instance.post
    prof = instance.post.author.get_profile()
    post.score -= instance.score()
    prof.score -= instance.reputation()
    post.save()
    prof.save()

signals.post_save.connect( create_profile, sender=User )
signals.pre_save.connect( create_post, sender=Post )

signals.post_save.connect( vote_created, sender=Vote )
signals.post_delete.connect( vote_deleted, sender=Vote )
