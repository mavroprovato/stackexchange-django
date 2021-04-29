from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

from stackexchange import filters, models, serializers


@extend_schema_view(
    list=extend_schema(summary='Get all comments on the site'),
    retrieve=extend_schema(summary='Gets the comment identified by id'),
)
class CommentViewSet(viewsets.ReadOnlyModelViewSet):
    """The answers view set
    """
    queryset = models.Comment.objects.select_related('post', 'user')
    serializer_class = serializers.CommentSerializer
    filter_backends = (filters.OrderingFilter, )

    @staticmethod
    def get_ordering_fields():
        """Return the ordering fields for the action.

        :return: The ordering fields for the action.
        """
        return ('creation', 'desc', 'creation_date'), ('votes', 'desc', 'score')
