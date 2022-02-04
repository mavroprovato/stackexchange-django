"""The application serializers
"""
import typing

from django.db.models import QuerySet
from rest_framework import fields, serializers

from stackexchange import models


class BaseSerializer(serializers.Serializer):
    """Base class for serializers
    """
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class BadgeSerializer(serializers.ModelSerializer):
    """The badge serializer
    """
    badge_type = fields.SerializerMethodField()
    award_count = fields.IntegerField()
    rank = fields.SerializerMethodField()
    badge_id = fields.IntegerField(source='pk')

    class Meta:
        model = models.Badge
        fields = ('badge_type', 'award_count', 'rank', 'badge_id', 'name')

    @staticmethod
    def get_badge_type(badge: models.Badge) -> str:
        """Get the badge type.

        :param badge: The badges.
        :return: The badge type.
        """
        return "tag_based" if badge.tag_based else "named"

    @staticmethod
    def get_rank(badge: models.Badge) -> str:
        """Get the badge rank.

        :param badge: The badges.
        :return: The badge type.
        """
        for class_id, class_description in models.Badge.CLASS_CHOICES:
            if badge.badge_class == class_id:
                return class_description


class BadgeCountSerializer(BaseSerializer):
    """The badge count serializer.
    """
    def get_fields(self) -> dict:
        """Return the fields for the serializer. Returns one field for each field class.

        :return: The fields for the serializer.
        """
        serializer_fields = super().get_fields()
        for _, field_name in models.Badge.CLASS_CHOICES:
            serializer_fields[field_name] = fields.IntegerField(source=f"{field_name}_count")

        return serializer_fields


class BaseUserSerializer(serializers.ModelSerializer):
    """The base user serializer.
    """
    user_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.User
        fields = ('reputation', 'user_id', 'display_name')


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badge_counts = BadgeCountSerializer(source="*")
    user_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.User
        fields = (
            'badge_counts', 'is_employee', 'reputation', 'creation_date', 'user_id', 'location', 'website_url',
            'display_name'
        )


class UserBadgeSerializer(serializers.ModelSerializer):
    """The user badge serializer
    """
    user = BaseUserSerializer()
    name = fields.CharField(source='badge.name')
    badge_type = fields.SerializerMethodField(source='badge.badge_type')
    rank = fields.SerializerMethodField(source='badge.rank')
    badge_id = fields.IntegerField(source='pk')

    class Meta:
        model = models.UserBadge
        fields = ('user', 'badge_type', 'rank', 'badge_id', 'name')

    @staticmethod
    def get_badge_type(user_badge: models.UserBadge) -> str:
        """Get the user badge type.

        :param user_badge: The badges.
        :return: The badge type.
        """
        return "tag_based" if user_badge.badge.tag_based else "named"

    @staticmethod
    def get_rank(user_badge: models.UserBadge) -> str:
        """Get the user badge rank.

        :param user_badge: The badges.
        :return: The badge type.
        """
        for class_id, class_description in models.Badge.CLASS_CHOICES:
            if user_badge.badge.badge_class == class_id:
                return class_description


class TagSerializer(serializers.ModelSerializer):
    """The tag serializer
    """
    class Meta:
        model = models.Tag
        fields = ('count', 'name')


class TagWikiSerializer(serializers.ModelSerializer):
    """The tag wiki serializer
    """
    excerpt_last_edit_date = fields.DateTimeField(source='excerpt.last_edit_date', default=None)
    body_last_edit_date = fields.DateTimeField(source='wiki.last_edit_date', default=None)
    excerpt = fields.CharField(source='excerpt.body', default=None)
    tag_name = fields.CharField(source='name')

    class Meta:
        model = models.Tag
        fields = ('excerpt_last_edit_date', 'body_last_edit_date', 'excerpt', 'tag_name')


class PostSerializer(serializers.ModelSerializer):
    """The post serializer
    """
    owner = BaseUserSerializer()
    post_type = fields.SerializerMethodField()
    post_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'last_activity_date', 'creation_date', 'post_type', 'post_id', 'content_license')

    @staticmethod
    def get_post_type(post: models.Post) -> typing.Optional[str]:
        """Get the post type

        :param post: The post.
        :return: The post type.
        """
        for choice in models.Post.TYPE_CHOICES:
            if choice[0] == post.type:
                return choice[1]


class PostHistorySerializer(serializers.ModelSerializer):
    """The post history serializer
    """
    user = BaseUserSerializer()
    post_type = fields.SerializerMethodField()

    class Meta:
        model = models.PostHistory
        fields = ('user', 'creation_date', 'post_id', 'post_type', 'content_license', 'comment', 'revision_guid')

    @staticmethod
    def get_post_type(post_history: models.PostHistory) -> typing.Optional[str]:
        """Get the post type

        :param post_history: The post history.
        :return: The post type.
        """
        for choice in models.Post.TYPE_CHOICES:
            if choice[0] == post_history.post.type:
                return choice[1]


class QuestionSerializer(PostSerializer):
    """The question serializer
    """
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    is_answered = fields.SerializerMethodField()
    question_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = (
            'tags', 'owner', 'is_answered', 'view_count', 'accepted_answer_id', 'answer_count', 'score',
            'last_activity_date', 'creation_date', 'last_edit_date', 'question_id', 'content_license', 'title'
        )

    @staticmethod
    def get_is_answered(post: models.Post) -> bool:
        """Get weather this question is answered.

        :param post: The post.
        :return: True if the question is answered.
        """
        return post.answer_count and post.answer_count > 1


class AnswerSerializer(PostSerializer):
    """The answer serializer
    """
    is_accepted = fields.SerializerMethodField()
    answer_id = fields.IntegerField(source="pk")
    question_id = fields.IntegerField(source="parent.pk")

    class Meta:
        model = models.Post
        fields = (
            'owner', 'is_accepted', 'score', 'last_activity_date', 'creation_date', 'answer_id', 'question_id',
            'content_license'
        )

    @staticmethod
    def get_is_accepted(post: models.Post) -> bool:
        """Get weather this answer is accepted.

        :param post: The post.
        :return: True if the answer is accepted.
        """
        return bool(post.accepted_answer_id)


class CommentSerializer(PostSerializer):
    """The comment serializer
    """
    owner = BaseUserSerializer(source="user")
    comment_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'creation_date', 'post_id', 'comment_id', 'content_license')
