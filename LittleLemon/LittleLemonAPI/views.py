from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
from rest_framework import filters
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .models import Category, MenuItem, Order, OrderItem, Cart
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, UpdateDeliverCrewSerializer, UpdateStatusSerializer, CategorySerializer
from .permissions import CustomDjangoModelPermission

class OrderView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['total', 'date']
    filterset_fields = ['delivery_crew', 'status', 'date', 'total']

    
    def get_queryset(self):
        if self.request.user.groups.filter(name="Delivery crew").exists():
            return Order.objects.filter(delivery_crew = self.request.user)
        elif self.request.user.groups.filter(name="Manager").exists():
            return Order.objects.all()
        else:
            return Order.objects.filter(user=self.request.user)
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# class based views
class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        cart = self.get_queryset()
        [item.delete() for item in cart]
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
    permission_classes = [CustomDjangoModelPermission]

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


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['title', 'price', 'category']
    filterset_fields = ['title', 'price', 'category']


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]



# function based views
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def orders_list_detail(request, orderId):
    if request.method == 'GET':
        if not request.user.groups.filter(name="Delivery crew").exists() and not request.user.groups.filter(name="Manager").exists():
            order = get_object_or_404(Order, pk=orderId, user=request.user)
            order_items = OrderItem.objects.filter(order=order)
            serialized_order = OrderItemSerializer(order_items, many=True)
            return Response(serialized_order.data, status.HTTP_200_OK)
        else:
            return Response({'message': 'Only order owner can see all items'}, 403)
        
    elif request.method == 'DELETE':
        if request.user.groups.filter(name="Manager").exists():
            order = get_object_or_404(Order, pk=orderId)
            order.delete()
            return Response({'message': f"order {orderId} was deleted."})
        else:
            return Response({'message': 'You are NOT autorized. Only manager can delete an order.'}, 403)
        
    else:
        if request.user.groups.filter(name="Delivery crew").exists():
            order = get_object_or_404(Order, pk=orderId, delivery_crew=request.user)
            serialized_order = UpdateStatusSerializer(order, data=request.data, context = {'request': request})
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_200_OK)
    
        elif request.user.groups.filter(name="Manager").exists():
            order = get_object_or_404(Order, pk=orderId)
            serialized_order = UpdateDeliverCrewSerializer(order, data=request.data, context = {'request': request})
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_200_OK)
            
        else:
            return Response({'message': 'You are NOT autorized'}, 403)


# function based views, not in use
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def orders_list(request):
    orders = Order.objects.all()
    if request.method == 'GET':
        if request.user.groups.filter(name="Delivery crew").exists():
            orders = orders.filter(delivery_crew = request.user)
        elif request.user.groups.filter(name="Manager").exists():
            pass
        else:
            orders = orders.filter(user=request.user)

        delivery_crew = request.query_params.get('delivery_crew')
        status_order = request.query_params.get('status')
        date = request.query_params.get('date')
        total = request.query_params.get('total')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=3)
        page = request.query_params.get('page',  default=1)

        if delivery_crew:
            orders = orders.filter(delivery_crew__id=delivery_crew)
        if status_order:
            orders = orders.filter(status=status_order)    
        if date:
            orders = orders.filter(date=date)
        if total:
            orders = orders.filter(total__lte=total)
        if ordering:
            ordering_fields = ordering.split(",")
            orders = orders.order_by(*ordering_fields)

        paginator = Paginator(orders, per_page=perpage)
        try:
            orders = paginator.page(number=page)
        except EmptyPage:
            orders = []

        serialized_orders = OrderSerializer(orders, many=True)
        return Response(serialized_orders.data, status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serialized_order = OrderSerializer(data=request.data, context = {'request': request})
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save(user=request.user)
        return Response(serialized_order.data, status.HTTP_201_CREATED)
   


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_list(request):
    if request.method == 'GET':
        cart = Cart.objects.filter(user=request.user)
        serialized_cart = CartSerializer(cart, many=True)
        return Response(serialized_cart.data, status.HTTP_200_OK)
    elif request.method == 'POST':
        serialized_items = CartSerializer(data = request.data, context = {'request': request})
        serialized_items.is_valid(raise_exception=True)
        serialized_items.save()
        
        return Response(serialized_items.data, status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        cart = Cart.objects.filter(user=request.user)
        [item.delete() for item in cart]
        return Response({'message': "your cart is empty"})
        


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
        title = request.query_params.get('title')
        price = request.query_params.get('price')
        category = request.query_params.get('category')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=3)
        page = request.query_params.get('page',  default=1)

        if title:
            items = items.filter(title=title)
        if price:
            items = items.filter(price_lte=price)    
        if category:
            items = items.filter(category__title=category)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []

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




