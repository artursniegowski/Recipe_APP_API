"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    authenticate,
    get_user_model,
)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UserSeriazlier(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        # to create a user model we want to use own own menthod
        # called create_user for creating a user a making sure the password
        # gets encrypted as defined in our manager
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        # we are overiding this method bc we want to make sure that
        # when the user gets updated that we dont return the password as text
        # but as a hashed value
        # password is optional, the user dosent have to update the user
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        # bc when we use the browsable API we want the input to be hidden
        style={'input_type': 'password'},
        # so django will autmaticly trim the extra white space,
        # but we dont want that functionality
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """validate and authenticate the user"""
        # this method will be called by our view
        # getting the email and password from the post request
        email = attrs.get('email')
        password = attrs.get('password')
        # trying to authenticate the user with the given credentials
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password,
        )
        # if the authenticated user dosent exists wewill raise an error
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        # if the user was authneticated than we can pass the validted user
        # this will be used and expected by the view
        attrs['user'] = user
        return attrs
