from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import models
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import tempfile
import os
from .models import Bill, BillItem


@shared_task(max_retries=3)
def send_bill_email_task(bill_id, customer_email=None):
    """ 
    Send generated bill to customer email using Celery
    """
    try:
        # Get bill with all related data
        bill = Bill.objects.select_related('customer').prefetch_related(
            'items__product_variant__product',
            'items__product_variant__size', 
            'items__product_variant__color',
            'items__product'
        ).get(id=bill_id)
        
        # Use customer email from bill if not provided
        if not customer_email:
            customer_email = bill.customer.email
        
        if not customer_email:
            return {
                'status': 'error',
                'message': 'No customer email found'
            }
        
        # Generate HTML email content
        html_content = render_to_string('shop/email/bill_email.html', {
            'bill': bill,
            'customer': bill.customer,
            'items': bill.items.all(),
            'company_name': 'Dress Shop',
            'company_address': '123 Fashion Street, Style City',
            'company_phone': '+91 98765 43210',
            'company_email': 'support@dressshop.com',
            'generated_date': timezone.now(),
        })
        
        # Generate PDF attachment
        pdf_content = generate_bill_pdf(bill)

        
        
        # Create email
        subject = f'Bill #{bill.bill_number} - Dress Shop'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [customer_email]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=from_email,
            to=to_email
        )
        email.content_subtype = 'html'
        
        # Attach PDF
        email.attach(
            f'bill_{bill.bill_number}.pdf',
            pdf_content,
            'application/pdf'
        )
        
        # Send email
        email.send()
        
        # Update bill status
        bill.status = 'sent'
        bill.save(update_fields=['status'])
        
        return {
            'status': 'success',
            'message': f'Bill {bill.bill_number} sent successfully to {customer_email}',
            'bill_id': bill_id,
            'customer_email': customer_email
        }
        
    except Bill.DoesNotExist:
        return {
            'status': 'error',
            'message': f'Bill with ID {bill_id} not found'
        }
    except Exception as exc:
        # Retry logic (without bind=True, we can't use self.retry)
        # For now, just return error
        return {
            'status': 'error',
            'message': f'Failed to send bill email: {str(exc)}',
            'bill_id': bill_id
        }


