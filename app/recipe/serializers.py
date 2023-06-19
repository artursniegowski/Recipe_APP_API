"""
Serializers for reipe APIs
"""
from core.models import Recipe
from rest_framework import serializers


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        # all the fields we want to use with this serialzier
        fields = ['id',
                  'title',
                  'time_minutes',
                  #'description', # noqa
                  'price',
                  'link']
        read_only_fields = ['id']


# inheriting from the RecipeSerializer - using it as base
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    # inheriting from the RecipeSerializer.Meta - using it as base
    # and adding to th fields the description
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
