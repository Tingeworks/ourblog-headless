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
    list_display = ('serial', 'status', 'get_client_name', 'price', 'created_at')
    search_fields = ('serial', 'get_client_name')

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
            path(
                '<int:invoice_id>/mark_as_paid/',
                self.admin_site.admin_view(self.mark_as_paid),
                name='mark-as-paid',
            ),
        ]
        return custom_urls + urls
    
    def mark_as_paid(self, request, invoice_id):
        invoice = self.get_object(request, invoice_id)
        if invoice:
            invoice.mark_as_paid()
            self.message_user(request, "Marked as paid", messages.SUCCESS)
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
        if obj.pk:
            url = reverse('admin:send-invoice-email', args=[obj.pk])
            url1 = reverse('admin:mark-as-paid', args=[obj.pk])
            return mark_safe(f'<div style="display:flex;column-gap:15px;margin:0;padding:0;align-items:center;justify-content:center;"><a class="button" href="{url}">Send Email</a><a class="button" href="{url1}">Mark as Paid</a></div>')
        return 'Actions appear after saving the record'

    send_email_button.allow_tags = True
    send_email_button.short_description = 'Actions'

    readonly_fields = ['send_email_button', 'created_at', 'serial', 'status']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Call the original method to get the default behavior
        response = super().change_view(request, object_id, form_url, extra_context)
        
        # Get the invoice object
        invoice = self.get_object(request, object_id)
        
        # Check if the invoice is paid and display the message
        if invoice and invoice.status == 'paid':
            self.message_user(request, "This invoice has been paid.", messages.INFO)

        return response

    fieldsets = (
        (None, {
            'fields': ('serial', 'client', 'description', 'price', 'created_at', 'status', 'send_email_button'),
        }),
    )
    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')