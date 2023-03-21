from django.urls import path
from . import views

urlpatterns = [

    # class-view base approach
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view()),
    path('category', views.CategoryView.as_view()),
    path('category/<int:pk>', views.CategoryDetail.as_view()),
    path('groups/manager/users', views.ManagerView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerViewDetail.as_view()),
    path('groups/delivery-crew/users', views.DeliveryView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryViewDetail.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.OrderDerailView.as_view()),


    # function-view based approach
    # path('menu-items', views.menu_item_list),
    # path('menu-items/<int:pk>', views.menu_item_detail),
    # path('groups/manager/users', views.manager_users),
    # path('groups/manager/users/<int:userId>', views.manager_users_detail),
    # path('groups/delivery-crew/users', views.delivery_users),
    # path('groups/delivery-crew/users/<int:userId>', views.delivery_users_detail),
    # path('cart/menu-items', views.cart_list),
    # path('orders', views.orders_list),
    # path('orders/<int:orderId>', views.orders_list_detail),
    

    
]