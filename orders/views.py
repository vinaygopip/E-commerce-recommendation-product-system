from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.models import Cart
from recommendations.engine import log_user_activity
from decimal import Decimal
import io

# ReportLab imports for PDF Invoice Generation (with graceful fallback)
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, "Your cart is currently empty. Add products before checking out.")
        return redirect('product_list')

    profile = getattr(request.user, 'profile', None)
    initial_data = {
        'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        'email': request.user.email,
        'phone': profile.phone_number if profile else '',
        'address': profile.address if profile else '',
        'city': profile.city if profile else '',
        'state': profile.state if profile else '',
        'postal_code': profile.postal_code if profile else '',
        'payment_method': 'Card',
    }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            
            subtotal = cart.get_total_price()
            # Free shipping over 500, else 50
            shipping = Decimal('0.00') if subtotal >= 500 else Decimal('50.00')
            order.subtotal = subtotal
            order.discount_amount = cart.get_total_savings()
            order.shipping_fee = shipping
            order.total_amount = subtotal + shipping
            order.payment_status = 'Paid' if order.payment_method != 'COD' else 'Pending'
            order.order_status = 'Processing'
            order.save()

            # Create OrderItems and record PURCHASE user activity
            for c_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=c_item.product,
                    product_name=c_item.product.name,
                    price=c_item.product.discounted_price,
                    quantity=c_item.quantity,
                    total_price=c_item.get_subtotal()
                )

                # Reduce stock
                if c_item.product.stock >= c_item.quantity:
                    c_item.product.stock -= c_item.quantity
                    c_item.product.save()

                # Log PURCHASE activity for ML models
                log_user_activity(
                    user=request.user,
                    session_key=request.session.session_key,
                    product=c_item.product,
                    activity_type='PURCHASE'
                )

            # Clear cart
            cart.items.all().delete()

            messages.success(request, f"Order #{order.order_number} placed successfully!")
            return redirect('order_success', order_number=order.order_number)
    else:
        form = CheckoutForm(initial=initial_data)

    subtotal = cart.get_total_price()
    shipping = Decimal('0.00') if subtotal >= 500 else Decimal('50.00')
    total = subtotal + shipping

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart.items.all(),
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'savings': cart.get_total_savings(),
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_invoice_pdf_view(request, order_number):
    """
    Generates and downloads a branded PDF tax invoice for the order using ReportLab.
    """
    order = get_object_or_404(Order, order_number=order_number)
    if not request.user.is_staff and order.user != request.user:
        raise Http404("Invoice not accessible.")

    if not HAS_REPORTLAB:
        return HttpResponse("PDF generation requires the 'reportlab' package. Please run 'pip install reportlab'.", content_type="text/plain", status=501)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=15
    )
    bold_style = ParagraphStyle(
        'BoldText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10
    )

    # Header
    elements.append(Paragraph("ShopSmart E-Commerce Tax Invoice", title_style))
    elements.append(Paragraph("Smart ML-Powered Shopping Experience • MCA Final Year Project", subtitle_style))
    elements.append(Spacer(1, 10))

    # Order details table
    header_data = [
        [
            Paragraph(f"<b>Invoice To:</b><br/>{order.full_name}<br/>{order.address}<br/>{order.city}, {order.state} - {order.postal_code}<br/>Phone: {order.phone}<br/>Email: {order.email}", styles['Normal']),
            Paragraph(f"<b>Order Number:</b> {order.order_number}<br/><b>Date:</b> {order.created_at.strftime('%B %d, %Y')}<br/><b>Payment:</b> {order.get_payment_method_display()} ({order.payment_status})<br/><b>Tracking No:</b> {order.tracking_number}<br/><b>Status:</b> {order.order_status}", styles['Normal'])
        ]
    ]
    header_table = Table(header_data, colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # Items table
    items_data = [
        ["#", "Item Description", "Unit Price", "Qty", "Subtotal"]
    ]
    for idx, item in enumerate(order.items.all(), 1):
        items_data.append([
            str(idx),
            Paragraph(item.product_name, styles['Normal']),
            f"Rs. {item.price:.2f}",
            str(item.quantity),
            f"Rs. {item.total_price:.2f}"
        ])

    items_data.append(["", "", "", "Subtotal:", f"Rs. {order.subtotal:.2f}"])
    items_data.append(["", "", "", "Shipping:", f"Rs. {order.shipping_fee:.2f}"])
    items_data.append(["", "", "", "Grand Total:", f"Rs. {order.total_amount:.2f}"])

    items_table = Table(items_data, colWidths=[30, 260, 80, 50, 120])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, len(items_data) - 4), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEABOVE', (3, -3), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (3, -1), (-1, -1), colors.HexColor('#EFF6FF')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 25))

    # Footer note
    footer_text = Paragraph(
        "<i>Thank you for shopping with ShopSmart! For any questions regarding this order, please contact support@shopsmart.com.</i>",
        styles['Normal']
    )
    elements.append(footer_text)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_number}.pdf"'
    return response
