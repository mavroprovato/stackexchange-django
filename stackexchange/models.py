"""The application models
"""
from django.contrib.postgres import indexes, search
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from sites import models as sites_models
from stackexchange import enums, managers


class SiteUser(models.Model):
    """The site user model.
    """
    site = models.ForeignKey(sites_models.Site, on_delete=models.CASCADE, help_text="The site")
    unique_id = models.IntegerField(help_text="The site unique user ID across all sites", unique=True)
    display_name = models.CharField(max_length=255, help_text="The site user display name")
    website_url = models.URLField(null=True, blank=True, help_text="The user web site URL")
    location = models.CharField(null=True, max_length=255, blank=True, help_text="The user location")
    about = models.TextField(null=True, blank=True, help_text="The user about information")
    creation_date = models.DateTimeField(auto_now_add=True, help_text="The site user creation date")
    last_modified_date = models.DateTimeField(auto_now=True, help_text="The site user last modified date")
    last_access_date = models.DateTimeField(help_text="The site user last access date")
    reputation = models.PositiveIntegerField(default=0, help_text="The site user reputation")
    views = models.PositiveIntegerField(default=0, help_text="The site user views")
    up_votes = models.PositiveIntegerField(default=0, help_text="The site user up votes")
    down_votes = models.PositiveIntegerField(default=0, help_text="The site user down votes")

    objects = managers.SiteUserQuerySet.as_manager()

    class Meta:
        db_table = 'site_users'
        indexes = models.Index(fields=('site', 'unique_id')),

    def __str__(self) -> str:
        """Return the string representation of the site user.

        :return: The user display name.
        """
        return str(self.display_name)


class Badge(models.Model):
    """The badge model.
    """
    name = models.CharField(max_length=255, unique=True, help_text="The badge name")
    badge_class = models.PositiveSmallIntegerField(
        choices=((bc.value, bc.description) for bc in enums.BadgeClass), help_text="The badge class")
    badge_type = models.PositiveSmallIntegerField(
        choices=((bt.value, bt.description) for bt in enums.BadgeType), help_text="The badge type")

    objects = managers.BadgeQuerySet.as_manager()

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
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name='badges', help_text="The site user")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='users', help_text="The badge")
    date_awarded = models.DateTimeField(default=timezone.now, help_text="The date awarded")

    objects = managers.UserBadgeQuerySet.as_manager()

    class Meta:
        db_table = 'user_badges'
        indexes = (models.Index(fields=('-date_awarded', 'id')),)


class Post(models.Model):
    """The post model.
    """
    question = models.ForeignKey(
        'Post', on_delete=models.CASCADE, null=True, blank=True, related_name='answers',
        help_text="The post question, if the post type is ANSWER")
    accepted_answer = models.ForeignKey(
        'Post', on_delete=models.CASCADE, null=True, blank=True, related_name='accepted_answers',
        help_text="The accepted answer, if the post type is QUESTION")
    owner = models.ForeignKey(
        SiteUser, on_delete=models.CASCADE, null=True, blank=True, related_name='posts',
        help_text="The owner of the post")
    last_editor = models.ForeignKey(
        SiteUser, on_delete=models.CASCADE, related_name='last_edited_posts', null=True, blank=True,
        help_text="The last editor of the post")
    type = models.PositiveSmallIntegerField(
        choices=((pt.value, pt.description) for pt in enums.PostType), help_text="The post type")
    title = models.CharField(max_length=1000, null=True, blank=True, help_text="The post title")
    body = models.TextField(help_text="The post body")
    last_editor_display_name = models.CharField(
        max_length=255, null=True, blank=True, help_text="The last editor display name")
    creation_date = models.DateTimeField(default=timezone.now, help_text="The post creation date")
    last_edit_date = models.DateTimeField(null=True, blank=True, auto_now=True, help_text="The post last edit date")
    last_activity_date = models.DateTimeField(help_text="The post last activity date")
    community_owned_date = models.DateTimeField(null=True, blank=True, help_text="The post community owned date")
    closed_date = models.DateTimeField(null=True, blank=True, help_text="The post closed date")
    score = models.IntegerField(help_text="The post score")
    view_count = models.PositiveIntegerField(default=0, help_text="The post view count")
    answer_count = models.PositiveIntegerField(default=0, help_text="The post answer count")
    comment_count = models.PositiveIntegerField(default=0, help_text="The post comment count")
    favorite_count = models.PositiveIntegerField(default=0, help_text="The post favorite count")
    content_license = models.CharField(
        max_length=max(len(cl.value) for cl in enums.ContentLicense),
        choices=((cl.name, cl.value) for cl in enums.ContentLicense), default=enums.ContentLicense.CC_BY_SA_4_0.name,
        help_text="The content license")
    tags = models.ManyToManyField('Tag', related_name='posts', through='PostTag', help_text="The post tags")
    title_search = search.SearchVectorField(null=True, help_text="The title search vector")

    class Meta:
        db_table = 'posts'
        indexes = (
            models.Index(fields=('-last_activity_date', 'id')), models.Index(fields=('-creation_date', 'id')),
            models.Index(fields=('-score', 'id')), indexes.GinIndex(fields=('title_search',))
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
        if self.type == enums.PostType.QUESTION.value:
            return slugify(self.title)

        return None

    def get_absolute_url(self) -> str | None:
        """Get the absolute URL for the post.

        :return: The absolute URL for the post.
        """
        if self.type == enums.PostType.QUESTION.value:
            return reverse('web-question-detail-slug', args=(str(self.id), self.slug()))

        return None


class Tag(models.Model):
    """The tag model
    """
    name = models.CharField(max_length=255, unique=True, help_text="The tag name")
    excerpt = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='excerpts', null=True, blank=True, help_text="The tag excerpt")
    wiki = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='wikis', null=True, blank=True, help_text="The tag wiki")
    award_count = models.IntegerField(help_text="The tag award count")
    moderator_only = models.BooleanField(default=False, help_text="Tag is for moderators only")
    required = models.BooleanField(default=False, help_text="Tag is required")

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
        unique_together = ('post', 'tag')


