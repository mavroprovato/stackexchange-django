"""The application models
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres import indexes, search
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from stackexchange import enums, managers


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
    creation_date = models.DateTimeField(help_text="The user creation date", default=timezone.now)
    last_modified_date = models.DateTimeField(help_text="The user last modified date", auto_now=True, null=True)
    last_access_date = models.DateTimeField(help_text="The user last access date", null=True, blank=True)
    reputation = models.PositiveIntegerField(help_text="The user reputation", default=0)
    views = models.PositiveIntegerField(help_text="The user profile views", default=0)
    up_votes = models.PositiveIntegerField(help_text="The user up votes", default=0)
    down_votes = models.PositiveIntegerField(help_text="The user down votes", default=0)
    is_active = models.BooleanField(help_text="True if the user is active", default=True)
    is_moderator = models.BooleanField(help_text="True if the user is a moderator", default=False)
    is_employee = models.BooleanField(help_text="True if the user is an employee", default=False)

    objects = managers.UserManager()

    class Meta:
        db_table = 'users'
        indexes = (
            models.Index(fields=('-reputation', 'id')), models.Index(fields=('-creation_date', 'id')),
            models.Index(fields=('display_name', 'id')), models.Index(fields=('-last_modified_date', 'id'))
        )

    def __str__(self) -> str:
        """Return the string representation of the user.

        :return: The user display name.
        """
        return str(self.display_name)

    @property
    def is_staff(self) -> bool:
        """Returns true if the user is a member of the staff.

        :return: True if the user is a member of the staff.
        """
        return self.is_employee

    @property
    def is_superuser(self) -> bool:
        """Returns true if the user is a superuser.

        :return: True if the user is a superuser.
        """
        return self.is_employee

    def slug(self) -> str:
        """Return the slug for the user.

        :return: The slug for the user.
        """
        return slugify(self.display_name, allow_unicode=True)

    def get_absolute_url(self) -> str:
        """Get the absolute URL for the user.

        :return: The absolute URL for the user.
        """
        return reverse('web-user-detail-slug', args=(str(self.id), self.slug()))


class Badge(models.Model):
    """The badge model
    """
    name = models.CharField(help_text="The badge name", max_length=255, unique=True)
    badge_class = models.PositiveSmallIntegerField(
        help_text="The badge class", choices=((bc.value, bc.description) for bc in enums.BadgeClass))
    badge_type = models.PositiveSmallIntegerField(
        help_text="The badge type", choices=((bt.value, bt.description) for bt in enums.BadgeType))

    objects = managers.BadgeQuerySet().as_manager()

    class Meta:
        db_table = 'badges'

    def __str__(self) -> str:
        """Return the string representation of the badge.

        :return: The badge name.
        """
        return str(self.name)


class UserBadge(models.Model):
    """The user badge model.
    """
    user = models.ForeignKey(User, help_text="The user", on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, help_text="The badge", on_delete=models.CASCADE, related_name='users')
    date_awarded = models.DateTimeField(help_text="The date awarded", default=timezone.now)

    objects = managers.UserBadgeQuerySet().as_manager()

    class Meta:
        db_table = 'user_badges'
        indexes = (models.Index(fields=('-date_awarded', 'id')),)


class Post(models.Model):
    """The post model
    """
    type = models.PositiveSmallIntegerField(
        help_text="The post type", choices=((pt.value, pt.description) for pt in enums.PostType))
    title = models.CharField(help_text="The post title", max_length=1000, null=True, blank=True)
    body = models.TextField(help_text="The post body")
    question = models.ForeignKey(
        'Post', help_text="The post question, if the post type is ANSWER",
        on_delete=models.CASCADE, null=True, blank=True, related_name='answers')
    accepted_answer = models.ForeignKey(
        'Post', help_text="The accepted answer, if the post type is QUESTION", on_delete=models.CASCADE, null=True,
        blank=True, related_name='accepted_answers')
    owner = models.ForeignKey(User, help_text="The owner of the post", on_delete=models.CASCADE,
                              related_name='posts', null=True, blank=True)
    last_editor = models.ForeignKey(User, help_text="The last editor of the post", on_delete=models.CASCADE,
                                    related_name='last_edited_posts', null=True, blank=True)
    last_editor_display_name = models.CharField(help_text="The last editor display name", max_length=255, null=True,
                                                blank=True)
    creation_date = models.DateTimeField(help_text="The post creation date", default=timezone.now)
    last_edit_date = models.DateTimeField(help_text="The post last edit date", null=True, blank=True, auto_now=True)
    last_activity_date = models.DateTimeField(help_text="The post last activity date")
    community_owned_date = models.DateTimeField(help_text="The post community owned date", null=True, blank=True)
    closed_date = models.DateTimeField(help_text="The post closed date", null=True, blank=True)
    score = models.IntegerField(help_text="The post score")
    view_count = models.PositiveIntegerField(help_text="The post view count", null=True, blank=True)
    answer_count = models.PositiveIntegerField(help_text="The post answer count", null=True, blank=True)
    comment_count = models.PositiveIntegerField(help_text="The post comment count", null=True, blank=True)
    favorite_count = models.PositiveIntegerField(help_text="The post favorite count", null=True, blank=True)
    content_license = models.CharField(
        help_text="The content license", max_length=max([len(cl.name) for cl in enums.ContentLicense]),
        choices=[(cl.name, cl.value) for cl in enums.ContentLicense], default=enums.ContentLicense.CC_BY_SA_4_0.name)
    tags = models.ManyToManyField('Tag', related_name='posts', through='PostTag')
    title_search = search.SearchVectorField(null=True, help_text="The title search vector")

    class Meta:
        db_table = 'posts'
        indexes = (
            models.Index(fields=('-last_activity_date', 'id')), models.Index(fields=('-creation_date', 'id')),
            models.Index(fields=('-score', 'id')), indexes.GinIndex(fields=('title_search',)),
        )

    def __str__(self) -> str:
        """Return the string representation of the post.

        :return: The post title.
        """
        return str(self.title)

    def slug(self) -> str | None:
        """Return the slug for the post. Only set if the post is an answer.

        :return: The slug for the post.
        """
        if self.type == enums.PostType.QUESTION:
            return slugify(self.title)

    def get_absolute_url(self) -> str | None:
        """Get the absolute URL for the post.

        :return: The absolute URL for the post.
        """
        if self.type == enums.PostType.QUESTION.value:
            return reverse('web-question-detail-slug', args=(str(self.id), self.slug()))


class Comment(models.Model):
    """The comment model
    """
    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name='comments')
    score = models.IntegerField(help_text="The comment score")
    text = models.TextField(help_text="The comment text")
    creation_date = models.DateTimeField(help_text="The date that the comment was created", default=timezone.now)
    content_license = models.CharField(
        help_text="The content license", max_length=max([len(cl.name) for cl in enums.ContentLicense]),
        choices=[(cl.name, cl.value) for cl in enums.ContentLicense], default=enums.ContentLicense.CC_BY_SA_4_0.name)
    user = models.ForeignKey(User, help_text="The user for the comment", on_delete=models.CASCADE,
                             related_name='comments', null=True, blank=True)
    user_display_name = models.CharField(help_text="The user display name", max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'comments'
        indexes = (models.Index(fields=('-creation_date', 'id')), models.Index(fields=('-score', 'id')))

    def __str__(self) -> str:
        """Return the string representation of the comment.

        :return: The comment text.
        """
        return str(self.text)


class PostHistory(models.Model):
    """The post history model
    """
    type = models.PositiveSmallIntegerField(
        help_text="The post history type", choices=((pht.value, pht.description) for pht in enums.PostHistoryType))
    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name='history')
    revision_guid = models.UUIDField(help_text="The GUID of the action that created this history record")
    creation_date = models.DateTimeField(
        help_text="The date that this history record was created", default=timezone.now)
    user = models.ForeignKey(User, help_text="The user that created this history record", on_delete=models.CASCADE,
                             related_name='post_history', null=True, blank=True)
    user_display_name = models.CharField(
        help_text="The display name of the user that created this record, if the user has been removed and no longer "
                  "referenced by id", max_length=255, null=True, blank=True)
    comment = models.TextField(help_text="The comment of the user that has edited this post", null=True, blank=True)
    text = models.TextField(help_text="A raw version of the new value for a given revision", null=True, blank=True)
    content_license = models.CharField(
        help_text="The content license", max_length=max([len(cl.name) for cl in enums.ContentLicense]),
        choices=[(cl.name, cl.value) for cl in enums.ContentLicense], default=enums.ContentLicense.CC_BY_SA_4_0.name,
        null=True, blank=True)

    objects = managers.PostHistoryQuerySet().as_manager()

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

    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name='links')
    related_post = models.ForeignKey(Post, help_text="The related post", on_delete=models.CASCADE,
                                     related_name='related_links')
    type = models.PositiveSmallIntegerField(help_text="The post link type", choices=TYPE_CHOICES)

    class Meta:
        db_table = 'post_links'


class PostVote(models.Model):
    """The post vote model
    """
    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name='votes')
    type = models.PositiveSmallIntegerField(
        help_text="The post vote type", choices=((pvt.value, pvt.description) for pvt in enums.PostVoteType))
    creation_date = models.DateTimeField(help_text="The date that this vote was created", default=timezone.now)
    user = models.ForeignKey(
        User, help_text="The user for the post vote, if the post vote type is FAVORITE or BOUNTY_START",
        on_delete=models.CASCADE, related_name='user_votes', null=True, blank=True)
    bounty_amount = models.PositiveSmallIntegerField(
        help_text="The post bounty amount, if the post vote type is BOUNTY_START or BOUNTY_CLOSE", null=True,
        blank=True)

    class Meta:
        db_table = 'post_votes'
        indexes = (models.Index(fields=('-creation_date', '-id')),)


class Tag(models.Model):
    """The tag model
    """
    name = models.CharField(help_text="The tag name", max_length=255, unique=True)
    award_count = models.IntegerField(help_text="The tag award count")
    excerpt = models.ForeignKey(Post, help_text="The tag excerpt", on_delete=models.CASCADE,
                                related_name='excerpts', null=True, blank=True)
    wiki = models.ForeignKey(Post, help_text="The tag wiki", on_delete=models.CASCADE, related_name='wikis',
                             null=True, blank=True)
    required = models.BooleanField(help_text="True if the tag fulfills required tag constraints", default=False)
    moderator_only = models.BooleanField(help_text="True if the tag can only be used by moderators", default=False)

    class Meta:
        db_table = 'tags'

    def __str__(self) -> str:
        """Return the string representation of the tag.

        :return: The tag name.
        """
        return str(self.name)


class PostTag(models.Model):
    """The post tag model
    """
    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name='post_tags')
    tag = models.ForeignKey(Tag, help_text="The tag", on_delete=models.CASCADE, related_name='post_tags')

    class Meta:
        db_table = 'post_tags'
        unique_together = ['post', 'tag']
