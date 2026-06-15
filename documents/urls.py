from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),

    path('', views.document_list, name='document_list'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/create/', views.document_create, name='document_create'),
    path('documents/<int:pk>/edit/', views.document_edit, name='document_edit'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),

    path('documents/<int:pk>/send/', views.send_to_approval, name='send_to_approval'),
    path('documents/<int:pk>/approve/', views.approve_document, name='approve_document'),
    path('documents/<int:pk>/reject/', views.reject_document, name='reject_document'),
]