from django.contrib.auth.models import User, Group

from rest_framework import serializers
from rest_framework.response import Response

from .models import Category, MenuItem, Order, OrderItem, Cart

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class UserSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField(method_name='get_group')
    # groups = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'group']

    def get_group(self, product = User):
        try:
            return Group.objects.filter(user=product)[0].name
        except:
            return "Not in a group"
        
           