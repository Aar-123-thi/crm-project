from django.contrib import admin
from .models import Customer, Lead, Purchase, Product
from .models import Profile

admin.site.register(Customer)
admin.site.register(Lead)
admin.site.register(Purchase)
admin.site.register(Profile)
admin.site.register(Product)

