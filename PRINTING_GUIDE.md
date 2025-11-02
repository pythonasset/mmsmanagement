# Printing Guide - Work Orders & Inspections

## Overview

The Maintenance Management System includes comprehensive printing functionality for work orders and inspection reports. You can generate professional PDF documents or print directly from your browser.

## Printing Methods

### Method 1: PDF Generation (Recommended)

**Best for:**
- Archival records
- Email distribution
- Professional documentation
- Offline storage

**How to use:**
1. Open a work order or inspection
2. Click the **🖨️ Print PDF** button
3. Click **📥 Download PDF** when it appears
4. Save the PDF to your desired location
5. Print from your PDF viewer (Adobe Reader, Chrome, etc.)

**Features:**
- Professional formatting with company branding
- Complete information included
- Signature lines (inspections)
- Timestamped generation date
- Optimized for A4/Letter paper

### Method 2: Browser Print

**Best for:**
- Quick printing
- One-click printing
- No file downloads needed

**How to use:**
1. Open a work order or inspection
2. Click the **🖨️ Browser Print** button
3. A new window opens with a print-friendly view
4. Your browser's print dialog appears automatically
5. Select your printer and print

**Note:** Make sure your browser allows pop-ups for this application.

## What Gets Printed

### Work Order Printout Includes:

**Header Section:**
- Company name and logo
- "WORK ORDER" title
- Document type identifier

**Work Order Details:**
- Work Order number
- Title
- Type
- Status
- Priority
- Created date
- Scheduled date (if set)
- Completed date (if completed)

**Asset Information:**
- Asset ID
- Asset name
- Asset type
- Location

**Description:**
- Full work order description

**Assignment & Scheduling:**
- Assigned technician/user
- Team assignment (if applicable)

**Cost Information:**
- Estimated cost
- Actual cost
- Labor hours

**Notes:**
- Additional notes
- Completion notes (if completed)

**Footer:**
- Generation timestamp
- Company name

### Inspection Report Includes:

**Header Section:**
- Company name and logo
- "INSPECTION REPORT" title
- Document type identifier

**Inspection Details:**
- Inspection number
- Type
- Date
- Inspector name
- Condition rating
- Defects found status

**Inspected Asset:**
- Asset ID
- Asset name
- Asset type
- Location

**Findings:**
- Inspection findings

**Defect Description:**
- Detailed defect information (if defects found)

**Recommendations:**
- Inspector recommendations

**Follow-up Information:**
- Follow-up required status
- Follow-up notes

**Signature Section:**
- Inspector signature line with date
- Supervisor signature line with date

**Footer:**
- Generation timestamp
- Company name

## Printing Best Practices

### PDF Printing

1. **Generate PDFs regularly**
   - Create PDFs for completed work orders
   - Generate inspection reports immediately after inspection
   - Store PDFs in organized folders

2. **File Naming**
   - PDFs are automatically named: `WorkOrder_[WO-NUMBER]_[DATE].pdf`
   - Or: `Inspection_[INSP-NUMBER]_[DATE].pdf`
   - Example: `WorkOrder_WO-00123_20241101.pdf`

3. **Storage**
   - Store PDFs in project folders
   - Archive completed work order PDFs
   - Keep inspection reports with asset files
   - Backup PDFs to cloud storage

### Browser Printing

1. **Check Pop-up Settings**
   - Allow pop-ups for the application URL
   - Chrome: Click the popup icon in address bar
   - Edge: Check site permissions

2. **Print Settings**
   - Use portrait orientation
   - Select A4 or Letter paper size
   - Margins: Default or 0.5 inch
   - Enable background graphics for better appearance

3. **Printer Selection**
   - Select appropriate printer
   - Check print preview before printing
   - Verify paper is loaded

## Customizing Print Output

### Company Branding

The printouts automatically include:
- Company name from `config.ini`
- Company icon/emoji
- Company information in footer

To customize:
1. Edit `config.ini`
2. Update company name, icon, and contact info
3. Restart application
4. New printouts will use updated information

### Currency Symbol

Currency values use the symbol from `config.ini`:
- Default: `$` (USD/AUD)
- Change in `config.ini`: `currency_symbol = £` (for GBP)
- Restart application for changes to take effect

## Field Worker Printing

### For Work Orders

**Recommended workflow:**

1. **Before Site Visit:**
   - Generate PDF of work order
   - Print copy for field worker
   - Worker takes printed copy to site

2. **At Site:**
   - Worker completes work following printed instructions
   - Worker notes actual costs and labor hours
   - Worker adds completion notes on paper

3. **After Site Visit:**
   - Worker returns with annotated printout
   - Office updates work order in system
   - Mark work order as complete
   - Generate final PDF for records

### For Inspections

**Recommended workflow:**

1. **Before Inspection:**
   - Print blank inspection form
   - Pre-filled with asset details

2. **During Inspection:**
   - Inspector completes form on-site
   - Records condition rating
   - Notes defects
   - Adds recommendations
   - Signs form

3. **After Inspection:**
   - Enter data into system
   - Generate final PDF
   - File in asset records

## Troubleshooting

