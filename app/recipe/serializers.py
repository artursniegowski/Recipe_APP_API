"""
Serializers for reipe APIs
"""
from core.models import Recipe, Tag, Ingredient
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients"""
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        # TODO: i think id is not needed here as the model
        # should enforce that, therfore the serializer should
        # enforce this at the id automaticly
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        # TODO: i think id is not needed here as the model
        # should enforce that, therfore the serializer should
        # enforce this at the id automaticly
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    # adding the tags, many = True indicates this will be list
    # required = False - just indicating this will not be arequired filed
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # all the fields we want to use with this serialzier
        fields = ['id',
                  'title',
                  'time_minutes',
                  #'description', # noqa
                  'price',
                  'link',
                  'tags',
                  'ingredients',
                  ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags_data, recipe):
        """Handling getting or creating tags as needed."""
        # the user field is expected to be present in the validated_data
        # since it is a required field
        # oterwise we could get the user from the request as so
        # auth_user = self.context['request'].user
        # the upper would be required if we wouldent
        # pass the user in the valid_data
        for tag_data in tags_data:
            # creating or getting a tag if it already exists
            tag, _ = Tag.objects.get_or_create(user=recipe.user, **tag_data)
            # adding the tag to the recipe
            recipe.tags.add(tag)

    def _get_or_create_ingredients(self, ingredients_data, recipe):
        """Handle getting or creatingingredients as needed."""
        # the user field is expected to be present in the validated_data
        # since it is a required field
        # oterwise we could get the user from the request as so
        # auth_user = self.context['request'].user
        # the upper would be required if we wouldent
        # pass the user in the valid_data
        for ingredient_data in ingredients_data:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=recipe.user,
                **ingredient_data)
            recipe.ingredients.add(ingredient_obj)

    # we have to add this method bc nested serializers are read only by default
    # so here we will add the functionality that they can be writable
    def create(self, validated_data):
        """Create a recipe."""
        # getting the tags data first, and removing it from the validated data
        tags_data = validated_data.pop('tags', [])
        # getting the ingredients data first, and removing it
        # from the validated data
        ingredients_data = validated_data.pop('ingredients', [])

        # creating a recipe
        recipe = Recipe.objects.create(**validated_data)
        # the user field is expected to be present in the validated_data
        # since it is a required field
        # oterwise we could get the user from the request as so
        # auth_user = self.context['request'].user
        # the upper would be required if we wouldent
        # pass the user in the valid_data
        self._get_or_create_tags(tags_data, recipe)
        # this way all the ingredient will get added or will be created
        self._get_or_create_ingredients(ingredients_data, recipe)

        return recipe

    # creating the update functionality for the serializer
    def update(self, instance, validated_data):
        """Update recipe."""
        # getting the tags data first, and removing it from the validated data
        tags_data = validated_data.pop('tags', None)
        # getting the ingredients data first, and removing it from the
        # validated data
        ingredients_data = validated_data.pop('ingredients', None)

        if tags_data is not None:
            # clearing all the existing tags first
            # if we are supose to update them
            instance.tags.clear()
            self._get_or_create_tags(tags_data, instance)

        if ingredients_data is not None:
            # clearing all the existing ingredients first
            # if we are supose to update them
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients_data, instance)

        # basiacly evrerything except the tags we will asign to our
        # recipe, as it comes in the validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # saving the updated instace
        instance.save()

        return instance


# inheriting from the RecipeSerializer - using it as base
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    # inheriting from the RecipeSerializer.Meta - using it as base
    # and adding to th fields the description
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
