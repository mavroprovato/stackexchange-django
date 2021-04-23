"""The application models
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from stackexchange import managers


class User(AbstractBaseUser, PermissionsMixin):
    """The user model
    """
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email', )

    username = models.CharField(help_text="The user name", max_length=255, unique=True)
    email = models.EmailField(help_text="The user email", max_length=255, unique=True)
    display_name = models.CharField(help_text="The user display name", max_length=255)
    website_url = models.URLField(help_text="The user web site URL", null=True, blank=True)
    location = models.CharField(help_text="The user location", max_length=255, null=True, blank=True)
    about = models.TextField(help_text="The user about information", null=True, blank=True)
    creation_date = models.DateTimeField(help_text="The user creation date", auto_now_add=True)
    reputation = models.PositiveIntegerField(help_text="The user reputation", default=0)
    views = models.PositiveIntegerField(help_text="The user profile views", default=0)
    up_votes = models.PositiveIntegerField(help_text="The user up votes", default=0)
    down_votes = models.PositiveIntegerField(help_text="The user down votes", default=0)
    is_active = models.BooleanField(help_text="If the user is active", default=True)
    is_employee = models.BooleanField(help_text="If the user is an employee", default=False)

    objects = managers.UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        """Return the string representation of the user

        :return: The user display name
        """
        return str(self.display_name)

    @property
    def is_staff(self):
        """Returns true if the user is a member of the staff.

        :return: True if the user is a member of the staff.
        """
        return self.is_employee

    @property
    def is_superuser(self):
        """Returns true if the user is a superuser.

        :return: True if the user is a superuser.
        """
        return self.is_employee


class Badge(models.Model):
    """The badge model
    """
    CLASS_GOLD = 1
    CLASS_SILVER = 2
    CLASS_BRONZE = 3

    CLASS_CHOICES = (
        (CLASS_GOLD, 'gold'),
        (CLASS_SILVER, 'silver'),
        (CLASS_BRONZE, 'bronze'),
    )
    name = models.CharField(help_text="The badge name", max_length=255, unique=True)
    badge_class = models.SmallIntegerField(help_text="The badge class", choices=CLASS_CHOICES)
    tag_based = models.BooleanField(help_text="If the badge is tag based")

    class Meta:
        db_table = 'badges'

    def __str__(self) -> str:
        """Return the string representation of the badge

        :return: The badge name
        """
        return str(self.name)


class UserBadge(models.Model):
    """The user badge model.
    """
    user = models.ForeignKey(User, help_text="The user", on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, help_text="The badge", on_delete=models.CASCADE, related_name='users')
    date_awarded = models.DateTimeField(help_text="The date awarded", auto_now_add=True)

    class Meta:
        db_table = 'user_badges'


class Post(models.Model):
    """The post model
    """
    TYPE_QUESTION = 1
    TYPE_ANSWER = 2
    TYPE_WIKI = 3
    TYPE_TAG_WIKI_EXPERT = 4
    TYPE_TAG_WIKI = 5
    TYPE_MODERATOR_NOMINATION = 6
    TYPE_WIKI_PLACEHOLDER = 7
    TYPE_PRIVILEGE_WIKI = 8

    TYPE_CHOICES = (
        (TYPE_QUESTION, 'Question'),
        (TYPE_ANSWER, 'Answer'),
        (TYPE_WIKI, 'Wiki'),
        (TYPE_TAG_WIKI_EXPERT, 'Tag Wiki Expert'),
        (TYPE_MODERATOR_NOMINATION, 'Moderator Nomination'),
        (TYPE_WIKI_PLACEHOLDER, 'Wiki Placeholder'),
        (TYPE_PRIVILEGE_WIKI, 'Privilege Wiki'),
    )

    title = models.CharField(help_text="The post title", max_length=1000, null=True, blank=True)
    body = models.TextField(help_text="The post body")
    type = models.PositiveSmallIntegerField(help_text="The post type", choices=TYPE_CHOICES)
    creation_date = models.DateTimeField(help_text="The post creation date", auto_now_add=True)
    last_edit_date = models.DateTimeField(help_text="The post last edit date", null=True, blank=True, auto_now=True)
    last_activity_date = models.DateTimeField(help_text="The post last activity date")
    score = models.IntegerField(help_text="The post score")
    view_count = models.PositiveIntegerField(help_text="The post view count", null=True, blank=True)
    answer_count = models.PositiveIntegerField(help_text="The post answer count", null=True, blank=True)
    comment_count = models.PositiveIntegerField(help_text="The post comment count", null=True, blank=True)
    favorite_count = models.PositiveIntegerField(help_text="The post favorite count", null=True, blank=True)
    owner = models.ForeignKey(User, help_text="The owner of the post", on_delete=models.CASCADE,
                              related_name='owner_posts', null=True, blank=True)
    last_editor = models.ForeignKey(User, help_text="The last editor of the post", on_delete=models.CASCADE,
                                    related_name='last_editor_posts', null=True, blank=True)
    parent = models.ForeignKey('Post', help_text="The parent post", on_delete=models.CASCADE, null=True, blank=True,
                               related_name='children')
    accepted_answer = models.ForeignKey('Post', help_text="The accepted answer", on_delete=models.CASCADE, null=True,
                                        blank=True, related_name='accepted_answers')
    tags = models.ManyToManyField('Tag', related_name='posts', through='PostTag')

    class Meta:
        db_table = 'posts'


class Comment(models.Model):
    """The comment model
    """
    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name="post_comments")
    score = models.IntegerField(help_text="The comment score")
    text = models.TextField(help_text="The comment text")
    creation_date = models.DateTimeField(help_text="The date that the comment was created", auto_now_add=True)
    user = models.ForeignKey(User, help_text="The user for the comment", on_delete=models.CASCADE,
                             related_name='user_comments', null=True, blank=True)

    class Meta:
        db_table = 'comments'


class PostHistory(models.Model):
    """The post history model
    """
    TYPE_INITIAL_TITLE = 1
    TYPE_INITIAL_BODY = 2
    TYPE_INITIAL_TAGS = 3
    TYPE_EDIT_TITLE = 4
    TYPE_EDIT_BODY = 5
    TYPE_EDIT_TAGS = 6
    TYPE_ROLLBACK_TITLE = 7
    TYPE_ROLLBACK_BODY = 8
    TYPE_ROLLBACK_TAGS = 9
    TYPE_POST_CLOSED = 10
    TYPE_POST_REOPENED = 11
    TYPE_POST_DELETED = 12
    TYPE_POST_UNDELETED = 13
    TYPE_POST_LOCKED = 14
    TYPE_POST_UNLOCKED = 15
    TYPE_COMMUNITY_OWNED = 16
    TYPE_POST_MIGRATED = 17
    TYPE_QUESTION_MERGED = 18
    TYPE_QUESTION_PROTECTED = 19
    TYPE_QUESTION_UNPROTECTED = 20
    TYPE_POST_DISASSOCIATED = 21
    TYPE_QUESTION_UNMERGED = 22

    TYPE_CHOICES = (
        (TYPE_INITIAL_TITLE, 'Initial Title'),
        (TYPE_INITIAL_BODY, 'Initial Body'),
        (TYPE_INITIAL_TAGS, 'Initial Tags'),
        (TYPE_EDIT_TITLE, 'Edit Title'),
        (TYPE_EDIT_BODY, 'Edit Body'),
        (TYPE_EDIT_TAGS, 'Edit Tags'),
        (TYPE_ROLLBACK_TITLE, 'Rollback Title'),
        (TYPE_ROLLBACK_BODY, 'Rollback Body'),
        (TYPE_ROLLBACK_TAGS, 'Rollback Tags'),
        (TYPE_POST_CLOSED, 'Post Closed'),
        (TYPE_POST_REOPENED, 'Post Reopened'),
        (TYPE_POST_DELETED, 'Post Deleted'),
        (TYPE_POST_UNDELETED, 'Post Undeleted'),
        (TYPE_POST_LOCKED, 'Post Locked'),
        (TYPE_POST_UNLOCKED, 'Post Unlocked'),
        (TYPE_COMMUNITY_OWNED, 'Community Owned'),
        (TYPE_POST_MIGRATED, 'Post Migrated'),
        (TYPE_QUESTION_MERGED, 'Question Merged'),
        (TYPE_QUESTION_PROTECTED, 'Question Protected'),
        (TYPE_QUESTION_UNPROTECTED, 'Question Unprotected'),
        (TYPE_POST_DISASSOCIATED, 'Post Disassociated'),
        (TYPE_QUESTION_UNMERGED, 'Question Unmerged'),
    )

    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name="post_history")
    type = models.PositiveSmallIntegerField(help_text="The post history type", choices=TYPE_CHOICES)
    revision_guid = models.CharField(help_text="The GUID of the action that created this history record", max_length=36)
    creation_date = models.DateTimeField(help_text="The date that this history record was created", auto_now_add=True)
    user = models.ForeignKey(User, help_text="The user that created this history record", on_delete=models.CASCADE,
                             related_name='user_post_history', null=True, blank=True)
    user_display_name = models.CharField(
        help_text="The display name of the user that created this record, if the user has been removed and no longer "
                  "referenced by id", max_length=255, null=True, blank=True)
    comment = models.TextField(help_text="The comment of the user that has edited this post", null=True, blank=True)
    text = models.TextField(help_text="The new value for a given revision", null=True, blank=True)

    class Meta:
        db_table = 'post_history'
        verbose_name_plural = 'post history'


class PostLink(models.Model):
    """The post link model
    """
    TYPE_LINKED = 1
    TYPE_DUPLICATE = 3

    TYPE_CHOICES = (
        (TYPE_LINKED, 'Linked'),
        (TYPE_DUPLICATE, 'Duplicate'),
    )

    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name="post_links")
    related_post = models.ForeignKey(Post, help_text="The related post", on_delete=models.CASCADE,
                                     related_name="related_post_links")
    type = models.PositiveSmallIntegerField(help_text="The post link type", choices=TYPE_CHOICES)

    class Meta:
        db_table = 'post_links'


class PostVote(models.Model):
    """The post vote model
    """
    TYPE_ACCEPTED_BY_ORIGINATOR = 1
    TYPE_UP_MOD = 2
    TYPE_DOWN_MOD = 3
    TYPE_OFFENSIVE = 4
    TYPE_FAVORITE = 5
    TYPE_CLOSE = 6
    TYPE_REOPEN = 7
    TYPE_BOUNTY_START = 8
    TYPE_BOUNTY_CLOSE = 9
    TYPE_DELETION = 10
    TYPE_UN_DELETION = 11
    TYPE_SPAM = 12
    TYPE_INFORM_MODERATOR = 13

    TYPE_CHOICES = (
        (TYPE_ACCEPTED_BY_ORIGINATOR, 'AcceptedByOriginator'),
        (TYPE_UP_MOD, 'UpMod'),
        (TYPE_DOWN_MOD, 'DownMod'),
        (TYPE_OFFENSIVE, 'Offensive'),
        (TYPE_FAVORITE, 'Favorite'),
        (TYPE_CLOSE, 'Close'),
        (TYPE_REOPEN, 'Reopen'),
        (TYPE_BOUNTY_START, 'Bounty Start'),
        (TYPE_BOUNTY_CLOSE, 'Bounty Close'),
        (TYPE_DELETION, 'Deletion'),
        (TYPE_UN_DELETION, 'Un-deletion'),
        (TYPE_SPAM, 'Spam'),
        (TYPE_INFORM_MODERATOR, 'Inform Moderator'),
    )

    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name="post_votes")
    type = models.SmallIntegerField(help_text="The post vote type", choices=TYPE_CHOICES)
    user = models.ForeignKey(User, help_text="The user for the vote", on_delete=models.CASCADE,
                             related_name='user_votes', null=True, blank=True)
    creation_date = models.DateTimeField(help_text="The date that this vote was created", auto_now_add=True)

    class Meta:
        db_table = 'post_votes'


class Tag(models.Model):
    """The tag model
    """
    name = models.CharField(help_text="The tag name", max_length=255, unique=True)
    count = models.IntegerField(help_text="The tag count")
    excerpt = models.ForeignKey(Post, help_text="The tag excerpt", on_delete=models.CASCADE,
                                related_name='tag_excerpts', null=True, blank=True)
    wiki = models.ForeignKey(Post, help_text="The tag wiki", on_delete=models.CASCADE, related_name='tag_wikis',
                             null=True, blank=True)

    class Meta:
        db_table = 'tags'

    def __str__(self) -> str:
        """Return the string representation of the tag

        :return: The tag name
        """
        return str(self.name)


class PostTag(models.Model):
    """The post tag model
    """
    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name="post_tags")
    tag = models.ForeignKey(Tag, help_text="The tag", on_delete=models.CASCADE, related_name="post_tags")

    class Meta:
        db_table = 'post_tags'
