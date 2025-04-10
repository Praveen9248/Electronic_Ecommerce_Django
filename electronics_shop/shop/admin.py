from django.contrib import admin
from .models import (
    User,
    Category,
    Brand,
    Product,
    ProductImage,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Review,
    RepairProduct,
    ServiceRequest,
    TechnicianAssignment,
    ServiceStatus,
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )
    ordering = ('username',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'available', 'created_at', 'updated_at')
    list_filter = ('category', 'brand', 'available')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'alt_text')
    list_filter = ('product',)
    search_fields = ('product__name', 'alt_text')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    search_fields = ('id', 'user__username')
    raw_id_fields = ('user',)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    raw_id_fields = ('product',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')
    list_filter = ('cart',)
    search_fields = ('cart__id', 'product__name')
    raw_id_fields = ('cart', 'product')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    raw_id_fields = ('product',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'total_amount', 'order_status', 'payment_method')
    list_filter = ('order_status', 'payment_method', 'order_date')
    search_fields = ('id', 'user__username', 'shipping_address', 'billing_address', 'transaction_id')
    raw_id_fields = ('user',)
    inlines = [OrderItemInline]
    date_hierarchy = 'order_date'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order',)
    search_fields = ('order__id', 'product__name')
    raw_id_fields = ('order', 'product')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'payment_method', 'amount', 'status', 'timestamp')
    list_filter = ('payment_method', 'status', 'timestamp')
    search_fields = ('payment_id', 'order__id', 'transaction_id')
    raw_id_fields = ('order',)
    date_hierarchy = 'timestamp'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'updated_at', 'product')
    search_fields = ('product__name', 'user__username', 'comment')
    raw_id_fields = ('product', 'user')
    ordering = ('-created_at',)

@admin.register(RepairProduct)
class RepairProductAdmin(admin.ModelAdmin):
    list_display = ('device_model', 'brand', 'serial_number', 'user', 'purchase_date')
    list_filter = ('brand',)
    search_fields = ('device_model', 'serial_number', 'user__username')
    raw_id_fields = ('user', 'brand')

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'repair_product', 'request_date', 'status')
    list_filter = ('status', 'request_date', 'pickup_option')
    search_fields = ('id', 'user__username', 'repair_product__device_model', 'issue_description')
    raw_id_fields = ('user', 'repair_product', 'order')
    date_hierarchy = 'request_date'

@admin.register(TechnicianAssignment)
class TechnicianAssignmentAdmin(admin.ModelAdmin):
    list_display = ('request', 'technician', 'assigned_at')
    raw_id_fields = ('request', 'technician')

@admin.register(ServiceStatus)
class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = ('request', 'status', 'updated_by', 'updated_at')
    list_filter = ('status', 'updated_by', 'updated_at', 'request')
    raw_id_fields = ('request', 'updated_by')
    date_hierarchy = 'updated_at'