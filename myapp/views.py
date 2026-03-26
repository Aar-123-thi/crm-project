from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import Customer, Lead, Purchase, Profile
from .forms import CustomerForm, LeadForm, PurchaseForm, ProfileImageForm


def index(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    total_customers = Customer.objects.count()
    total_leads = Lead.objects.exclude(status__iexact='converted').count()
    total_purchases = Purchase.objects.count()
    total_revenue = sum(p.product.price * p.quantity for p in Purchase.objects.all())
    recent_customers = Customer.objects.order_by('-id')[:5]
    recent_leads = Lead.objects.exclude(status__iexact='converted').order_by('-id')[:5]
    recent_purchases = Purchase.objects.order_by('-id')[:5]

    return render(request, 'dashboard.html', {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'total_purchases': total_purchases,
        'total_revenue': total_revenue,
        'recent_customers': recent_customers,
        'recent_leads': recent_leads,
        'recent_purchases': recent_purchases,
    })


@login_required
def customers(request):
    customers = Customer.objects.all()
    return render(request, 'customers.html', {'customers': customers})


@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CustomerForm()
    return render(request, 'add_customer.html', {'form': form})


@login_required
def edit_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        return redirect('customers')
    return render(request, 'edit_customer.html', {'form': form})


@login_required
def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.delete()
    return redirect('customers')


@login_required
def leads(request):
    leads = Lead.objects.exclude(status__iexact='converted')
    return render(request, 'leads.html', {'leads': leads})


@login_required
def add_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = LeadForm()
    return render(request, 'add_lead.html', {'form': form})


@login_required
def edit_lead(request, id):
    lead = get_object_or_404(Lead, id=id)
    form = LeadForm(request.POST or None, instance=lead)
    if form.is_valid():
        form.save()
        return redirect('leads')
    return render(request, 'edit_lead.html', {'form': form})


@login_required
def delete_lead(request, id):
    lead = get_object_or_404(Lead, id=id)
    lead.delete()
    return redirect('leads')


@login_required
def convert_lead(request, id):
    lead = get_object_or_404(Lead, id=id)

    # Prevent duplicate conversion
    if lead.status.lower() != 'converted':

        # Prevent duplicate customer creation
        if not Customer.objects.filter(email=lead.email).exists():
            Customer.objects.create(
                name=lead.name,
                phone=lead.phone,
                email=lead.email
            )

        lead.status = 'converted'
        lead.save()

    return redirect('customers')


@login_required
def purchases(request):
    purchases = Purchase.objects.all()
    return render(request, 'purchases.html', {'purchases': purchases})


@login_required
def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PurchaseForm()
    return render(request, 'add_purchase.html', {'form': form})

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileImageForm(instance=profile)

    return render(request, 'profile.html', {
        'profile': profile,
        'form': form
    })


@login_required
def reports(request):
    total_customers = Customer.objects.count()
    total_leads = Lead.objects.exclude(status__iexact='converted').count()
    total_purchases = Purchase.objects.count()
    total_revenue = sum(p.product.price * p.quantity for p in Purchase.objects.all())
    leads_new = Lead.objects.filter(status__iexact='new').count()
    leads_contacted = Lead.objects.filter(status__iexact='contacted').count()
    leads_converted = Lead.objects.filter(status__iexact='converted').count()

    return render(request, 'reports.html', {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'total_purchases': total_purchases,
        'total_revenue': total_revenue,
        'leads_new': leads_new,
        'leads_contacted': leads_contacted,
        'leads_converted': leads_converted,
    })

