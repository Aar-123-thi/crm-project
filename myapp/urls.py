from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('customers/', views.customers, name='customers'),
    path('leads/', views.leads, name='leads'),
    path('purchases/', views.purchases, name='purchases'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/edit/<int:id>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:id>/', views.delete_customer, name='delete_customer'),
    path('leads/add/', views.add_lead, name='add_lead'),
    path('leads/edit/<int:id>/', views.edit_lead, name='edit_lead'),
    path('leads/delete/<int:id>/', views.delete_lead, name='delete_lead'),
    path('leads/convert/<int:id>/', views.convert_lead, name='convert_lead'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
    path('profile/', views.profile, name='profile'),
    path('reports/', views.reports, name='reports'),
]


