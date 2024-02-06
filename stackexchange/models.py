"""The application models
"""
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone

from stackexchange import enums, managers


class User(AbstractBaseUser):
    """The user model.
    """
    USERNAME_FIELD = 'username'

    username = models.CharField(max_length=255, unique=True, help_text="The user name")
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True, help_text="The user email")
    staff = models.BooleanField(default=False, help_text="True if the user is member of the staff")

    objects = managers.UserManager()

    class Meta:
        db_table = 'users'

    def is_staff(self) -> bool:
        """Return True if the user is a staff user.

        :return: True if the user is a staff user.
        """
        return self.staff

    def has_perm(self, *_) -> bool:
        """Return True if the user has the specified permission. Admin users have all permissions.

        :return: True if the user is an admin user.
        """
        return self.is_staff()

    def has_perms(self, perm_list, obj=None) -> bool:
        """Return True if the user has each of the specified permissions. If object is passed, check if the user has all
        required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, *_) -> bool:
        """Return True if the user has any permissions in the given app label. Admin users have all permissions.

        :return: True if the user is an admin user.
        """
        return self.is_staff()


class Site(models.Model):
    """The site model.
    """
    name = models.CharField(max_length=32, unique=True, help_text="The site name")
    description = models.CharField(max_length=64, unique=True, help_text="The site description")
    long_description = models.CharField(max_length=128, unique=True, help_text="The site long description")
    url = models.URLField(help_text="The site URL")
    image_url = models.URLField(help_text="The site image URL")
    icon_url = models.URLField(help_text="The site icon URL")
    badge_icon_url = models.URLField(help_text="The site badge icon URL")
    tag_css = models.TextField(help_text="CSS for tags")
    tagline = models.CharField(max_length=256, help_text="The site tagline")
    total_questions = models.PositiveIntegerField(help_text="The site total question count")
    total_answers = models.PositiveIntegerField(help_text="The site total answer count")
    total_users = models.PositiveIntegerField(help_text="The site total user count")
    total_comments = models.PositiveIntegerField(help_text="The site total comment count")
    total_tags = models.PositiveIntegerField(help_text="The site total tag count")
    last_post = models.DateTimeField(help_text="The date of the last post")
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, help_text="The parent site")

    class Meta:
        db_table = 'sites'

    def __str__(self) -> str:
        """Return the string representation of the site.

        :return: The site name.
        """
        return str(self.name)


class SiteUser(models.Model):
    """The site user model.
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, help_text="The site")
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The user", null=True, blank=True)
    site_user_id = models.IntegerField(help_text="The site user id")
    display_name = models.CharField(max_length=255, help_text="The site user display name")
    website_url = models.URLField(null=True, blank=True, help_text="The user web site URL")
    location = models.CharField(null=True, max_length=255, blank=True, help_text="The user location")
    about = models.TextField(null=True, blank=True, help_text="The user about information")
    creation_date = models.DateTimeField(help_text="The site user creation data")
    last_access_date = models.DateTimeField(help_text="The site user last access data")
    reputation = models.PositiveIntegerField(help_text="The site user reputation")
    views = models.PositiveIntegerField(help_text="The site user views")
    up_votes = models.PositiveIntegerField(help_text="The site user up votes")
    down_votes = models.PositiveIntegerField(help_text="The site user down votes")

    class Meta:
        db_table = 'site_users'
        unique_together = ('site', 'site_user_id')

    def __str__(self) -> str:
        """Return the string representation of the site user.

        :return: The user display name.
        """
        return str(self.display_name)


