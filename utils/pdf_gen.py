import os
import textwrap
from datetime import datetime

def generate_invoice_pdf(invoice: dict) -> str:
    """Generate a lightweight PDF invoice using reportlab."""
    os.makedirs('static/invoices', exist_ok=True)
    pdf_path = f"static/invoices/SLV_{invoice['bill_number']}.pdf"

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                rightMargin=1.5*cm, leftMargin=1.5*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        story = []

        # Colors
        primary = colors.HexColor('#5D4037')
        accent = colors.HexColor('#8D6E63')
        light_bg = colors.HexColor('#FFF8F5')
        gold = colors.HexColor('#C8A97A')

        # Header
        title_style = ParagraphStyle('title', fontSize=22, textColor=primary,
                                      alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=2)
        sub_style = ParagraphStyle('sub', fontSize=10, textColor=accent,
                                    alignment=TA_CENTER, fontName='Helvetica', spaceAfter=2)
        normal_c = ParagraphStyle('nc', fontSize=9, textColor=colors.HexColor('#333333'),
                                   alignment=TA_CENTER, fontName='Helvetica')

        story.append(Paragraph("SLV TAILOR SHOP", title_style))
        story.append(Paragraph("KEMPANARASIMHAIAH", sub_style))
        story.append(Paragraph("Arasanakunte, Solur Hobli, Magadi Taluk, Bangalore - 562127", normal_c))
        story.append(Paragraph("📞 9535536981", normal_c))
        story.append(HRFlowable(width="100%", thickness=2, color=primary, spaceAfter=8))

        # Bill title
        bill_style = ParagraphStyle('bill', fontSize=14, textColor=primary,
                                     alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=6)
        story.append(Paragraph("INVOICE / RECEIPT", bill_style))

        # Bill info table
        bill_data = [
            ['Bill Number:', invoice.get('bill_number', ''),
             'Date:', invoice.get('created_at', '')[:10] if invoice.get('created_at') else ''],
            ['Booking Date:', invoice.get('booking_date', ''),
             'Delivery Date:', invoice.get('delivery_date', '')],
        ]
        bill_table = Table(bill_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        bill_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDCCBB')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(bill_table)
        story.append(Spacer(1, 8))

        # Customer details
        section_style = ParagraphStyle('section', fontSize=11, textColor=colors.white,
                                        fontName='Helvetica-Bold', spaceAfter=0, spaceBefore=0)
        cust_header = Table([['  CUSTOMER DETAILS']], colWidths=[17*cm])
        cust_header.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), primary),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(cust_header)

        cust_data = [
            ['Name:', invoice.get('customer_name', ''), 'Phone:', invoice.get('phone', '')],
            ['Age:', invoice.get('age', ''), 'Dress Type:', invoice.get('dress_type', '')],
            ['Address:', invoice.get('address', ''), '', ''],
        ]
        cust_table = Table(cust_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        cust_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDCCBB')),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFAF7')),
        ]))
        story.append(cust_table)
        story.append(Spacer(1, 6))

        # Measurements
        if invoice.get('measurements'):
            meas_header = Table([['  MEASUREMENTS']], colWidths=[17*cm])
            meas_header.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), accent),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(meas_header)
            meas_table = Table([[invoice.get('measurements', '')]], colWidths=[17*cm])
            meas_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDCCBB')),
                ('PADDING', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFAF7')),
            ]))
            story.append(meas_table)
            story.append(Spacer(1, 6))

        # Payment Summary
        pay_header = Table([['  PAYMENT SUMMARY']], colWidths=[17*cm])
        pay_header.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), primary),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(pay_header)

        adv = float(invoice.get('advance_amount') or 0)
        final = float(invoice.get('final_amount') or 0)
        balance = final - adv

        pay_data = [
            ['Total Amount:', f'Rs. {final:.2f}'],
            ['Advance Paid:', f'Rs. {adv:.2f}'],
            ['Balance Due:', f'Rs. {balance:.2f}'],
        ]
        pay_table = Table(pay_data, colWidths=[8.5*cm, 8.5*cm])
        pay_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDCCBB')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BACKGROUND', (0,0), (1,1), colors.HexColor('#FFFAF7')),
            ('BACKGROUND', (0,2), (1,2), colors.HexColor('#FFF0E8')),
            ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold'),
            ('TEXTCOLOR', (1,2), (1,2), primary),
        ]))
        story.append(pay_table)
        story.append(Spacer(1, 6))

        # Remarks
        if invoice.get('remarks'):
            story.append(Paragraph(f"<b>Remarks:</b> {invoice['remarks']}",
                                    ParagraphStyle('rem', fontSize=9, textColor=colors.HexColor('#555555'))))
            story.append(Spacer(1, 6))

        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=accent, spaceBefore=6, spaceAfter=4))
        footer_style = ParagraphStyle('footer', fontSize=8, textColor=colors.HexColor('#888888'),
                                       alignment=TA_CENTER, fontName='Helvetica')
        story.append(Paragraph("Thank you for choosing SLV Tailor Shop! We value your trust.", footer_style))
        story.append(Paragraph("This is a computer-generated invoice.", footer_style))

        doc.build(story)

    except ImportError:
        # Fallback: plain text PDF using basic approach
        with open(pdf_path.replace('.pdf', '.txt'), 'w') as f:
            f.write(f"SLV TAILOR SHOP\nKEMPANARASIMHAIAH\nArasanakunte, Solur Hobli, Magadi Taluk, Bangalore - 562127\nPhone: 9535536981\n\n")
            f.write(f"Bill Number: {invoice.get('bill_number')}\n")
            f.write(f"Customer: {invoice.get('customer_name')}\n")
            f.write(f"Phone: {invoice.get('phone')}\n")
            f.write(f"Total: Rs. {invoice.get('final_amount')}\n")
            f.write(f"Advance: Rs. {invoice.get('advance_amount')}\n")
            f.write(f"Balance: Rs. {invoice.get('balance_amount')}\n")
        pdf_path = pdf_path.replace('.pdf', '.txt')

    return pdf_path
