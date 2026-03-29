from django.contrib import admin
from .models import Customer, Lead, Purchase, Product, Sale, SaleItem
from .models import Profile

admin.site.register(Customer)
admin.site.register(Lead)
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(SaleItem)