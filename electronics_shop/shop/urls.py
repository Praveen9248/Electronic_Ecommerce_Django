from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name="home_page"),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('contact/',views.contact,name="contact_page"),
    path('about/',views.about,name="about_page"),

    path('search/',views.search_filters,name="search_page"),
    
    path('shop/',views.shop,name="shop_page"),
    path('shop/<slug:slug>/',views.shop_detail,name="shop_detail_page"),

    path('cart/',views.cart,name="cart_page"),
    path('add_to_cart/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart_item/', views.update_cart_item, name='update_cart_item'),
    path('remove_cart_item/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),

    path("paypal",include("paypal.standard.ipn.urls")),
    path('billing/<int:order_id>/', views.billing, name='billing'),
    path('paypal-ipn/', views.paypal_ipn_listener, name='paypal-ipn'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment-success'),
    path('payment-failed/<int:order_id>/', views.payment_failed, name='payment-failed'),

    path('technician/', views.technician_view, name='technician_page'),
    path('technician/<int:request_id>/', views.task_detail, name='task_detail_page'),
    path('technician/reports/', views.completed_requests_view, name='completed_reports'),
    path('technician/dashboard/', views.technician_dashboard, name='technician_dashboard'),

    path('services/', views.services, name='service_page'),
    path('add_service_request/', views.add_service_request, name='add_service_request'),
    path('add_repair_product/', views.add_repair_product, name='add_repair_product'),
    path('status/', views.contact, name='service_status_page'),

] + static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)