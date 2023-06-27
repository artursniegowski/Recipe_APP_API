"""
Views for the recipe APIs.
"""
from core.models import Ingredient, Recipe, Tag
from rest_framework import (
    authentication,
    mixins,
    permissions,
    viewsets,
    )
from recipe.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APis."""

    serializer_class = RecipeDetailSerializer
    # this is not necessary since the model is already defined in
    # the serializer !
    # query set of object managable through this API
    queryset = Recipe.objects.all()
    # the only accepted authetication will be with token
    authentication_classes = [authentication.TokenAuthentication]
    # requires the user to be authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrive recipes for authenticated user."""
        # making sure the autheticatedd user gets only the recipes
        # that are connected to that user and no other recipes
        current_user = self.request.user
        return Recipe.objects.filter(user=current_user).order_by('-id')

    # this will be used to change the serializer for a detail view
    # so there will be a different serializer for list view, adn detail view
    def get_serializer_class(self):
        """Return the serializer class for the request."""
        # so if the action is list (get on main endpoint) -
        # listing all elements
        # the serializer will be change to the
        # RecipeSerializer which is more general, and for any other action
        # the default serializer will be used which is
        # the RecipeDetailSerializer
        if self.action == 'list':
            return RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe with the current user from the request."""
        # we overide this method to save the current user from the request
        # to the recipe, to make sure that this user is asociated with the
        # recipe we are saving
        serializer.save(user=self.request.user)


# creating one class taht canbe  used as based
# so other can simply inherit from it
class BaseRecipeAttrViewSet(
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet
                            ):
    """Base viewset for recipe atributes."""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        # only tot he user in the request which has to be uathneticated
        # by token
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
