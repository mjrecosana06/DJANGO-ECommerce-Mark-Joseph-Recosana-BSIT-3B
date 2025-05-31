from django.urls import path
from . import views

urlpatterns = [
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),  # ✅ ADD THIS
	path('register/', views.registerPage, name="register"),
	path('login/', views.loginPage, name="login"),
	path('logout/', views.logoutPage, name="logout"),
	path('my-orders/', views.my_orders, name='my_orders'),
	path('about/', views.about, name='about'),
	path('confirm-received/<int:order_id>/', views.confirm_order_received, name='confirm_order_received'),
]
