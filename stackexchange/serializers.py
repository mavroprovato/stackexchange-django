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
    rank = fields.SerializerMethodField()
    badge_id = fields.IntegerField(source='pk')

    class Meta:
        model = models.Badge
        fields = ('badge_type', 'rank', 'badge_id', 'name')

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
    bronze = fields.SerializerMethodField()
    silver = fields.SerializerMethodField()
    gold = fields.SerializerMethodField()

    @staticmethod
    def get_bronze(user_badges: QuerySet) -> int:
        """Get the number of bronze badges for a user.

        :param user_badges: The user badges.
        :return: The number of bronze badges.
        """
        return BadgeCountSerializer.count_badges(user_badges, models.Badge.CLASS_BRONZE)

    @staticmethod
    def get_silver(user_badges: QuerySet) -> int:
        """Get the number of silver badges for a user.

        :param user_badges: The user badges.
        :return: The number of silver badges.
        """
        return BadgeCountSerializer.count_badges(user_badges, models.Badge.CLASS_SILVER)

    @staticmethod
    def get_gold(user_badges: QuerySet) -> int:
        """Get the number of gold badges for a user.

        :param user_badges: The gold badges.
        :return: The number of gold badges.
        """
        return BadgeCountSerializer.count_badges(user_badges, models.Badge.CLASS_SILVER)

    @staticmethod
    def count_badges(user_badges: QuerySet, badge_class: str) -> int:
        """Count the user badges for a class.

        :param user_badges: The user badges.
        :param badge_class: The badge class.
        :return: The number of badges for the class.
        """
        count = 0
        for user_badge in user_badges.all():
            if user_badge.badge.badge_class == badge_class:
                count += 1

        return count


class BaseUserSerializer(serializers.ModelSerializer):
    """The base user serializer.
    """
    user_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.User
        fields = ('reputation', 'user_id', 'display_name')


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


class UserSerializer(serializers.ModelSerializer):
    """The user serializer.
    """
    badge_counts = BadgeCountSerializer(source="badges")
    user_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.User
        fields = (
            'badge_counts', 'is_employee', 'reputation', 'creation_date', 'user_id', 'location', 'website_url',
            'display_name'
        )


class TagSerializer(serializers.ModelSerializer):
    """The tag serializer
    """
    class Meta:
        model = models.Tag
        fields = ('name', 'count')


class PostSerializer(serializers.ModelSerializer):
    """The post serializer
    """
    owner = BaseUserSerializer()
    post_type = fields.SerializerMethodField()
    post_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'last_activity_date', 'creation_date', 'post_type', 'post_id')

    @staticmethod
    def get_post_type(post: models.Post) -> typing.Optional[str]:
        """Get the post type

        :param post: The post.
        :return: The post type.
        """
        for choice in models.Post.TYPE_CHOICES:
            if choice[0] == post.type:
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
            'tags', 'owner', 'is_answered', 'view_count', 'answer_count', 'score', 'last_activity_date',
            'creation_date', 'last_edit_date', 'question_id', 'title'
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
    answer_id = fields.IntegerField(source="pk")

    class Meta:
        model = models.Post
        fields = ('owner', 'score', 'last_activity_date', 'creation_date', 'answer_id')
