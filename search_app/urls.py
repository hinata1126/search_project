from django.urls import path 
from . import views 
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [ 
    path('', views.search_view, name='search_view'),
    path('search/', views.search_view, name='search_view'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete', views.product_delete, name='product_delete'),
    path('product/', views.product_list, name='product_list'), 
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    # path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),

    path('checkout/', views.checkout, name='checkout'),  #購入手続き
    path('order_complete/', views.order_complete, name='order_complete'),  #注文完了ページ
    path('order-history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)