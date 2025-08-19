from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('get-in-touch/', views.get_in_touch, name='get_in_touch'),
    path('cart/', views.cart, name='cart'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('our-story/', views.our_story, name='our_story'),
]