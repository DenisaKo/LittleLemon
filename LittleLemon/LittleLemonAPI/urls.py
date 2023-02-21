from django.urls import path
from . import views

urlpatterns = [

    # class-view base approach
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view()),
    path('groups/manager/users', views.ManagerView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerViewDetail.as_view()),
    path('groups/delivery-crew/users', views.DeliveryView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryViewDetail.as_view()),


    # function-view based approach
    # path('menu-items', views.menu_item_list),
    # path('menu-items/<int:pk>', views.menu_item_detail),
    path('groups/manager/users', views.manager_users),
    path('groups/manager/users/<int:userId>', views.manager_users_detail),
    path('groups/delivery-crew/users', views.delivery_users),
    path('groups/delivery-crew/users/<int:userId>', views.delivery_users_detail),

    
]