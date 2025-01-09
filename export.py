from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class ShoppingListExporter:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.styles = getSampleStyleSheet()
        
    def export_to_pdf(self, shopping_list_id, output_path):
        """Export shopping list to PDF"""
        try:
            # Get shopping list items
            items = self.db_manager.get_shopping_list_items(shopping_list_id)
            if not items:
                return False
                
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Prepare story (content)
            story = []
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            title = Paragraph("Shopping List", title_style)
            story.append(title)
            
            # Add date
            date_style = ParagraphStyle(
                'Date',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.gray
            )
            date = Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                date_style
            )
            story.append(date)
            story.append(Spacer(1, 20))
            
            # Prepare table data
            table_data = [['Item', 'Quantity', 'Store', 'Price']]
            total_price = 0
            
            for item in items:
                table_data.append([
                    item['name'],
                    str(item['quantity']),
                    item['store'],
                    f"€{item['price']:.2f}"
                ])
                total_price += item['price'] * item['quantity']
                
            # Add total row
            table_data.append(['', '', 'Total:', f"€{total_price:.2f}"])
            
            # Create table
            table = Table(table_data, colWidths=[200, 70, 100, 100])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ]))
            
            story.append(table)
            
            # Add savings information
            story.append(Spacer(1, 20))
            savings_style = ParagraphStyle(
                'Savings',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.green
            )
            savings = self.calculate_savings(items)
            savings_text = Paragraph(
                f"Potential savings: €{savings:.2f} by choosing the best prices",
                savings_style
            )
            story.append(savings_text)
            
            # Build PDF
            doc.build(story)
            return True
        except Exception as e:
            print(f"Error exporting to PDF: {e}")
            return False
            
    def calculate_savings(self, items):
        """Calculate potential savings by comparing with lowest prices"""
        total_savings = 0
        for item in items:
            # Get lowest price for this product across all stores
            lowest_price = self.db_manager.get_lowest_price(item['name'])
            if lowest_price and lowest_price < item['price']:
                total_savings += (item['price'] - lowest_price) * item['quantity']
        return total_savings
