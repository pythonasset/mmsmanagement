"""
Print Manager Module
Handles PDF generation and print-friendly formatting for work orders and inspections
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.colors import HexColor


class PrintManager:
    """Manager for printing and PDF generation"""
    
    def __init__(self, config):
        """Initialize print manager with configuration"""
        self.config = config
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#1f77b4'),
            spaceAfter=10,
            spaceBefore=15,
            borderWidth=0,
            borderPadding=5,
            borderColor=HexColor('#1f77b4'),
            borderRadius=None,
            backColor=HexColor('#f0f2f6')
        ))
        
        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            spaceAfter=8
        ))
    
    def generate_work_order_pdf(self, work_order, session):
        """
        Generate a PDF for a work order
        
        Args:
            work_order: WorkOrder database object
            session: Database session
        
        Returns:
            BytesIO: PDF file in memory
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Header with company info
        story.append(Paragraph(f"{self.config.APP_ICON} {self.config.COMPANY_NAME}", self.styles['CustomTitle']))
        story.append(Paragraph("WORK ORDER", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Work Order Information
        story.append(Paragraph("Work Order Details", self.styles['SectionHeader']))
        
        wo_data = [
            ['Work Order #:', work_order.work_order_number or 'N/A'],
            ['Title:', work_order.title or 'N/A'],
            ['Type:', work_order.work_type or 'N/A'],
            ['Status:', work_order.status or 'N/A'],
            ['Priority:', work_order.priority or 'N/A'],
            ['Created:', work_order.created_date.strftime('%d/%m/%Y %H:%M') if work_order.created_date else 'N/A'],
        ]
        
        if work_order.scheduled_date:
            wo_data.append(['Scheduled:', work_order.scheduled_date.strftime('%d/%m/%Y') if work_order.scheduled_date else 'N/A'])
        
        if work_order.completion_date:
            wo_data.append(['Completed:', work_order.completion_date.strftime('%d/%m/%Y %H:%M') if work_order.completion_date else 'N/A'])
        
        wo_table = Table(wo_data, colWidths=[2*inch, 4*inch])
        wo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(wo_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Asset Information
        if work_order.asset:
            story.append(Paragraph("Associated Asset", self.styles['SectionHeader']))
            
            asset_data = [
                ['Asset ID:', work_order.asset.asset_id or 'N/A'],
                ['Asset Name:', work_order.asset.name or 'N/A'],
                ['Asset Type:', work_order.asset.asset_type.name if work_order.asset.asset_type else 'N/A'],
                ['Location:', work_order.asset.address or 'N/A'],
            ]
            
            asset_table = Table(asset_data, colWidths=[2*inch, 4*inch])
            asset_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(asset_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Description
        if work_order.description:
            story.append(Paragraph("Description", self.styles['SectionHeader']))
            description_text = work_order.description.replace('\n', '<br/>')
            story.append(Paragraph(description_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Assignment Information
        story.append(Paragraph("Assignment & Scheduling", self.styles['SectionHeader']))
        
        assignment_data = []
        
        if work_order.assigned_to:
            assignment_data.append(['Assigned To:', work_order.assigned_to])
        else:
            assignment_data.append(['Assigned To:', 'Unassigned'])
        
        assignment_table = Table(assignment_data, colWidths=[2*inch, 4*inch])
        assignment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(assignment_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Cost Information
        story.append(Paragraph("Cost Information", self.styles['SectionHeader']))
        
        currency = self.config.CURRENCY_SYMBOL
        cost_data = [
            ['Estimated Cost:', f"{currency}{work_order.estimated_cost:.2f}" if work_order.estimated_cost else 'N/A'],
            ['Actual Cost:', f"{currency}{work_order.actual_cost:.2f}" if work_order.actual_cost else 'N/A'],
            ['Labor Hours:', f"{work_order.labor_hours:.1f}" if work_order.labor_hours else 'N/A'],
        ]
        
        cost_table = Table(cost_data, colWidths=[2*inch, 4*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(cost_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Notes
        if work_order.notes:
            story.append(Paragraph("Notes", self.styles['SectionHeader']))
            notes_text = work_order.notes.replace('\n', '<br/>')
            story.append(Paragraph(notes_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = f"Generated on {datetime.now().strftime('%d/%m/%Y %H:%M')} | {self.config.COMPANY_NAME}"
        story.append(Paragraph(footer_text, self.styles['InfoText']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_inspection_pdf(self, inspection, session):
        """
        Generate a PDF for an inspection
        
        Args:
            inspection: Inspection database object
            session: Database session
        
        Returns:
            BytesIO: PDF file in memory
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Header with company info
        story.append(Paragraph(f"{self.config.APP_ICON} {self.config.COMPANY_NAME}", self.styles['CustomTitle']))
        story.append(Paragraph("INSPECTION REPORT", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Inspection Information
        story.append(Paragraph("Inspection Details", self.styles['SectionHeader']))
        
        insp_data = [
            ['Inspection #:', inspection.inspection_number or 'N/A'],
            ['Type:', inspection.inspection_type or 'N/A'],
            ['Date:', inspection.inspection_date.strftime('%d/%m/%Y') if inspection.inspection_date else 'N/A'],
            ['Inspector:', inspection.inspector or 'N/A'],
            ['Condition Rating:', f"{inspection.condition_rating}/5" if inspection.condition_rating else 'N/A'],
            ['Defects Found:', 'Yes' if inspection.defects_found else 'No'],
        ]
        
        insp_table = Table(insp_data, colWidths=[2*inch, 4*inch])
        insp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(insp_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Asset Information
        if inspection.asset:
            story.append(Paragraph("Inspected Asset", self.styles['SectionHeader']))
            
            asset_data = [
                ['Asset ID:', inspection.asset.asset_id or 'N/A'],
                ['Asset Name:', inspection.asset.name or 'N/A'],
                ['Asset Type:', inspection.asset.asset_type.name if inspection.asset.asset_type else 'N/A'],
                ['Location:', inspection.asset.address or 'N/A'],
            ]
            
            asset_table = Table(asset_data, colWidths=[2*inch, 4*inch])
            asset_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(asset_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Defect Details
        if inspection.defects_found and inspection.defect_description:
            story.append(Paragraph("Defect Description", self.styles['SectionHeader']))
            defect_text = inspection.defect_description.replace('\n', '<br/>')
            story.append(Paragraph(defect_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if inspection.recommendations:
            story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
            recommendations_text = inspection.recommendations.replace('\n', '<br/>')
            story.append(Paragraph(recommendations_text, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Follow-up
        if inspection.follow_up_required:
            story.append(Paragraph("Follow-up Required", self.styles['SectionHeader']))
            
            followup_data = [
                ['Requires Follow-up:', 'Yes'],
            ]
            
            if inspection.follow_up_date:
                followup_data.append(['Follow-up Date:', inspection.follow_up_date.strftime('%d/%m/%Y') if inspection.follow_up_date else 'N/A'])
            
            followup_table = Table(followup_data, colWidths=[2*inch, 4*inch])
            followup_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(followup_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Signature section
        story.append(Spacer(1, 0.4*inch))
        story.append(Paragraph("Signatures", self.styles['SectionHeader']))
        
        sig_data = [
            ['Inspector Signature:', '_' * 40],
            ['Date:', '_' * 40],
            ['', ''],
            ['Supervisor Signature:', '_' * 40],
            ['Date:', '_' * 40],
        ]
        
        sig_table = Table(sig_data, colWidths=[2*inch, 4*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
            ('LINEBELOW', (1, 1), (1, 1), 1, colors.black),
            ('LINEBELOW', (1, 3), (1, 3), 1, colors.black),
            ('LINEBELOW', (1, 4), (1, 4), 1, colors.black),
        ]))
        story.append(sig_table)
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = f"Generated on {datetime.now().strftime('%d/%m/%Y %H:%M')} | {self.config.COMPANY_NAME}"
        story.append(Paragraph(footer_text, self.styles['InfoText']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_html_print_view(self, item_type, item, session):
        """
        Generate HTML for browser printing
        
        Args:
            item_type: 'work_order' or 'inspection'
            item: Database object
            session: Database session
        
        Returns:
            str: HTML string ready for printing
        """
        if item_type == 'work_order':
            return self._generate_work_order_html(item)
        elif item_type == 'inspection':
            return self._generate_inspection_html(item)
        else:
            return "<p>Invalid item type</p>"
    
    def _generate_work_order_html(self, work_order):
        """Generate HTML for work order printing"""
        currency = self.config.CURRENCY_SYMBOL
        
        html = f"""
        <html>
        <head>
            <title>Work Order - {work_order.work_order_number}</title>
            <style>
                @media print {{
                    body {{ margin: 0.5in; }}
                    .no-print {{ display: none; }}
                }}
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 8.5in;
                    margin: auto;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #1f77b4;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    color: #1f77b4;
                    margin: 5px 0;
                }}
                .header h2 {{
                    color: #333;
                    margin: 5px 0;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .section-title {{
                    background-color: #f0f2f6;
                    padding: 8px;
                    font-weight: bold;
                    color: #1f77b4;
                    border-left: 4px solid #1f77b4;
                    margin-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }}
                table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                }}
                table td:first-child {{
                    font-weight: bold;
                    background-color: #f5f5f5;
                    width: 30%;
                }}
                .description-box {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    background-color: #f9f9f9;
                    white-space: pre-wrap;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.config.APP_ICON} {self.config.COMPANY_NAME}</h1>
                <h2>WORK ORDER</h2>
            </div>
            
            <div class="section">
                <div class="section-title">Work Order Details</div>
                <table>
                    <tr>
                        <td>Work Order #:</td>
                        <td>{work_order.work_order_number or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Title:</td>
                        <td>{work_order.title or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Type:</td>
                        <td>{work_order.work_type or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Status:</td>
                        <td><strong>{work_order.status or 'N/A'}</strong></td>
                    </tr>
                    <tr>
                        <td>Priority:</td>
                        <td><strong>{work_order.priority or 'N/A'}</strong></td>
                    </tr>
                    <tr>
                        <td>Created:</td>
                        <td>{work_order.created_date.strftime('%d/%m/%Y %H:%M') if work_order.created_date else 'N/A'}</td>
                    </tr>
"""
        
        if work_order.scheduled_date:
            html += f"""
                    <tr>
                        <td>Scheduled:</td>
                        <td>{work_order.scheduled_date.strftime('%d/%m/%Y') if work_order.scheduled_date else 'N/A'}</td>
                    </tr>
"""
        
        if work_order.completion_date:
            html += f"""
                    <tr>
                        <td>Completed:</td>
                        <td>{work_order.completion_date.strftime('%d/%m/%Y %H:%M') if work_order.completion_date else 'N/A'}</td>
                    </tr>
"""
        
        html += """
                </table>
            </div>
"""
        
        # Asset Information
        if work_order.asset:
            html += f"""
            <div class="section">
                <div class="section-title">Associated Asset</div>
                <table>
                    <tr>
                        <td>Asset ID:</td>
                        <td>{work_order.asset.asset_id or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Asset Name:</td>
                        <td>{work_order.asset.name or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Asset Type:</td>
                        <td>{work_order.asset.asset_type.name if work_order.asset.asset_type else 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Location:</td>
                        <td>{work_order.asset.address or 'N/A'}</td>
                    </tr>
                </table>
            </div>
"""
        
        # Description
        if work_order.description:
            html += f"""
            <div class="section">
                <div class="section-title">Description</div>
                <div class="description-box">{work_order.description}</div>
            </div>
"""
        
        # Assignment
        html += """
            <div class="section">
                <div class="section-title">Assignment & Scheduling</div>
                <table>
"""
        
        if work_order.assigned_to:
            html += f"""
                    <tr>
                        <td>Assigned To:</td>
                        <td>{work_order.assigned_to}</td>
                    </tr>
"""
        else:
            html += """
                    <tr>
                        <td>Assigned To:</td>
                        <td>Unassigned</td>
                    </tr>
"""
        
        html += """
                </table>
            </div>
"""
        
        # Cost Information
        html += f"""
            <div class="section">
                <div class="section-title">Cost Information</div>
                <table>
                    <tr>
                        <td>Estimated Cost:</td>
                        <td>{f'{currency}{work_order.estimated_cost:.2f}' if work_order.estimated_cost else 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Actual Cost:</td>
                        <td>{f'{currency}{work_order.actual_cost:.2f}' if work_order.actual_cost else 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Labor Hours:</td>
                        <td>{f'{work_order.labor_hours:.1f}' if work_order.labor_hours else 'N/A'}</td>
                    </tr>
                </table>
            </div>
"""
        
        # Notes
        if work_order.notes:
            html += f"""
            <div class="section">
                <div class="section-title">Notes</div>
                <div class="description-box">{work_order.notes}</div>
            </div>
"""
        
        html += f"""
            <div class="footer">
                Generated on {datetime.now().strftime('%d/%m/%Y %H:%M')} | {self.config.COMPANY_NAME}
            </div>
        </body>
        </html>
"""
        
        return html
    
    def _generate_inspection_html(self, inspection):
        """Generate HTML for inspection printing"""
        html = f"""
        <html>
        <head>
            <title>Inspection Report - {inspection.inspection_number}</title>
            <style>
                @media print {{
                    body {{ margin: 0.5in; }}
                    .no-print {{ display: none; }}
                }}
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 8.5in;
                    margin: auto;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 3px solid #1f77b4;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    color: #1f77b4;
                    margin: 5px 0;
                }}
                .header h2 {{
                    color: #333;
                    margin: 5px 0;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .section-title {{
                    background-color: #f0f2f6;
                    padding: 8px;
                    font-weight: bold;
                    color: #1f77b4;
                    border-left: 4px solid #1f77b4;
                    margin-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }}
                table td {{
                    padding: 8px;
                    border: 1px solid #ddd;
                }}
                table td:first-child {{
                    font-weight: bold;
                    background-color: #f5f5f5;
                    width: 30%;
                }}
                .description-box {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    background-color: #f9f9f9;
                    white-space: pre-wrap;
                }}
                .signature-line {{
                    border-bottom: 1px solid #000;
                    margin-top: 30px;
                    padding-top: 40px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px solid #ddd;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.config.APP_ICON} {self.config.COMPANY_NAME}</h1>
                <h2>INSPECTION REPORT</h2>
            </div>
            
            <div class="section">
                <div class="section-title">Inspection Details</div>
                <table>
                    <tr>
                        <td>Inspection #:</td>
                        <td>{inspection.inspection_number or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Type:</td>
                        <td>{inspection.inspection_type or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Date:</td>
                        <td>{inspection.inspection_date.strftime('%d/%m/%Y') if inspection.inspection_date else 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Inspector:</td>
                        <td>{inspection.inspector or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Condition Rating:</td>
                        <td><strong>{f'{inspection.condition_rating}/5' if inspection.condition_rating else 'N/A'}</strong></td>
                    </tr>
                    <tr>
                        <td>Defects Found:</td>
                        <td><strong>{'Yes' if inspection.defects_found else 'No'}</strong></td>
                    </tr>
                </table>
            </div>
"""
        
        # Asset Information
        if inspection.asset:
            html += f"""
            <div class="section">
                <div class="section-title">Inspected Asset</div>
                <table>
                    <tr>
                        <td>Asset ID:</td>
                        <td>{inspection.asset.asset_id or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Asset Name:</td>
                        <td>{inspection.asset.name or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Asset Type:</td>
                        <td>{inspection.asset.asset_type.name if inspection.asset.asset_type else 'N/A'}</td>
                    </tr>
                    <tr>
                        <td>Location:</td>
                        <td>{inspection.asset.address or 'N/A'}</td>
                    </tr>
                </table>
            </div>
"""
        
        # Defect Details
        if inspection.defects_found and inspection.defect_description:
            html += f"""
            <div class="section">
                <div class="section-title">Defect Description</div>
                <div class="description-box">{inspection.defect_description}</div>
            </div>
"""
        
        # Recommendations
        if inspection.recommendations:
            html += f"""
            <div class="section">
                <div class="section-title">Recommendations</div>
                <div class="description-box">{inspection.recommendations}</div>
            </div>
"""
        
        # Follow-up
        if inspection.follow_up_required:
            html += """
            <div class="section">
                <div class="section-title">Follow-up Required</div>
                <table>
                    <tr>
                        <td>Requires Follow-up:</td>
                        <td><strong>Yes</strong></td>
                    </tr>
"""
            
            if inspection.follow_up_date:
                html += f"""
                    <tr>
                        <td>Follow-up Date:</td>
                        <td>{inspection.follow_up_date.strftime('%d/%m/%Y') if inspection.follow_up_date else 'N/A'}</td>
                    </tr>
"""
            
            html += """
                </table>
            </div>
"""
        
        # Signature Section
        html += """
            <div class="section">
                <div class="section-title">Signatures</div>
                <div style="margin-top: 40px;">
                    <div style="display: inline-block; width: 48%; vertical-align: top;">
                        <div style="margin-bottom: 50px;">Inspector Signature:</div>
                        <div class="signature-line"></div>
                        <div style="margin-top: 5px;">Date: ________________</div>
                    </div>
                    <div style="display: inline-block; width: 48%; vertical-align: top; margin-left: 4%;">
                        <div style="margin-bottom: 50px;">Supervisor Signature:</div>
                        <div class="signature-line"></div>
                        <div style="margin-top: 5px;">Date: ________________</div>
                    </div>
                </div>
            </div>
"""
        
        html += f"""
            <div class="footer">
                Generated on {datetime.now().strftime('%d/%m/%Y %H:%M')} | {self.config.COMPANY_NAME}
            </div>
        </body>
        </html>
"""
        
        return html

