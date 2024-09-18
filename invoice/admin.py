from django.contrib import admin
from django.shortcuts import redirect
from .models import Client, Invoice
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import path
from django.utils.safestring import mark_safe
from django.urls import reverse

# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('serial', 'get_client_name', 'price', 'created_at')
    search_fields = ('serial', 'get_client_name')
    readonly_fields =  ('serial', 'created_at', 'status')

    def get_client_name(self, obj):
        return obj.client.name
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:invoice_id>/send_email/',
                self.admin_site.admin_view(self.send_invoice_email),
                name='send-invoice-email',
            ),
        ]
        return custom_urls + urls

    def send_invoice_email(self, request, invoice_id):
        invoice = self.get_object(request, invoice_id)
        if invoice:
            try:
                invoice.send_invoice_email()
                self.message_user(request, f"Invoice email sent successfully to {invoice.client.email}.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Failed to send invoice email: {e}", messages.ERROR)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    def send_email_button(self, obj):
        url = reverse('admin:send-invoice-email', args=[obj.pk])
        return mark_safe(f'<a class="button" href="{url}">Send Email</a>')
    send_email_button.allow_tags = True
    send_email_button.short_description = 'Send Invoice Email'

    readonly_fields = ['send_email_button']

    fieldsets = (
        (None, {
            'fields': ('client', 'description', 'price', 'status', 'send_email_button'),
        }),
    )
    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')