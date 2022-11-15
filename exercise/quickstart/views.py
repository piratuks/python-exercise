from rest_framework import permissions, authentication, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, logout
from exercise.quickstart.serializers import EmployeeSerializer, MenuSerializer, \
    MenuRequestSerializer, RestaurantSerializer, EmptySerializer, \
    UserLoginSerializer, UserRegisterSerializer, AuthUserSerializer, \
    PasswordChangeSerializer, UserSerializer, VoteSerializer, VotingManyRequestSerializer, \
    VotingSingleRequestSerializer
from exercise.quickstart.models import Employee, MenuItem, RefMenu, Restaurant, Menu, Vote
from .utils import get_and_authenticate_user, create_user_account


User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = EmptySerializer
    serializer_classes = {
        'login': UserLoginSerializer,
        'register': UserRegisterSerializer,
        'password_change': PasswordChangeSerializer,
    }

    @action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)

        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST', ], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(methods=['POST', ], detail=False,
            permission_classes=[permissions.IsAuthenticated, ])
    def logout(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        logout(request)
        data = {'success': 'Sucessfully logged out'}
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False,
            permission_classes=[permissions.IsAuthenticated, ])
    def password_change(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured(
                'serializer_classes should be a dict mapping.')

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows employees to be viewed or edited.
    """
    queryset = Employee.objects.all().order_by('-username')
    serializer_class = EmployeeSerializer
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, data_id=None):  # pylint: disable=arguments-differ
        item = get_object_or_404(self.queryset, pk=data_id)
        serializer = EmployeeSerializer(item)
        return Response(serializer.data)


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows restaurants to be viewed or edited.
    """
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    serializer_classes = {
        'menu': MenuSerializer,
        'vote': {
            'v1.0': VotingSingleRequestSerializer,
            'v2.0': VotingManyRequestSerializer,
        },
    }
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured(
                'serializer_classes should be a dict mapping.')

        if self.action in self.serializer_classes.keys():
            if self.action == 'vote':
                if self.request.version == 'v2.0':
                    return self.serializer_classes[self.action]['v2.0']
                elif self.request.version == 'v1.0':
                    return self.serializer_classes[self.action]['v1.0']
                else:
                    return self.serializer_classes[self.action]['v1.0']
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    def vote_singular(self, request_data, data_id=None):
        existing_vote_serializer = VotingSingleRequestSerializer(
            data=request_data)
        if not existing_vote_serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        menu = Menu.objects.filter(
            restaurant_id=data_id,
            name=existing_vote_serializer.data['menuName'],
            day=existing_vote_serializer.data['day'])
        if menu.__len__() > 0:
            obj_menu = Menu.objects.get(
                restaurant_id=data_id,
                name=existing_vote_serializer.data['menuName'],
                day=existing_vote_serializer.data['day'])
            vote_object = Vote.objects.filter(
                menu_id=obj_menu.id, day=existing_vote_serializer.data['day'])
            if vote_object.__len__() > 0:
                obj_vote = Vote.objects.get(
                    menu_id=obj_menu.id, day=existing_vote_serializer.data['day'])
                obj_vote.count = existing_vote_serializer.data['votes']
                obj_vote.save()
            else:
                Vote.objects.create(
                    count=existing_vote_serializer.data['votes'],
                    day=existing_vote_serializer.data['day'],
                    menu_id=obj_menu.id
                )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'error': 'Menu with provided name and day have not been found'})

        return Response(
            status=status.HTTP_200_OK, data={
                'error': 'Only top three menu items are accepted for voting'})

    @action(methods=['POST', ], detail=True,
            permission_classes=[permissions.IsAuthenticated, ])
    def vote(self, request, data_id=None):
        if request.version == 'v2.0':
            existing_vote_serializer = VotingManyRequestSerializer(
                data=request.data)
            if not existing_vote_serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if (existing_vote_serializer.data.__len__() >
                    3 or existing_vote_serializer.data.__len__() < 1):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST, data={
                        'error': 'Only top three menu items are accepted for voting'})

            for item in existing_vote_serializer.data['data']:
                response = self.vote_singular(item, data_id)
                if request.data is not None:
                    break
            return response
        elif request.version == 'v1.0':
            return self.vote_singular(request.data, data_id)
        else:
            return self.vote_singular(request.data, data_id)

    @action(methods=['GET',
                     ],
            url_path='current',
            detail=True,
            permission_classes=[permissions.IsAuthenticated,
                                ],
            serializer_class=MenuSerializer)
    def menus_current_day(self, request, data_id=None):  # pylint: disable=unused-argument
        day = timezone.now().weekday() + 1
        menu = Menu.objects.filter(restaurant_id=data_id, day=day)
        data = []
        if menu.__len__() > 0:
            data = MenuSerializer(menu, many=True).data
        return Response(data=data, status=status.HTTP_200_OK,)

    @action(methods=['GET',
                     ],
            url_path='current',
            detail=False,
            permission_classes=[permissions.IsAuthenticated,
                                ],
            serializer_class=VoteSerializer)
    def votes(self, request):  # pylint: disable=unused-argument
        day = timezone.now().weekday() + 1
        vote_object = Vote.objects.filter(day=day)
        data = []
        if vote_object.__len__() > 0:
            data = VoteSerializer(vote_object, many=True).data
        return Response(data=data, status=status.HTTP_200_OK,)

    @action(methods=['GET',
                     ],
            detail=True,
            permission_classes=[permissions.IsAuthenticated,
                                ],
            serializer_class=MenuSerializer)
    def menus(self, request, data_id=None):  # pylint: disable=unused-argument
        menu = Menu.objects.filter(restaurant_id=data_id)
        data = []
        if menu.__len__() > 0:
            data = MenuSerializer(menu, many=True).data
        return Response(data=data, status=status.HTTP_200_OK,)

    @action(methods=['POST',
                     ],
            detail=True,
            permission_classes=[permissions.IsAuthenticated,
                                ],
            serializer_class=MenuRequestSerializer)
    def menu(self, request, data_id=None):
        data = request.data

        if (data['day'] < 1 or data['day'] > 7):
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={
                    'error': 'Days are from 1 to 7 (from Monday to Sunday)'})

        existing_menu = Menu.objects.filter(
            day=data['day'], restaurant_id=data_id)
        if existing_menu.__len__() > 0:
            obj_menu = Menu.objects.get(day=data['day'], restaurant_id=data_id)
            obj_menu.name = data['menuName']
            obj_menu.save()
        else:
            obj_menu = Menu.objects.create(
                name=data['menuName'],
                day=data['day'],
                restaurant_id=data_id
            )

        for item in data['menuItems']:
            existing_menu_item = MenuItem.objects.filter(
                name=item['name'], price=item['price'], currency=item['currency'])
            if existing_menu_item.__len__() == 0:
                obj_menu_item = MenuItem.objects.create(
                    name=item['name'],
                    price=item['price'],
                    currency=item['currency']
                )
            else:
                obj_menu_item = MenuItem.objects.get(
                    name=item['name'], price=item['price'], currency=item['currency'])
            existing_ref_menu = RefMenu.objects.filter(
                menuID=obj_menu.id, menuItemID=obj_menu_item.id)
            if existing_ref_menu.__len__() == 0:
                RefMenu.objects.create(
                    menuID=obj_menu,
                    menuItemID=obj_menu_item,
                )

        return Response(status=status.HTTP_201_CREATED)

    def retrieve(self, request, data_id=None):  # pylint: disable=arguments-differ
        item = get_object_or_404(self.queryset, pk=data_id)
        serializer = RestaurantSerializer(item)
        return Response(serializer.data)
