"""Base classes for model factories
"""
import factory


class BaseModelFactory(factory.django.DjangoModelFactory):
    """Base class for model factory.
    """
    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        creation_date = kwargs.pop('creation_date', None)
        last_modified_date = kwargs.pop('last_modified_date', None)
        obj = super()._create(target_class, *args, **kwargs)
        if creation_date is not None:
            obj.creation_date = creation_date
        if last_modified_date is not None:
            obj.last_modified_date = last_modified_date

        return obj
