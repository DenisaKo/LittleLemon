from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response

from .models import Category, MenuItem, Order, OrderItem, Cart
from .serializers import MenuItemSerializer, UserSerializer

# class based views
class DeliveryView(generics.ListAPIView, generics.CreateAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions, IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Delivery crew')
            managers.user_set.add(user)
            serialized_user = UserSerializer(user)
            return Response(serialized_user.data, status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User does NOT exist'}, 400)


class DeliveryViewDetail(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        managers = Group.objects.get(name='Delivery crew')
        managers.user_set.remove(user)
        serialized_user = UserSerializer(user)
        return Response(serialized_user.data, status.HTTP_200_OK)


class ManagerView(generics.ListAPIView, generics.CreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions, IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            serialized_user = UserSerializer(user)
            return Response(serialized_user.data, status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User does NOT exist'}, 400)


class ManagerViewDetail(generics.RetrieveDestroyAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        serialized_user = UserSerializer(user)
        return Response(serialized_user.data, status.HTTP_200_OK)


# class-view based approach
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]



# function based views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def delivery_users(request):
    if request.user.groups.filter(name='Manager').exists():
        if request.method == "GET":
            users = User.objects.filter(groups__name='Delivery crew')
            serialized_users = UserSerializer(users, many = True)
            return Response(serialized_users.data, status.HTTP_200_OK)
        elif request.method == 'POST':
                username = request.data['username']
                if username:
                    user = get_object_or_404(User, username=username)
                    managers = Group.objects.get(name='Delivery crew')
                    managers.user_set.add(user)
                    serialized_user = UserSerializer(user)
                    return Response(serialized_user.data, status.HTTP_201_CREATED)
                else:
                    return Response({'message': 'User does NOT exist'}, 400)
    else:
        return Response({'message': 'You are NOT autorized'}, 403)



@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def delivery_users_detail(request, userId):
    if request.user.groups.filter(name='Manager').exists():
        user = get_object_or_404(User.objects.filter(groups__name='Delivery crew'), pk=userId)
        if request.method == "GET":
            serializered_item = UserSerializer(user)
            return Response(serializered_item.data)
        elif request.method == 'DELETE':
            managers = Group.objects.get(name='Delivery crew')
            managers.user_set.remove(user)
            serialized_user = UserSerializer(user)
            return Response(serialized_user.data, status.HTTP_200_OK)
    else:
        return Response({'message': 'You are NOT autorized'}, 403)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manager_users(request):
    if request.user.groups.filter(name='Manager').exists():
        if request.method == "GET":
            users = User.objects.filter(groups__name='Manager')
            serialized_users = UserSerializer(users, many = True)
            return Response(serialized_users.data, status.HTTP_200_OK)
        elif request.method == 'POST':
                username = request.data['username']
                if username:
                    user = get_object_or_404(User, username=username)
                    managers = Group.objects.get(name='Manager')
                    managers.user_set.add(user)
                    serialized_user = UserSerializer(user)
                    return Response(serialized_user.data, status.HTTP_201_CREATED)
                else:
                    return Response({'message': 'User does NOT exist'}, 400)
    else:
        return Response({'message': 'You are NOT autorized'}, 403)



@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def manager_users_detail(request, userId):
    if request.user.groups.filter(name='Manager').exists():
        user = get_object_or_404(User.objects.filter(groups__name='Manager'), pk=userId)
        if request.method == "GET":
            serializered_item = UserSerializer(user)
            return Response(serializered_item.data)
        elif request.method == 'DELETE':
            managers = Group.objects.get(name='Manager')
            managers.user_set.remove(user)
            serialized_user = UserSerializer(user)
            return Response(serialized_user.data, status.HTTP_200_OK)
    else:
        return Response({'message': 'You are NOT autorized'}, 403)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_item_list(request):
    if request.method == "GET":
        items = MenuItem.objects.all()
        serialized_items = MenuItemSerializer(items, many = True)
        return Response(serialized_items.data, status.HTTP_200_OK)
    elif request.method == 'POST':
        if request.user.groups.filter(name="Manager").exists():
            serialized_items = MenuItemSerializer(data = request.data)
            serialized_items.is_valid(raise_exception=True)
            serialized_items.save()
            return Response(serialized_items.data, status.HTTP_201_CREATED)
        else:
            return Response({'message': 'You are NOT autorized'}, 403)
        
     

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item_detail(request, pk):
    item = get_object_or_404(MenuItem, pk=pk)
    if request.method == "GET":
        serializered_item = MenuItemSerializer(item)
        return Response(serializered_item.data)
    else:
        if request.user.groups.filter(name="Manager").exists():
            if request.method == "DELETE":
                item.delete()
                msg = f'Item {item.title} deleted'
                return Response({"message": msg})
            else:
                new_data = request.data
                for key, value in new_data.items():
                    setattr(item, key, value)
                item.save()
                serialized_item = MenuItemSerializer(item)
                return Response(serialized_item.data)
        else:
            return Response({'message': 'You are NOT autorized'}, 403)