def generate_bill_pdf(bill):
    """
    Generate Flipkart-style professional invoice using ReportLab
    """
    # Create PDF in memory using BytesIO
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Build the story (content)
    story = []
    
    # Header with Logo placeholder and Invoice info
    header_data = [
        [Paragraph("<b>DRESS SHOP</b>", normal_style), Paragraph(f"<b>INVOICE #{bill.bill_number}</b>", normal_style)],
        [Paragraph("Fashion Retail Excellence", normal_style), Paragraph(f"Date: {timezone.now().strftime('%d-%b-%Y')}", normal_style)],
        [Paragraph("123 Fashion Street, Style City", normal_style), Paragraph(f"Due Date: {timezone.now().strftime('%d-%b-%Y')}", normal_style)],
        [Paragraph("Phone: +91 98765 43210", normal_style), Paragraph(f"Status: {bill.status.upper()}", normal_style)],
        [Paragraph("Email: support@dressshop.com", normal_style), ""]
    ]
    
    header_table = Table(header_data, colWidths=[3.5*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Billing and Shipping Information
    if bill.customer:
        billing_info = [
            [Paragraph("<b>BILL TO</b>", normal_style), Paragraph("<b>SHIP TO</b>", normal_style)],
            [bill.customer.name or 'N/A', bill.customer.name or 'N/A'],
            [bill.customer.email or 'N/A', bill.customer.address or 'N/A'],
            [bill.customer.phone or 'N/A', bill.customer.phone or 'N/A']
        ]
    else:
        billing_info = [
            [Paragraph("<b>BILL TO</b>", normal_style), Paragraph("<b>SHIP TO</b>", normal_style)],
            ['Walk-in Customer', 'Walk-in Customer'],
            ['N/A', 'N/A'],
            ['N/A', 'N/A']
        ]
    
    billing_table = Table(billing_info, colWidths=[3.5*inch, 2.5*inch])
    billing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (1, 1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(billing_table)
    story.append(Spacer(1, 15))
    
    # Order Items Table
    items_data = [
        ['#', 'Item Description', 'Size', 'Color', 'Qty', 'Unit Price', 'GST (18%)', 'Total']
    ]
    
    for idx, item in enumerate(bill.items.all(), 1):
        gst_amount = float(item.unit_price) * item.quantity * 0.18
        items_data.append([
            str(idx),
            item.product_variant.product.name if item.product_variant else 'N/A',
            item.product_variant.size.name if item.product_variant and item.product_variant.size else 'N/A',
            item.product_variant.color.name if item.product_variant and item.product_variant.color else 'N/A',
            str(item.quantity),
            f"₹{item.unit_price:.2f}",
            f"₹{gst_amount:.2f}",
            f"₹{item.total:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[0.4*inch, 2.2*inch, 0.7*inch, 0.7*inch, 0.5*inch, 0.9*inch, 0.8*inch, 0.8*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))
    
    # GST Summary and Totals
    gst_summary = [
        [Paragraph("<b>GST SUMMARY</b>", normal_style), Paragraph("<b>ORDER SUMMARY</b>", normal_style)],
        ['CGST (9%):', 'Subtotal:'],
        [f"₹{float(bill.tax_amount)/2:.2f}", f"₹{bill.subtotal:.2f}"],
        ['SGST (9%):', 'Discount:'],
        [f"₹{float(bill.tax_amount)/2:.2f}", f"₹{bill.discount_amount:.2f}"],
        ['Total GST:', 'GST Amount:'],
        [f"₹{bill.tax_amount:.2f}", f"₹{bill.tax_amount:.2f}"],
        ['', ''],
        ['', 'Shipping:'],
        ['', '₹0.00'],
        ['', ''],
        ['', '<b>Grand Total:</b>'],
        ['', f"<b>₹{bill.total_amount:.2f}</b>"]
    ]
    
    gst_table = Table(gst_summary, colWidths=[2.5*inch, 2*inch])
    gst_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
        ('BACKGROUND', (0, 1), (1, 1), colors.lightgreen),
        ('BACKGROUND', (0, 2), (1, 2), colors.lightgreen),
        ('BACKGROUND', (0, 3), (1, 3), colors.lightgreen),
        ('BACKGROUND', (0, 4), (1, 4), colors.lightgreen),
        ('BACKGROUND', (0, 5), (1, 5), colors.lightgreen),
        ('BACKGROUND', (0, 6), (1, 6), colors.lightgreen),
        ('BACKGROUND', (0, 7), (1, 7), colors.lightgreen),
        ('BACKGROUND', (0, 8), (1, 9), colors.lightgrey),
        ('BACKGROUND', (0, 10), (1, 10), colors.lightgreen),
        ('BACKGROUND', (0, 11), (1, 11), colors.lightgreen),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 10), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 10), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 10), (-1, -1), 8),
        ('TOPPADDING', (0, 10), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(gst_table)
    story.append(Spacer(1, 15))
    
    # Payment Information
    payment_info = [
        [Paragraph("<b>PAYMENT INFORMATION</b>", normal_style), Paragraph("<b>TERMS & CONDITIONS</b>", normal_style)],
        [f"Payment Method: {bill.get_payment_method_display()}", "1. Goods once sold will not be taken back."],
        [f"Payment Status: {bill.status.upper()}", "2. All disputes subject to Dress Shop jurisdiction."],
        [f"Invoice Date: {timezone.now().strftime('%d-%b-%Y')}", "3. Payment due within 30 days."],
        ["", "4. Late payment subject to 18% annual interest."],
        ["", "5. Prices inclusive of all taxes."]
    ]
    
    payment_table = Table(payment_info, colWidths=[3.5*inch, 2.5*inch])
    payment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
        ('BACKGROUND', (0, 1), (1, 1), colors.lightblue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 10))
    
    # Footer
    footer_data = [
        [Paragraph("<b>Thank you for your business!</b>", normal_style)],
        [Paragraph(f"Generated on: {timezone.now().strftime('%d-%b-%Y %H:%M:%S')}", normal_style)],
        [Paragraph("For any queries, contact: support@dressshop.com | +91 98765 43210", normal_style)]
    ]
    
    footer_table = Table(footer_data, colWidths=[6*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(footer_table)
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content from buffer
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


@shared_task
def send_bulk_bill_emails(bill_ids):
    """
    Send multiple bills in bulk (for batch processing)
    """
    results = []
    
    for bill_id in bill_ids:
        try:
            result = send_bill_email_task(bill_id)
            results.append(result)
        except Exception as e:
            results.append({
                'status': 'error',
                'message': f'Failed to process bill {bill_id}: {str(e)}',
                'bill_id': bill_id
            })
    
    return {
        'status': 'completed',
        'total_processed': len(bill_ids),
        'successful': len([r for r in results if r['status'] == 'success']),
        'failed': len([r for r in results if r['status'] == 'error']),
        'results': results
    }


@shared_task
def send_daily_bills_summary():
    """
    Send daily summary of all bills generated (scheduled task)
    """
    try:
        today = timezone.now().date()
        bills_today = Bill.objects.filter(
            created_at__date=today
        ).select_related('customer')
        
        if not bills_today.exists():
            return {
                'status': 'no_bills',
                'message': 'No bills generated today'
            }
        
        # Generate summary HTML
        html_content = render_to_string('shop/email/daily_bills_summary.html', {
            'bills': bills_today,
            'total_amount': bills_today.aggregate(total=models.Sum('total_amount'))['total'] or 0,
            'total_bills': bills_today.count(),
            'date': today,
            'company_name': 'Dress Shop',
        })
        
        # Send summary email to admin
        subject = f'Daily Bills Summary - {today.strftime("%Y-%m-%d")}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else ['admin@dressshop.com']
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=from_email,
            to=to_email
        )
        email.content_subtype = 'html'
        email.send()
        
        return {
            'status': 'success',
            'message': f'Daily summary sent for {bills_today.count()} bills',
            'total_amount': bills_today.aggregate(total=models.Sum('total_amount'))['total'] or 0
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to send daily summary: {str(e)}'
        }