### PDF Won't Download

**Possible causes:**
- Browser blocking downloads
- Pop-up blocker active
- PDF generation error

**Solutions:**
1. Check browser download settings
2. Allow downloads from this site
3. Try using Browser Print instead
4. Check error message in application
5. Refresh page and try again

### Browser Print Window Doesn't Open

**Possible causes:**
- Pop-up blocker enabled
- Browser security settings

**Solutions:**
1. Check for pop-up blocker icon in address bar
2. Click icon and allow pop-ups
3. In Chrome: Settings → Privacy → Pop-ups → Allow for this site
4. Try PDF printing method instead

### Missing Information in Printout

**Possible causes:**
- Data not entered in system
- Field left blank

**Solutions:**
1. Review work order/inspection details
2. Add missing information
3. Generate new printout
4. Ensure all required fields are completed

### Formatting Issues

**Possible causes:**
- Browser zoom level
- Print margins too small
- Wrong paper size selected

**Solutions:**
1. Set browser zoom to 100%
2. Use default print margins (0.5 inch)
3. Select correct paper size (A4 or Letter)
4. Check print preview before printing
5. Try PDF method for consistent formatting

### Printer Doesn't Print

**Possible causes:**
- Printer offline
- No paper
- Printer driver issues

**Solutions:**
1. Check printer is turned on
2. Verify paper is loaded
3. Check printer status in OS
4. Try printing test page
5. Save as PDF and print from PDF viewer

## Advanced Tips

### Batch Printing

To print multiple work orders:

1. Open each work order
2. Generate PDF for each
3. Download all PDFs
4. Use PDF software to print all at once

### Email Integration

To email work orders or inspections:

1. Generate PDF
2. Download PDF
3. Attach PDF to email
4. Send to recipient

Or alternatively:
- Copy the PDF to a shared drive
- Email link to shared drive location

### Archive Management

**Recommended archival structure:**

```
Documents/
├── WorkOrders/
│   ├── 2024/
│   │   ├── 01-January/
│   │   │   ├── WorkOrder_WO-00123_20240115.pdf
│   │   │   ├── WorkOrder_WO-00124_20240120.pdf
│   │   └── 02-February/
│   │       └── ...
│   └── 2025/
│       └── ...
└── Inspections/
    ├── 2024/
    │   ├── 01-January/
    │   └── ...
    └── 2025/
        └── ...
```

### Mobile Printing

If accessing from mobile device:

1. Generate PDF
2. Download to mobile device
3. Use mobile print service:
   - AirPrint (iOS)
   - Google Cloud Print
   - Printer manufacturer app

## Print Quality

### Recommended Settings

**For Work Orders:**
- Paper: A4 or Letter
- Orientation: Portrait
- Quality: Normal (300 DPI)
- Color: Black & White acceptable
- Double-sided: No

**For Inspection Reports:**
- Paper: A4 or Letter
- Orientation: Portrait
- Quality: Normal or High (300-600 DPI)
- Color: Black & White acceptable
- Double-sided: No

### Professional Printing

For formal documentation:

1. Use PDF generation method
2. Print on company letterhead (if applicable)
3. Use high-quality printer
4. Print in color for better clarity
5. Bind multi-page reports

## Signature Procedures

### For Inspection Reports

**Digital Workflow:**
1. Generate PDF
2. Print inspection report
3. Inspector signs physically
4. Supervisor signs
5. Scan signed copy
6. Store in digital archive

**Physical Workflow:**
1. Print inspection report
2. Inspector signs on-site
3. Supervisor signs in office
4. File in physical records
5. Keep digital PDF copy

## Integration with Records Management

### Filing Requirements

Check your organization's requirements:
- Retention period
- Storage location
- Format (digital/physical)
- Approval signatures needed

### Audit Trail

For audit purposes:
- PDF timestamp shows generation date
- Work order/inspection shows completion date
- Store both digital and physical copies
- Maintain complete history

## Support

For printing issues or questions:

- **Technical Support:** Check FAQ section
- **Email:** support@example.com
- **Documentation:** Refer to this guide

## Quick Reference

| Action | Location | Output |
|--------|----------|--------|
| Print Work Order PDF | Work Order Details → 🖨️ Print PDF | PDF file for download |
| Print Work Order (Browser) | Work Order Details → 🖨️ Browser Print | Opens print dialog |
| Print Inspection PDF | Inspection Details → 🖨️ Print PDF | PDF file for download |
| Print Inspection (Browser) | Inspection Details → 🖨️ Browser Print | Opens print dialog |

## Common Questions

**Q: Can I customize the PDF format?**
A: Company branding is customizable via `config.ini`. Layout customization requires code changes.

**Q: Can I print multiple work orders at once?**
A: Generate individual PDFs, then use PDF software to combine and print.

**Q: Are signatures legally binding?**
A: Physical signatures on printed copies may be required. Check local regulations.

**Q: Can I print without reportlab library?**
A: Browser print method works without additional libraries. PDF requires reportlab.

**Q: How do I add my company logo?**
A: Currently uses emoji icon from config. Logo integration requires customization.

---

**Last Updated:** November 2024

