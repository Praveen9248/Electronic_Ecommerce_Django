from django.conf import settings
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q

from .decorators import customer_required, technician_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Order, OrderItem, Payment, Product,Cart,CartItem, ServiceRequest, ServiceStatus, TechnicianAssignment

from .forms import ProductFilterForm, RepairProductForm, ServiceRequestForm, UpdateServiceRequestStatusForm
from django import forms

from django.http import HttpResponse
import uuid
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.models import PayPalIPN

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def redirect_based_on_role(user):
    if user.role == 'Customer':
        return redirect('home_page')
    elif user.role == 'Technician':
        return redirect('technician_page')
    else:
        return redirect('/admin/')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect_based_on_role(request.user)
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'Auth/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect_based_on_role(request.user)
    else:
        form = CustomUserCreationForm()
    return render(request, 'Auth/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home_page')

def search_filters(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'Customer/product_list.html', {
        'query': query,
        'results': results,
    })

def home(request):
    return render(request,'Customer/index.html')

@login_required
@technician_required
def technician_view(request):
    assignments = TechnicianAssignment.objects.filter(
        technician=request.user,
        request__status__in=[
            'pending', 'submitted', 'accepted', 'rejected', 'cancelled', 'assigned',
            'in_progress', 'awaiting_parts', 'on_hold'
        ]
    ).select_related('request', 'request__repair_product').order_by('-assigned_at')

    assigned_requests = [a.request for a in assignments]

    context = {
        'assigned_requests': assigned_requests,
    }
    return render(request, 'Technician/index.html', context)

@login_required
@technician_required
def task_detail(request, request_id):
    try:
        assigned_request = ServiceRequest.objects.select_related('repair_product__brand', 'user').get(
            id=request_id,
            assignment__technician=request.user
        )
    except ServiceRequest.DoesNotExist:
        return render(request, 'Technician/index.html', {'request_id': request_id})

    if request.method == 'POST':
        form = UpdateServiceRequestStatusForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            notes = form.cleaned_data.get('notes')
            work_done = form.cleaned_data.get('work_done')
            parts_used = form.cleaned_data.get('parts_used')
            final_cost = form.cleaned_data.get('final_cost')

            assigned_request.status = new_status
            assigned_request.save()

            ServiceStatus.objects.create(
                request=assigned_request,
                updated_by=request.user,
                status=new_status,
                notes=notes,
                work_done=work_done,
                parts_used=parts_used,
                final_cost=final_cost
            )
            return redirect('task_detail_page', request_id=request_id)
    else:
        form = UpdateServiceRequestStatusForm(initial={
            'status': assigned_request.status
        })

    context = {
        'assigned_request': assigned_request,
        'form': form,
    }
    return render(request, 'Technician/task_detail.html', context)

@login_required
@technician_required
def technician_dashboard(request):
    technician = request.user
    context = {
        'technician': technician,
    }
    return render(request,'Technician/dashboard.html',context)

@login_required
@technician_required
def completed_requests_view(request):
    completed_assignments = TechnicianAssignment.objects.filter(
        technician=request.user,
        request__status='completed'
    ).select_related('request').order_by('-assigned_at')

    completed_requests = [a.request for a in completed_assignments]

    context = {
        'completed_requests': completed_requests
    }
    return render(request, 'Technician/completed_requests.html', context)

@login_required
@customer_required
def services(request):
    service_requests = ServiceRequest.objects.filter(user=request.user).select_related('repair_product').order_by('-request_date')
    return render(request, 'Customer/services.html', {'service_requests': service_requests})

