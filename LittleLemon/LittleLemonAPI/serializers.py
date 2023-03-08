from django.contrib.auth.models import User, Group
from django.shortcuts import get_list_or_404, get_object_or_404

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

import bleach

from .models import Category, MenuItem, Order, OrderItem, Cart


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class MenuItemSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if(attrs['price']<0):
            raise serializers.ValidationError('Price must be greater than 0')
        (bleach.clean(value) for value in attrs)
        return super().validate(attrs)
        
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class UserSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField(method_name='get_group')
    
    class Meta:
        model = User
        fields = ['id', 'username', 'group']

    def get_group(self, product = User):
        try:
            return Group.objects.filter(user=product)[0].name
        except:
            return "Not in a group"
        
class CartSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_name = serializers.CharField(source = 'user.username', read_only=True)
    menuitem_name = serializers.CharField(source = 'menuitem.title', read_only=True)

    def validate(self, attrs):
        if(attrs['quantity']<0):
            raise serializers.ValidationError('Price must be greater than 0')
        (bleach.clean(value) for value in attrs)
        return super().validate(attrs)
   
    class Meta:
        model = Cart
        fields = ['user', 'user_name', 'menuitem', 'menuitem_name', 'quantity', 'unit_price', 'price']
        validators = [
                UniqueTogetherValidator(
                    queryset = Cart.objects.all(),
                    fields= ['menuitem', 'user']
                )
            ]


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only='True')
    delivery_crew = serializers.PrimaryKeyRelatedField(read_only='True')
    status = serializers.BooleanField(read_only=True)
    total = serializers.DecimalField(decimal_places=2, max_digits=6,  read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']


    def create(self, validated_data):
        user = validated_data['user']
        cart_items = get_list_or_404(Cart, user=user)
        total = sum(cart_item.price for cart_item in cart_items)
        order = Order.objects.create(user=user, total=total)

        [OrderItem.objects.create(
            order = order,
            menuitem = cart_item.menuitem,
            quantity = cart_item.quantity,
            unit_price = cart_item.unit_price,
            price = cart_item.price
            ) for cart_item in cart_items]
        
        [cart_item.delete() for cart_item in cart_items]
        return order


class UpdateDeliverCrewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only='True')
    delivery_crew = serializers.PrimaryKeyRelatedField(read_only='True')
    delivery_crew_id = serializers.IntegerField(write_only='True')

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'delivery_crew_id', 'status', 'total', 'date']

    def validate_delivery_crew_id(self, value):
        if not User.objects.filter(pk=value, groups__name__in=['Delivery crew']):
            raise serializers.ValidationError('this user doest not exist in delivery crew')
        return value


class UpdateStatusSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only='True')
    status_change = serializers.BooleanField(source='status', write_only=True, required=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'status_change', 'total', 'date']

    def validate_status_change(self, value):
        if value not in [True, False]:
            raise serializers.ValidationError('Value has to be a bool value')
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only='True')
    menuitem = serializers.PrimaryKeyRelatedField(read_only='True')
    menuitem_name = serializers.CharField(source='menuitem.title', read_only=True)
    quantity = serializers.IntegerField( read_only=True)
    unit_price = serializers.DecimalField(decimal_places=2, max_digits=6,  read_only=True)
    price = serializers.DecimalField(decimal_places=2, max_digits=6,  read_only=True)
   

    class Meta:
        model = Order
        fields = ['order', 'menuitem', 'menuitem_name', 'quantity', 'unit_price', 'price']
        validators = [
                UniqueTogetherValidator(
                    queryset = Cart.objects.all(),
                    fields= ['order', 'menuitem']
                )
            ]
