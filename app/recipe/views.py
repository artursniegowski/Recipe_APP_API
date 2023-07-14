"""
Views for the recipe APIs.
"""
from core.models import Ingredient, Recipe, Tag
from rest_framework import (
    authentication,
    mixins,
    permissions,
    status,
    viewsets,
    )
from rest_framework.decorators import action
from rest_framework.response import Response
from recipe.serializers import (
    IngredientSerializer,
    RecipeDetailSerializer,
    RecipeImageSerializer,
    RecipeSerializer,
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
        # upload image will be a custom action that will be defined as a
        # different method in our view Set, actions are basically ways that you
        # can add additional functionality on top of the viewSet default
        # funcionality that is created
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe with the current user from the request."""
        # we overide this method to save the current user from the request
        # to the recipe, to make sure that this user is asociated with the
        # recipe we are saving
        serializer.save(user=self.request.user)

    # creating the custom action
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
