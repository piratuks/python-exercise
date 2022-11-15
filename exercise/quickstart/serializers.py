from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager
from django.db.models import Q
from exercise.quickstart.models import Employee, MenuItem, RefMenu, Restaurant, Menu


User = get_user_model()


class PasswordChangeSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(
                'Current password does not match')
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:  # pylint: disable=too-few-public-methods
        model = User
        fields = (
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'username')

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if user:
            raise serializers.ValidationError("Email is already taken")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class UserLoginSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)


class AuthUserSerializer(serializers.ModelSerializer):
    auth_token = serializers.SerializerMethodField()

    class Meta:  # pylint: disable=too-few-public-methods
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'auth_token')
        read_only_fields = ('id', 'is_active', 'is_staff')

    def get_auth_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key


class EmptySerializer(serializers.Serializer):  # pylint: disable=abstract-method
    pass


class EmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True, max_length=255)
    email = serializers.EmailField(required=True, max_length=255)
    first_name = serializers.CharField(required=True, max_length=255)
    last_name = serializers.CharField(required=True, max_length=255)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Employee` instance, given the validated data.
        """
        return Employee.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Restaurant` instance, given the validated data.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.save()
        return instance

    def delete(self, instance):
        """
        Removes `Employee` instance.
        """
        return Employee.objects.delete(**instance)


class RestaurantSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    restaurantName = serializers.CharField(
        required=True, allow_blank=False, max_length=255)
    address = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255)
    city = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Restaurant` instance, given the validated data.
        """
        return Restaurant.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Restaurant` instance, given the validated data.
        """
        instance.restaurantName = validated_data.get(
            'restaurantName', instance.restaurantName)
        instance.address = validated_data.get('address', instance.address)
        instance.city = validated_data.get('city', instance.city)
        instance.save()
        return instance

    def delete(self, instance):
        """
        Removes `Restaurant` instance.
        """
        return Restaurant.objects.delete(**instance)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:  # pylint: disable=too-few-public-methods
        model = User
        fields = ['url', 'username', 'email', 'groups']


class RefSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.IntegerField(read_only=True)
    menuID = serializers.IntegerField(required=True, source="menuID_id")
    menuItemID = serializers.IntegerField(
        required=True, source="menuItemID_id")


class MenuItemSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    currency = serializers.CharField(max_length=10)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class MenuSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255)
    day = serializers.IntegerField(required=True)
    restaurant = RestaurantSerializer(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)
    menuItems = type(
        'SerializerMethodField',
        (serializers.SerializerMethodField,
         MenuItemSerializer),
        {})("get_menu_items")

    def get_menu_items(self, obj):
        queryset_ref_menu = RefMenu.objects.filter(menuID=obj.id).values()
        serializer = RefSerializer(queryset_ref_menu, many=True)
        my_filter_qs = Q()
        for creator in serializer.data:
            my_filter_qs = my_filter_qs | Q(id=creator["menuItemID"])

        if serializer.data.__len__() > 0:
            queryset_menu_item = MenuItem.objects.filter(my_filter_qs)
            serializer_menu_item = MenuItemSerializer(
                queryset_menu_item, many=True)
            return serializer_menu_item.data

        return []

    class Meta:  # pylint: disable=too-few-public-methods
        model = Menu
        fields = (
            'id',
            'name',
            'day',
            'created',
            'updated',
            'restaurant',
            'menuItems')


class VoteSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.IntegerField(read_only=True)
    count = serializers.IntegerField(required=True)
    day = serializers.IntegerField(required=True)
    menu = MenuSerializer(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)


class MenuItemRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    name = serializers.CharField(required=True, max_length=255)
    price = serializers.DecimalField(
        required=True, max_digits=6, decimal_places=2)
    currency = serializers.CharField(max_length=10)


class MenuRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    menuName = serializers.CharField(required=True, max_length=255)
    day = serializers.IntegerField(required=True)
    menuItems = MenuItemRequestSerializer(required=True, many=True)


class VotingSingleRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    menuName = serializers.CharField(required=True, max_length=255)
    day = serializers.IntegerField(required=True)
    votes = serializers.IntegerField(required=True)


class VotingManyRequestSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    data = VotingSingleRequestSerializer(many=True)
