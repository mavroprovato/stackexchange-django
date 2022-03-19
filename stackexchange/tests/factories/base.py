"""Base classes for model factories
"""
import factory


class BaseModelFactory(factory.django.DjangoModelFactory):
    """Base class for model factory.
    """
    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        creation_date = kwargs.pop('creation_date', None)
        obj = super()._create(target_class, *args, **kwargs)
        if creation_date is not None:
            obj.creation_date = creation_date
            obj.save()

        return obj