class PostVote(models.Model):
    """The post vote model
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes', help_text="The post")
    user = models.ForeignKey(
        SiteUser, on_delete=models.CASCADE, null=True, blank=True, related_name='votes',
        help_text="The user for the post vote, if the post vote type is FAVORITE or BOUNTY_START")
    type = models.PositiveSmallIntegerField(
        choices=((pvt.value, pvt.description) for pvt in enums.PostVoteType), help_text="The post vote type")
    creation_date = models.DateTimeField(help_text="The date that this vote was created", default=timezone.now)
    bounty_amount = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="The post bounty amount, if the post vote type is BOUNTY_START or BOUNTY_CLOSE")

    class Meta:
        db_table = 'post_votes'
        indexes = (models.Index(fields=('-creation_date', '-id')),)


class PostComment(models.Model):
    """The post comment model
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', help_text="The post")
    user = models.ForeignKey(
        SiteUser, on_delete=models.CASCADE, null=True, blank=True, related_name='comments',
        help_text="The user for the comment")
    score = models.IntegerField(help_text="The comment score")
    text = models.TextField(help_text="The comment text")
    creation_date = models.DateTimeField(default=timezone.now, help_text="The date that the comment was created")
    content_license = models.CharField(
        help_text="The content license", max_length=max(len(cl.value) for cl in enums.ContentLicense),
        choices=((cl.name, cl.value) for cl in enums.ContentLicense), default=enums.ContentLicense.CC_BY_SA_4_0.name)
    user_display_name = models.CharField(max_length=255, null=True, blank=True, help_text="The user display name")

    class Meta:
        db_table = 'post_comments'
        indexes = (models.Index(fields=('-creation_date', 'id')), models.Index(fields=('-score', 'id')))

    def __str__(self) -> str:
        """Return the string representation of the post comment.

        :return: The comment text.
        """
        return str(self.text)


class PostHistory(models.Model):
    """The post history model
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='history', help_text="The post")
    user = models.ForeignKey(
        SiteUser, on_delete=models.CASCADE, null=True, blank=True, related_name='post_history',
        help_text="The user that created this history record")
    type = models.PositiveSmallIntegerField(
        choices=((pht.value, pht.description) for pht in enums.PostHistoryType), help_text="The post history type")
    revision_guid = models.UUIDField(help_text="The GUID of the action that created this history record", db_index=True)
    creation_date = models.DateTimeField(
        help_text="The date that this history record was created", default=timezone.now)
    user_display_name = models.CharField(
        max_length=255, null=True, blank=True, help_text="The display name of the user that created this record")
    comment = models.TextField(null=True, blank=True, help_text="The comment of the user that has edited this post")
    text = models.TextField(null=True, blank=True, help_text="A raw version of the new value for a given revision")
    content_license = models.CharField(
       max_length=max(len(cl.value) for cl in enums.ContentLicense),
       choices=((cl.name, cl.value) for cl in enums.ContentLicense), default=enums.ContentLicense.CC_BY_SA_4_0.name,
       help_text="The content license")

    objects = managers.PostHistoryQuerySet.as_manager()

    class Meta:
        db_table = 'post_history'
        verbose_name_plural = 'post history'


class PostLink(models.Model):
    """The post link model
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='links', help_text="The post")
    related_post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='related_links', help_text="The related post")
    type = models.PositiveSmallIntegerField(
        choices=((pht.value, pht.description) for pht in enums.PostLinkType), help_text="The post link type")

    class Meta:
        db_table = 'post_links'
