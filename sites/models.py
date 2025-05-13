"""The application models
"""
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Site(TenantMixin):
    """The site model.
    """
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, help_text="The parent site")
    name = models.CharField(max_length=32, unique=True, help_text="The site name")
    description = models.CharField(max_length=64, help_text="The site description")
    long_description = models.CharField(max_length=128, help_text="The site long description")
    url = models.URLField(help_text="The site URL")
    image_url = models.URLField(help_text="The site image URL")
    icon_url = models.URLField(help_text="The site icon URL")
    badge_icon_url = models.URLField(help_text="The site badge icon URL")
    tag_css = models.TextField(help_text="CSS for tags")
    tagline = models.CharField(max_length=256, help_text="The site tagline")
    total_questions = models.PositiveIntegerField(default=0, help_text="The site total question count")
    total_answers = models.PositiveIntegerField(default=0, help_text="The site total answer count")
    total_users = models.PositiveIntegerField(default=0, help_text="The site total user count")
    total_comments = models.PositiveIntegerField(default=0, help_text="The site total comment count")
    total_tags = models.PositiveIntegerField(default=0, help_text="The site total tag count")
    last_post_date = models.DateTimeField(null=True, blank=True, help_text="The date of the last post")

    class Meta:
        db_table = 'sites'

    def __str__(self) -> str:
        """Return the string representation of the site.

        :return: The site name.
        """
        return str(self.name)


class Domain(DomainMixin):
    """The domain model.
    """
