from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Admin', 'Admin'),
        ('Technician', 'Technician'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Customer')
    
    def __str__(self):
        return f"{self.username} - {self.role}"
    

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
      return f"Image of {self.product.name}"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=5
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

    def total_price(self):
        return self.quantity * self.product.price
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    order_status = models.CharField(max_length=50, default='Pending')
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.order_date}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order.id}"
    
class RepairProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repaired_devices')
    device_model = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    serial_number = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, help_text="Optional description or notes about the device.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_model} ({self.serial_number if self.serial_number else 'No SN'}) - {self.user.username}"

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('awaiting_parts', 'Awaiting Parts'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('shipped', 'Shipped'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    repair_product = models.ForeignKey(RepairProduct, on_delete=models.CASCADE, related_name='requests')
    request_date = models.DateTimeField(auto_now_add=True)
    issue_description = models.TextField()
    customer_notes = models.TextField(blank=True, null=True)
    pickup_option = models.BooleanField(default=False, help_text="Customer will drop off/pickup.")
    shipping_address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_requests')

    def __str__(self):
        return f"Request #{self.id} - {self.repair_product.device_model}"

class TechnicianAssignment(models.Model):
    request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='assignment')
    technician = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'Technician'},
        related_name='assigned_requests'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Assignment for Request #{self.request.id} to {self.technician.username if self.technician else 'Not Assigned'}"

class ServiceStatus(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('diagnosis', 'Diagnosis'),
        ('repairing', 'Repairing'),
        ('testing', 'Testing'),
        ('completed', 'Completed'),
        ('needs_customer_info', 'Needs Customer Info'),
        ('parts_ordered', 'Parts Ordered'),
        ('ready', 'Ready'),
    ]

    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='status_updates')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='status_updates')
    updated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    work_done = models.TextField(blank=True, null=True, help_text="Details of the work performed.")
    parts_used = models.TextField(blank=True, null=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Status for Request #{self.request.id} - {self.get_status_display()} at {self.updated_at}"