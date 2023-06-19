"""
Urls mappings for the recipe app.
"""
from django.urls import (
    include,
    path,
)
from rest_framework.routers import DefaultRouter
from recipe import views


# this will generate the endpoints for recipes
# GET: recipes/
# POST: recipes/
# DELETE: recipes/{pk}/
# GET: recipes/{pk}/
# PUT: recipes/{pk}/
# PATCH: recipes/{pk}/
# DELETE: recipes/{pk}/
# list all enpoints - so basiacly emty endpoit will do  that
# /
router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    # ex: 'api/recipe/'
    path('', include(router.urls)),
]
