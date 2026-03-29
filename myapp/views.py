from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from .models import Customer, Lead,  Profile, Sale, SaleItem, Product
from .forms import CustomerForm, LeadForm, PurchaseForm, ProfileImageForm, SaleForm
from collections import defaultdict

def index(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    total_customers = Customer.objects.count()
    total_leads = Lead.objects.exclude(status__iexact='converted').count()

    # NEW SALES LOGIC
    total_sales = Sale.objects.count()

    total_revenue = 0
    for sale in Sale.objects.all():
        for item in sale.items.all():
            total_revenue += item.total_price()

    recent_customers = Customer.objects.order_by('-id')[:5]
    recent_leads = Lead.objects.exclude(status__iexact='converted').order_by('-id')[:5]
    recent_sales = Sale.objects.order_by('-id')[:5]

    return render(request, 'dashboard.html', {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'recent_customers': recent_customers,
        'recent_leads': recent_leads,
        'recent_sales': recent_sales,
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
    total_sales = Sale.objects.count()

    total_revenue = 0
    daily_data = defaultdict(int)

    for sale in Sale.objects.all():
        sale_total = sum(item.total_price() for item in sale.items.all())

        total_revenue += sale_total
        daily_data[sale.date] += sale_total

    # Lead stats
    leads_new = Lead.objects.filter(status__iexact='new').count()
    leads_contacted = Lead.objects.filter(status__iexact='contacted').count()
    leads_converted = Lead.objects.filter(status__iexact='converted').count()

    return render(request, 'reports.html', {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'leads_new': leads_new,
        'leads_contacted': leads_contacted,
        'leads_converted': leads_converted,
        'daily_data': dict(daily_data),
    })

@login_required
def add_sale(request):
    products = Product.objects.all()
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():
            product_ids = request.POST.getlist('product[]')
            quantities = request.POST.getlist('quantity[]')

            # Only proceed if products were actually added
            if product_ids and any(product_ids): 
                sale = sale_form.save()
                for p_id, qty in zip(product_ids, quantities):
                    if p_id and qty:
                        product = Product.objects.get(id=p_id)
                        SaleItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=int(qty)
                        )
                return redirect('sales_history') # Redirect to history or dashboard
    else:
        sale_form = SaleForm()

    return render(request, 'add_sale.html', {'sale_form': sale_form, 'products': products})
    
@login_required
def daily_report(request, date):
    # We use prefetch_related so the Template can see 'product.name'
    sales = Sale.objects.filter(date=date).prefetch_related('items__product').annotate(
        items_count=Count('items') # Count how many unique products in this sale
    )

    # Use Sum and F expressions to calculate the money correctly
    total_data = SaleItem.objects.filter(sale__date=date).aggregate(
        grand_total=Sum(F('quantity') * F('product__price'))
    )
    
    total = total_data['grand_total'] or 0

    return render(request, 'daily_report.html', {
        'sales': sales,
        'total': total,
        'date': date
    })

@login_required
def sales_history(request):
    sales = Sale.objects.all().order_by('-date')

    return render(request, 'sales_history.html', {
        'sales': sales
    })

@login_required
def download_daily_report(request, date):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from django.http import HttpResponse

    sales = Sale.objects.filter(date=date)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{date}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"Daily Report - {date}", styles['Title']))
    elements.append(Spacer(1, 10))

    total = 0

    for sale in sales:
        elements.append(Paragraph(f"Customer: {sale.customer.name}", styles['Heading3']))

        for item in sale.items.all():
            line = f"{item.product.name} ({item.quantity} × ₹{item.product.price}) = ₹{item.total_price()}"
            elements.append(Paragraph(line, styles['Normal']))
            total += item.total_price()

        elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Total Revenue: ₹{total}", styles['Heading2']))

    doc.build(elements)
    return response