from django.db import models


class User(models.Model):
    """The user model
    """
    display_name = models.CharField(help_text="The user display name", max_length=255)
    website = models.URLField(help_text="The user web site", null=True, blank=True)
    location = models.CharField(help_text="The user location", max_length=255, null=True, blank=True)
    about = models.TextField(help_text="The user about information", null=True, blank=True)
    created = models.DateField(help_text="The user creation date")
    reputation = models.PositiveIntegerField(help_text="The user reputation")
    views = models.PositiveIntegerField(help_text="The user profile views")
    up_votes = models.PositiveIntegerField(help_text="The user up votes")
    down_votes = models.PositiveIntegerField(help_text="The user down votes")

    class Meta:
        db_table = 'users'


class Badge(models.Model):
    """The badge model
    """
    name = models.CharField(help_text="The badge name", max_length=255, unique=True)
    badge_class = models.SmallIntegerField(help_text="The badge class")
    tag_based = models.BooleanField(help_text="If the badge is tag based")

    class Meta:
        db_table = 'badges'


class UserBadge(models.Model):
    """The user badge model.
    """
    user = models.ForeignKey(User, help_text="The user", on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, help_text="The badge", on_delete=models.CASCADE, related_name='user_badges')
    date_awarded = models.DateTimeField(help_text="The date awarded")

    class Meta:
        db_table = 'user_badges'


class Post(models.Model):
    """The post model
    """
    TYPE_QUESTION = 'question'
    TYPE_ANSWER = 'answer'
    TYPE_WIKI = 'wiki'
    TYPE_TAG_WIKI_EXPERT = 'tag_wiki_expert'
    TYPE_TAG_WIKI = 'tag_wiki'
    TYPE_MODERATOR_NOMINATION = 'moderator_nomination'
    TYPE_WIKI_PLACEHOLDER = 'wiki_placeholder'
    TYPE_PRIVILEGE_WIKI = 'privilege_wiki'

    title = models.CharField(help_text="The post title", max_length=1000, null=True, blank=True)
    body = models.TextField(help_text="The post body")
    type = models.CharField(help_text="The post type", max_length=30)
    created = models.DateField(help_text="The post creation date")
    last_edit = models.DateField(help_text="The post last edit date", null=True, blank=True)
    last_activity = models.DateField(help_text="The post last activity date")
    score = models.IntegerField(help_text="The post score")
    view_count = models.PositiveIntegerField(help_text="The post view count", null=True, blank=True)
    answer_count = models.PositiveIntegerField(help_text="The post answer count", null=True, blank=True)
    comment_count = models.PositiveIntegerField(help_text="The post comment count", null=True, blank=True)
    favorite_count = models.PositiveIntegerField(help_text="The post favorite count", null=True, blank=True)
    owner = models.ForeignKey(User, help_text="The owner", on_delete=models.CASCADE, related_name='owner_posts',
                              null=True, blank=True)
    last_editor = models.ForeignKey(User, help_text="The owner", on_delete=models.CASCADE,
                                    related_name='last_editor_posts', null=True, blank=True)

    class Meta:
        db_table = 'posts'


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


class PostTag(models.Model):
    """The post tag model
    """
    post = models.ForeignKey(Post, help_text="The post", on_delete=models.CASCADE, related_name="post_tags")
    tag = models.ForeignKey(Tag, help_text="The tag", on_delete=models.CASCADE, related_name="post_tags")

    class Meta:
        db_table = 'post_tags'
