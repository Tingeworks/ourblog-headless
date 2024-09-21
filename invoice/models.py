from django.db import models
from datetime import datetime
from .tasks import send_async_mail

class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False, default='Unknown')
    email = models.EmailField(max_length=100, blank=False, default='someone@example.com')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('paid', 'Paid'),
    ('cancelled', 'Cancelled'),
)

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    serial = models.CharField(max_length=20, unique=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def save(self, *args, **kwargs):
        # First, save the instance to ensure an id is generated
        if not self.serial:
            super().save(*args, **kwargs)  # Save to get the id
            current_date = datetime.now().strftime('%Y%m%d')
            padded_id = f'{self.id:04d}'  # Format id with leading zeros
            self.serial = f'T{current_date}{padded_id}'

        # Save again with the generated serial number
        super().save(*args, **kwargs)

    def mark_as_paid(self):
        self.status = 'paid'
        self.save()
        return True

    def reopen(self):
        self.status = "draft"
        self.save()
        return True
    
    def cancel(self):
        self.status = "cancelled"
        self.save()
        return True

    def send_invoice_email(self):
        subject = f"Invoice {self.serial} for {self.client.name}"
        # message = f"Dear {self.client.name},\n\n<h1>Please find attached the invoice for the services rendered.</h1>\n\nBest regards,\n\nYour Company"
        recipient_list = [self.client.email]

        html_email_template = """<!DOCTYPE html><html lang="en"><head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0"></head>

        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 2em 1em;">
            <div
                style="width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                <div style="text-align: center; padding-bottom: 20px;">
                    <h1 style="margin: 1em 0 0 0; color: #333333;">Invoice</h1>
                </div>
                <div style="font-size: 16px; color: #333333; line-height: 1.6;">
                    <p>Dear {client_name},</p>
                    <p>I hope this email finds you well.</p>
                    <p>Please find attached the invoice <strong>{invoice_number}</strong> for the services provided by
                        Tingeworks. The details of the invoice are as follows:</p>
                    <div style="background-color: #f9f9f9; padding: 10px; border-left: 4px solid #ff178f; margin-bottom: 20px;">
                        <p><strong>Invoice Number:</strong> {invoice_number}</p>
                        <p><strong>Invoice Date:</strong> {invoice_date}</p>
                        <p><strong>Due Date:</strong> {due_date}</p>
                        <p><strong>Total Amount Due:</strong> {total_amount} BDT</p>
                    </div>
                    <h2 style="font-size: 18px; margin-bottom: 10px;">Description of Services:</h2>
                    <p>{service_description}</p>
                    <p>Please make the payment by the due date mentioned above. You can make the payment via Wise, bank
                        transfer, or Payoneer:</p>
                    <h2 style="font-size: 18px; margin-bottom: 10px;">Bank Transfer Details:</h2>
                    <p><strong>Bank Name:</strong> The City Bank</p>
                    <p><strong>Account Name:</strong> Imtiaz Al Shariar</p>
                    <p><strong>Account Number:</strong> 2594094312001</p>
                    <p><strong>SWIFT/BIC Code:</strong> CIBLBDDH</p>
                    <p><strong>BKASH:</strong> 01846342780</p>
                    <div style="margin: 20px 0;">
                        <p>If you have any questions or need further information, please feel free to contact me directly at:
                        </p>
                        <p>Email: <a href="mailto:imtiaz@tingeworks.com">imtiaz@tingeworks.com</a></p>
                        <p>Phone: +8801846342780</p>
                    </div>
                    <p>Thank you for your prompt attention to this matter.</p>
                    <p>Best regards,</p>
                    <p><strong>Imtiaz Al Shariar Shamrat</strong><br>Owner, Tingeworks</p>
                </div>
                <div
                    style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #dddddd; font-size: 14px; color: #777777;">
                    <p>&copy; 2024 Tingeworks. All rights reserved.</p>
                </div>
            </div>
        </body>

        </html>"""

        # Example of how you can use it:
        email_html_content = html_email_template.format(
            client_name=self.client.name,
            invoice_number=self.serial,
            invoice_date="01 May 2024",
            due_date="09 May 2024",
            total_amount="71,000",
            service_description=self.description
        )

        if self.status == 'draft':
            self.status = 'sent'
            self.save()

        send_async_mail.delay(subject, "", recipient_list, html_message=email_html_content)
        return True


    def __str__(self):
        return self.serial