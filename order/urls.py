from django.urls import path
from . import views
from .views import OrderUpdateView, OrderListView, HistoryOrderListView

urlpatterns=[
    path('register-photographer/', views.create_photographer, name='create_photographer'),
    path('photographers/', views.photographers_list, name='photographers_list'),
    path('photographer/profile/', views.photographer_profile, name='photographer_profile'),
    path('edit-photographer/', views.edit_photographer, name='edit_photographer'),
	path('reserve/<int:to_user_id>', views.create_order, name='order-create'),
    path('order', OrderListView.as_view(), name='order'),
    path('order/history', HistoryOrderListView.as_view(), name='order-history'),
    path('order/<int:pk>/update/', OrderUpdateView.as_view(), name='order-update'),
    path('order/<int:pk>/delete/', views.order_delete, name='order-delete'),
    path('order/<int:pk>/reject/', views.order_reject, name='order-reject'),
    path('order/<int:pk>/accept/', views.order_accept, name='order-accept'),
	path('order/<int:pk>/', views.order_detail, name='order-detail'),


]