@login_required
@customer_required
def add_service_request(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.save()
            return redirect('service_page')
    else:
        form = ServiceRequestForm()

    return render(request, 'Customer/add_service_request.html', {'form': form})

@login_required
@customer_required
def add_repair_product(request):
    if request.method == 'POST':
        form = RepairProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('add_service_request')
    else:
        form = RepairProductForm()

    return render(request, 'Customer/add_repair_product.html', {'form': form})

@login_required
@customer_required
def contact(request):
    return render(request,'Customer/contact.html')

@login_required
@customer_required
def about(request):
    return render(request,'Customer/about.html')

@login_required
@customer_required
def shop(request):
    products = Product.objects.all()
    form = ProductFilterForm(request.GET)

    if form.is_valid():
        category = form.cleaned_data.get('category')
        brand = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')

        if category:
            products = products.filter(category=category)
        if brand:
            products = products.filter(brand=brand)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
    items_per_page = 6      
    paginator = Paginator(products, items_per_page)
    page_number = request.GET.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    context = {'page': page,'form':form}
    return render(request,'Customer/shop.html',context)

@login_required
@customer_required
def shop_detail(request,slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category,
        brand=product.brand
    ).exclude(slug=slug)[:4]
    return render(request,'Customer/shop-detail.html',{'context':product,'related_products':related_products})

@login_required
@customer_required
def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, user__isnull=True)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart

@login_required
@customer_required
def cart(request):
    cart = get_or_create_cart(request)
    grand_total = sum(item.total_price() for item in cart.items.all())
    return render(request,'Customer/cart.html',{'cart': cart, 'grand_total': grand_total})

@login_required
@customer_required
def add_to_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart_page')

@login_required
@customer_required
@require_POST
def update_cart_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity'))
        cart_item = get_object_or_404(CartItem, id=item_id)

        cart_item.quantity = quantity
        cart_item.save()

        return redirect('cart_page')
    return HttpResponseRedirect(reverse('cart_page'))

@login_required
@customer_required
@require_POST
def remove_cart_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()

        return redirect('cart_page')
    return HttpResponseRedirect(reverse('cart_page'))

@login_required
@customer_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        
        return redirect('view-cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == "POST":
        shipping_address = request.POST.get('shipping_address')
        billing_address = request.POST.get('billing_address')

        order = Order.objects.create(
            user=request.user,
            total_amount=total_price,
            shipping_address=shipping_address,
            billing_address=billing_address,
            order_status="Pending",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()
        
        
        return redirect(reverse('billing', args=[order.id]))

    return render(request, 'Customer/checkout.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
@customer_required
def billing(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': order.total_amount,
        'item_name': f'Order {order.id}',
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('payment-success', args=[order.id])}",
        'cancel_return': f"http://{host}{reverse('payment-failed', args=[order.id])}",
    }

    paypal_form = PayPalPaymentsForm(initial=paypal_dict)

    return render(request, 'Customer/billing.html', {'paypal_form': paypal_form, 'order': order})

@login_required
@customer_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.order_status = 'Paid'
    order.payment_method = 'PayPal'
    order.save()

    Payment.objects.create(
        order=order,
        payment_id=str(uuid.uuid4()),
        payment_method='PayPal',
        amount=order.total_amount,
        currency='USD',
        status='Completed'
    )
    return render(request, 'Customer/payment_success.html', {'order': order})

@login_required
@customer_required
def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.order_status = 'Payment Failed'
    order.save()
    
    return render(request, 'Customer/payment_failure.html', {'order': order})

def paypal_ipn_listener(request):
    ipn_obj = PayPalIPN.objects.last()

    if ipn_obj and ipn_obj.payment_status == "Completed":
        try:
            order = Order.objects.get(id=ipn_obj.invoice)
            order.order_status = 'Paid'
            order.transaction_id = ipn_obj.txn_id
            order.payment_method = 'PayPal'
            order.save()

            Payment.objects.create(
                order=order,
                payment_id=ipn_obj.txn_id,
                payment_method='PayPal',
                amount=ipn_obj.mc_gross,
                currency=ipn_obj.mc_currency,
                status=ipn_obj.payment_status,
                payment_data=ipn_obj.__dict__
            )
            return HttpResponse("Payment processed", status=200)
        except Order.DoesNotExist:
            return HttpResponse("Order not found", status=400)
    return HttpResponse("Invalid IPN", status=400)