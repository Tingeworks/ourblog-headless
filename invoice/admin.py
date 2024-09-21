from gettext import ngettext
from django.contrib import admin
from unfold.admin import ModelAdmin
from django.shortcuts import redirect
from django.db.models import QuerySet
from .models import Client, Invoice
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib import messages
from django.urls import path, reverse_lazy
from django.utils.safestring import mark_safe
from django.urls import reverse
from unfold.decorators import action

    
def notify(self, request, queryset=None):
    for invoice in queryset:
        invoice.send_invoice_email()
    self.message_user(request, "Reminders sent! Everyone recieved an email.", messages.INFO)


# Register your models here.
@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ('serial', 'invoice_status', 'client_name', 'price', 'created_at')
    search_fields = ('serial', 'client')
    list_filter = ('status', 'created_at')
    actions = [notify]

    def invoice_status (self, obj):
        return "Paid" if obj.status == 'paid' else obj.status

    def client_name(self, obj):
        return mark_safe(f"<a href='/admin/invoice/client/{obj.client.id}/change/'>{obj.client.name} ({obj.client.email})</a>")

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
            path(
                '<int:invoice_id>/reopen/',
                self.admin_site.admin_view(self.reopen),
                name='reopen'
            ),
            path(
                '<int:invoice_id>/cancel/',
                self.admin_site.admin_view(self.cancel),
                name='cancel'
            ),
        ]
        return custom_urls + urls
    
    def cancel(self, request, invoice_id):
        invoice = self.get_object(request, invoice_id)
        if invoice:
            invoice.cancel()
            self.message_user(request, "Invoice has been cancelled", messages.SUCCESS)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    
    def reopen(self, request, invoice_id):
        invoice = self.get_object(request, invoice_id)
        if invoice:
            invoice.reopen()
            self.message_user(request, "Invoice has been reopened", messages.SUCCESS)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
            if obj.status == 'paid' or obj.status == 'cancelled':
                url = reverse('admin:reopen', args=[obj.pk])    
                return mark_safe(f'<p style="color: grey; padding:0; margin: 0;"><span>({obj.status})</span> Invoice has been closed. <a href="{url}" >Reopen?</a></p>')

            send_invoice_url = reverse('admin:send-invoice-email', args=[obj.pk])
            confirm_payment_url = reverse('admin:mark-as-paid', args=[obj.pk])
            cancel_payment_url = reverse('admin:cancel', args=[obj.pk])
            return mark_safe(f'<div style="display:flex;column-gap:15px;margin:0;padding:0;align-items:center;justify-content:center;"><a class="button" href="{send_invoice_url}">Send Email</a><a class="button" href="{confirm_payment_url}">Mark as Paid</a><a class="button" href="{cancel_payment_url}">Cancel</a></div>')
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

        if invoice and invoice.status == 'cancelled':
            self.message_user(request, "This invoice has been cancelled.", messages.INFO)
        return response



    fieldsets = (
        (None, {
            'fields': ('serial', 'client', 'description', 'price', 'created_at', 'status', 'send_email_button'),
        }),
    )

    
@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')