class Badge(models.Model):
    """The badge model.
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, help_text="The site")
    name = models.CharField(max_length=255, help_text="The badge name")
    badge_class = models.PositiveSmallIntegerField(
        choices=((bc.value, bc.description) for bc in enums.BadgeClass), help_text="The badge class")
    badge_type = models.PositiveSmallIntegerField(
        choices=((bt.value, bt.description) for bt in enums.BadgeType), help_text="The badge type")

    objects = managers.BadgeQuerySet().as_manager()

    class Meta:
        db_table = 'badges'
        unique_together = ('site', 'name')

    def __str__(self) -> str:
        """Return the string representation of the badge.

        :return: The badge name.
        """
        return str(self.name)


class UserBadge(models.Model):
    """The user badge model.
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, help_text="The site")
    user = models.ForeignKey(SiteUser, help_text="The user", on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, help_text="The badge", on_delete=models.CASCADE, related_name='users')
    date_awarded = models.DateTimeField(help_text="The date awarded", default=timezone.now)

    objects = managers.UserBadgeQuerySet().as_manager()

    class Meta:
        db_table = 'user_badges'


class Post(models.Model):
    """The post model.
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, help_text="The site")
    site_post_id = models.IntegerField(help_text="The site post id")
    question = models.ForeignKey(
        'Post', help_text="The post question, if the post type is ANSWER",
        on_delete=models.CASCADE, null=True, blank=True, related_name='answers')
    accepted_answer = models.ForeignKey(
        'Post', help_text="The accepted answer, if the post type is QUESTION", on_delete=models.CASCADE, null=True,
        blank=True, related_name='accepted_answers')
    owner = models.ForeignKey(
        SiteUser, help_text="The owner of the post", on_delete=models.CASCADE, related_name='posts', null=True,
        blank=True)
    last_editor = models.ForeignKey(
        SiteUser, help_text="The last editor of the post", on_delete=models.CASCADE, related_name='last_edited_posts',
        null=True, blank=True)
    type = models.PositiveSmallIntegerField(
        help_text="The post type", choices=((pt.value, pt.description) for pt in enums.PostType))
    title = models.CharField(help_text="The post title", max_length=1000, null=True, blank=True)
    body = models.TextField(help_text="The post body")
    last_editor_display_name = models.CharField(
        help_text="The last editor display name", max_length=255, null=True, blank=True)
    creation_date = models.DateTimeField(help_text="The post creation date", default=timezone.now)
    last_edit_date = models.DateTimeField(help_text="The post last edit date", null=True, blank=True, auto_now=True)
    last_activity_date = models.DateTimeField(help_text="The post last activity date")
    community_owned_date = models.DateTimeField(help_text="The post community owned date", null=True, blank=True)
    closed_date = models.DateTimeField(help_text="The post closed date", null=True, blank=True)
    score = models.IntegerField(help_text="The post score")
    view_count = models.PositiveIntegerField(help_text="The post view count", default=0)
    answer_count = models.PositiveIntegerField(help_text="The post answer count", default=0)
    comment_count = models.PositiveIntegerField(help_text="The post comment count", default=0)
    favorite_count = models.PositiveIntegerField(help_text="The post favorite count", default=0)
    content_license = models.CharField(
        help_text="The content license", max_length=max(len(cl.name) for cl in enums.ContentLicense),
        choices=[(cl.name, cl.value) for cl in enums.ContentLicense], default=enums.ContentLicense.CC_BY_SA_4_0.name)

    class Meta:
        db_table = 'posts'

    def __str__(self) -> str:
        """Return the string representation of the post.

        :return: The post title.
        """
        return str(self.title)


class Tag(models.Model):
    """The tag model
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, help_text="The site")
    name = models.CharField(help_text="The tag name", max_length=255)
    award_count = models.IntegerField(help_text="The tag award count")
    excerpt = models.ForeignKey(
        Post, help_text="The tag excerpt", on_delete=models.CASCADE, related_name='excerpts', null=True, blank=True)
    wiki = models.ForeignKey(
        Post, help_text="The tag wiki", on_delete=models.CASCADE, related_name='wikis', null=True, blank=True)
    required = models.BooleanField(help_text="True if the tag fulfills required tag constraints", default=False)
    moderator_only = models.BooleanField(help_text="True if the tag can only be used by moderators", default=False)

    class Meta:
        db_table = 'tags'
        unique_together = ('site', 'name')

    def __str__(self) -> str:
        """Return the string representation of the tag.

        :return: The tag name.
        """
        return str(self.name)
