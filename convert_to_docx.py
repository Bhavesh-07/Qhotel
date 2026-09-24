import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    # values in dxa (1 pt = 20 dxa)
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_borders(cell, top="none", bottom="none", left="none", right="none", 
                     color="CBD5E1", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for border_name, border_val in borders.items():
        if border_val != "none":
            b = OxmlElement(f'w:{border_name}')
            b.set(qn('w:val'), border_val)
            b.set(qn('w:sz'), sz)
            b.set(qn('w:space'), '0')
            b.set(qn('w:color'), color)
            tcBorders.append(b)
        else:
            b = OxmlElement(f'w:{border_name}')
            b.set(qn('w:val'), 'none')
            tcBorders.append(b)
    tcPr.append(tcBorders)

def add_header_footer(doc):
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Security & Privacy Risk Remediation Plan  |  qhotels.co")
        hrun.font.name = 'Segoe UI'
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        # Footer
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        frun1 = fp.add_run("Confidential  •  Generated from Risk Assessment Report")
        frun1.font.name = 'Segoe UI'
        frun1.font.size = Pt(8.5)
        frun1.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

def format_run(run, font_name='Segoe UI', size_pt=10, bold=False, italic=False, color_rgb=(0x33, 0x41, 0x55)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def add_callout_box(doc, title, text, border_color="0284C7", bg_color="F0F9FF", title_color=(0x03, 0x69, 0xA1)):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(7.0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    set_cell_borders(cell, left="single", color=border_color, sz="24", top="none", bottom="none", right="none")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    
    if title:
        r_title = p.add_run(title + "\n")
        format_run(r_title, font_name='Segoe UI', size_pt=10, bold=True, color_rgb=title_color)
    
    r_body = p.add_run(text)
    format_run(r_body, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
    
    # spacing
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_problem_box(doc, problem_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(7.0)
    set_cell_background(cell, "FFF7ED") # soft amber/orange
    set_cell_margins(cell, top=100, bottom=100, left=160, right=160)
    set_cell_borders(cell, left="single", color="F97316", sz="20", top="none", bottom="none", right="none")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    
    r_lbl = p.add_run("⚠️ Problem Identified: ")
    format_run(r_lbl, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0xC2, 0x41, 0x0C))
    
    r_body = p.add_run(problem_text)
    format_run(r_body, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x43, 0x14, 0x07))
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(7.0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    set_cell_borders(cell, left="single", color="3B82F6", sz="18", 
                     top="single", bottom="single", right="single")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    
    r = p.add_run(code_text)
    format_run(r, font_name='Consolas', size_pt=9.0, bold=False, color_rgb=(0x0F, 0x17, 0x2A))
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)

def build_word_document():
    doc = docx.Document()
    add_header_footer(doc)
    
    # Configure Normal Style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Segoe UI'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
    
    # --- Title Section ---
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("Security & Privacy Risk Remediation Action Plan")
    format_run(r_title, font_name='Segoe UI', size_pt=20, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    # Meta / Info Bar Table
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    
    col_w = [Inches(3.5), Inches(3.5)]
    meta_data = [
        [("Target Asset:", " qhotels.co & associated infrastructure"), ("Source Assessment:", " risk_findings_2026-09-18_16-24-13.xlsx")],
        [("Responsible Teams:", " DevOps, Web Developers, Legal/Compliance"), ("Plan Status:", " Prioritized & Actionable Checklist")]
    ]
    
    for r_idx, row in enumerate(meta_table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_w[c_idx]
            set_cell_background(cell, "F1F5F9")
            set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
            set_cell_borders(cell, top="none", bottom="none", left="none", right="none")
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            lbl, val = meta_data[r_idx][c_idx]
            
            r_l = p.add_run(lbl)
            format_run(r_l, font_name='Segoe UI', size_pt=8.5, bold=True, color_rgb=(0x47, 0x55, 0x69))
            r_v = p.add_run(val)
            format_run(r_v, font_name='Segoe UI', size_pt=8.5, bold=False, color_rgb=(0x1E, 0x29, 0x3B))
    
    # Spacing after meta
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(6)
    sp.paragraph_format.space_after = Pt(4)
    
    # Overview Callout
    intro_text = (
        "This document breaks down all 11 security and privacy findings identified in the automated risk assessment "
        "scan for qhotels.co and associated network assets (13.65.148.90, 144.76.101.11, innrly.com, etc.).\n\n"
        "It provides a prioritized, step-by-step checklist of concrete remediation actions categorized by operational domain: "
        "Server/Infrastructure Administration, Web Development, and Compliance/Legal."
    )
    add_callout_box(doc, "📋 Executive Context & Objective", intro_text, border_color="0284C7", bg_color="F0F9FF")
    
    # --- Section 1: Executive Summary of Findings ---
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("1. Executive Summary of Findings")
    format_run(r_h1, font_name='Segoe UI', size_pt=14, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    p_summary = doc.add_paragraph()
    p_summary.paragraph_format.space_before = Pt(0)
    p_summary.paragraph_format.space_after = Pt(8)
    r_sum = p_summary.add_run("The risk scan identified ")
    format_run(r_sum, font_name='Segoe UI', size_pt=10, bold=False)
    r_sum_bold = p_summary.add_run("11 total findings")
    format_run(r_sum_bold, font_name='Segoe UI', size_pt=10, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    r_sum2 = p_summary.add_run(" distributed across 4 core risk categories:")
    format_run(r_sum2, font_name='Segoe UI', size_pt=10, bold=False)
    
    # Table of Findings
    table_findings = doc.add_table(rows=12, cols=5)
    table_findings.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_findings.autofit = False
    
    col_widths = [Inches(1.0), Inches(1.3), Inches(1.7), Inches(1.6), Inches(1.4)]
    headers = ["Priority", "Category", "Finding Name", "Affected Asset(s)", "Responsible Role"]
    
    # Style Header Row
    hdr_cells = table_findings.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "1E3A8A") # Navy
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=120, right=120)
        set_cell_borders(hdr_cells[i], top="single", bottom="single", left="none", right="none", color="1E3A8A", sz="8")
        
        p = hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        format_run(r, font_name='Segoe UI', size_pt=9.0, bold=True, color_rgb=(0xFF, 0xFF, 0xFF))
        if i == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    findings_data = [
        ("🔴 High", "Privacy / Tracking", "Risky Tracking Technology", "qhotels.co", "Web Developer"),
        ("🟡 Medium", "Database Exposure", "Microsoft SQL Service Exposed", "13.65.148.90 (Port 1433)", "Infrastructure / DevOps"),
        ("🟡 Medium", "Database Exposure", "MySQL Service Exposed", "144.76.101.11 (Port 3306)", "Infrastructure / DevOps"),
        ("🟡 Medium", "Cleartext Protocol", "FTP Service without SSL/TLS (7 hosts)", "13.65.148.90, qhotels.co, innrly.com", "Infrastructure / DevOps"),
        ("🟡 Medium", "Cleartext Protocol", "HTTP Service without SSL/TLS (14 hosts)", "qhotels.co, innrly.com subdomains", "Infrastructure / DevOps"),
        ("🟡 Medium", "Privacy / Consent", "No Cookie Banner Detected", "qhotels.co", "Web Developer"),
        ("🟡 Medium", "Privacy / Consent", "Non-necessary Cookies Instantly Fire", "qhotels.co", "Web Developer"),
        ("🟡 Medium", "Privacy / GPC", "No Global Privacy Control (GPC)", "qhotels.co", "Web Developer"),
        ("🟡 Medium", "Privacy / GPC", "Website May Ignore GPC Header", "qhotels.co", "Web Developer"),
        ("🟡 Medium", "Privacy / Legal", "Missing \"Do Not Sell My Info\" Link", "qhotels.co", "Web Developer / Legal"),
        ("🟡 Medium", "Privacy / Legal", "Privacy Policy Older than 12 Months", "qhotels.co", "Legal / Web Developer")
    ]
    
    for row_idx, data in enumerate(findings_data, start=1):
        row_cells = table_findings.rows[row_idx].cells
        bg_fill = "FFFFFF" if row_idx % 2 != 0 else "F8FAFC"
        
        for c_idx in range(5):
            row_cells[c_idx].width = col_widths[c_idx]
            set_cell_background(row_cells[c_idx], bg_fill)
            set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=120, right=120)
            set_cell_borders(row_cells[c_idx], top="single", bottom="single", left="none", right="none", color="E2E8F0", sz="4")
            
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            
            val = data[c_idx]
            if c_idx == 0: # Priority
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(val)
                if "High" in val:
                    format_run(r, font_name='Segoe UI', size_pt=8.5, bold=True, color_rgb=(0xDC, 0x26, 0x26))
                else:
                    format_run(r, font_name='Segoe UI', size_pt=8.5, bold=True, color_rgb=(0xD9, 0x77, 0x06))
            elif c_idx == 2: # Finding name
                r = p.add_run(val)
                format_run(r, font_name='Segoe UI', size_pt=8.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
            else:
                r = p.add_run(val)
                format_run(r, font_name='Segoe UI', size_pt=8.5, bold=False, color_rgb=(0x47, 0x55, 0x69))
    
    # Spacing
    sp2 = doc.add_paragraph()
    sp2.paragraph_format.space_before = Pt(10)
    sp2.paragraph_format.space_after = Pt(4)
    
    # --- Section 2: Detailed Action Plan by Domain ---
    h1_2 = doc.add_paragraph()
    h1_2.paragraph_format.space_before = Pt(16)
    h1_2.paragraph_format.space_after = Pt(4)
    r_h1_2 = h1_2.add_run("2. Detailed Action Plan by Domain")
    format_run(r_h1_2, font_name='Segoe UI', size_pt=14, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    # Phase 1 Header
    h2_p1 = doc.add_paragraph()
    h2_p1.paragraph_format.space_before = Pt(12)
    h2_p1.paragraph_format.space_after = Pt(4)
    r_h2_p1 = h2_p1.add_run("Phase 1: Infrastructure & Network Security (DevOps / Server Admin)")
    format_run(r_h2_p1, font_name='Segoe UI', size_pt=12, bold=True, color_rgb=(0x1E, 0x3A, 0x8A))
    
    # 1.1
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(2)
    r = h3.add_run("1.1 Close Public Database Ports (MS SQL & MySQL)")
    format_run(r, font_name='Segoe UI', size_pt=11, bold=True, color_rgb=(0x33, 0x41, 0x55))
    
    add_problem_box(doc, "Database ports 1433 (MS SQL on 13.65.148.90) and 3306 (MySQL on 144.76.101.11) are reachable over the public internet. This exposes internal databases to brute force, automated credential stuffing, and remote exploit vectors.")
    
    p_act = doc.add_paragraph()
    p_act.paragraph_format.space_before = Pt(2)
    p_act.paragraph_format.space_after = Pt(2)
    r_act = p_act.add_run("Action Required:")
    format_run(r_act, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    steps_1_1 = [
        "In Windows Firewall and cloud security groups (AWS/Azure/Hetzner), block public inbound traffic on port 1433 and port 3306.",
        "If remote administration is required, mandate connection via VPN or restrict access strictly to whitelisted static office/server IP addresses.",
        "Ensure database service listening binding is set to localhost (127.0.0.1 / bind-address = 127.0.0.1) for local-only database instances."
    ]
    for i, s in enumerate(steps_1_1, start=1):
        p_step = doc.add_paragraph()
        p_step.paragraph_format.left_indent = Inches(0.25)
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(2)
        r_num = p_step.add_run(f"{i}. ")
        format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
        r_txt = p_step.add_run(s)
        format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
    
    # 1.2
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(2)
    r = h3.add_run("1.2 Disable Plain FTP & Enforce SFTP / FTPS")
    format_run(r, font_name='Segoe UI', size_pt=11, bold=True, color_rgb=(0x33, 0x41, 0x55))
    
    add_problem_box(doc, "Plain FTP (Port 21) transmits administrative credentials, user authentication tokens, and website files across the network in unencrypted cleartext.")
    
    p_act = doc.add_paragraph()
    p_act.paragraph_format.space_before = Pt(2)
    p_act.paragraph_format.space_after = Pt(2)
    r_act = p_act.add_run("Action Required:")
    format_run(r_act, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    steps_1_2 = [
        "Disable standard unencrypted FTP services on 13.65.148.90, qhotels.co, and innrly.com servers.",
        "Transition all file transfer workflows to SFTP (SSH File Transfer Protocol on Port 22) or FTPS (FTP over TLS/SSL with explicit encryption enforced)."
    ]
    for i, s in enumerate(steps_1_2, start=1):
        p_step = doc.add_paragraph()
        p_step.paragraph_format.left_indent = Inches(0.25)
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(2)
        r_num = p_step.add_run(f"{i}. ")
        format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
        r_txt = p_step.add_run(s)
        format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
        
    # 1.3
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(2)
    r = h3.add_run("1.3 Enforce HTTPS & HTTP-to-HTTPS Redirection Across All Domains")
    format_run(r, font_name='Segoe UI', size_pt=11, bold=True, color_rgb=(0x33, 0x41, 0x55))
    
    add_problem_box(doc, "14 hostnames accept unencrypted plain HTTP (Port 80) connections without strictly enforcing encryption.")
    
    p_act = doc.add_paragraph()
    p_act.paragraph_format.space_before = Pt(2)
    p_act.paragraph_format.space_after = Pt(2)
    r_act = p_act.add_run("Action Required:")
    format_run(r_act, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    steps_1_3 = [
        "In IIS (or edge reverse proxy / Cloudflare), configure an automatic HTTP to HTTPS 301 Permanent Redirect for all incoming requests.",
        "Add the HSTS (HTTP Strict Transport Security) header in IIS web.config to mandate encrypted communication browser-side:",
    ]
    for i, s in enumerate(steps_1_3, start=1):
        p_step = doc.add_paragraph()
        p_step.paragraph_format.left_indent = Inches(0.25)
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(2)
        r_num = p_step.add_run(f"{i}. ")
        format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
        r_txt = p_step.add_run(s)
        format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
    
    # Code block for IIS HSTS
    xml_code = (
        '<httpProtocol>\n'
        '  <customHeaders>\n'
        '    <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains; preload" />\n'
        '  </customHeaders>\n'
        '</httpProtocol>'
    )
    add_code_block(doc, xml_code)
    
    p_step3 = doc.add_paragraph()
    p_step3.paragraph_format.left_indent = Inches(0.25)
    p_step3.paragraph_format.space_before = Pt(1)
    p_step3.paragraph_format.space_after = Pt(4)
    r_num = p_step3.add_run("3. ")
    format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
    r_txt = p_step3.add_run("Ensure valid SSL/TLS certificates (e.g. Let's Encrypt / DigiCert) are installed and auto-renewing on all active subdomains.")
    format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
    
    # Phase 2 Header
    h2_p2 = doc.add_paragraph()
    h2_p2.paragraph_format.space_before = Pt(14)
    h2_p2.paragraph_format.space_after = Pt(4)
    r_h2_p2 = h2_p2.add_run("Phase 2: Web Privacy, Cookie Consent & GPC Compliance (Frontend / Web Developer)")
    format_run(r_h2_p2, font_name='Segoe UI', size_pt=12, bold=True, color_rgb=(0x1E, 0x3A, 0x8A))
    
    # 2.1
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(2)
    r = h3.add_run("2.1 Implement a Consent Management Platform (CMP) & Cookie Banner")
    format_run(r, font_name='Segoe UI', size_pt=11, bold=True, color_rgb=(0x33, 0x41, 0x55))
    
    add_problem_box(doc, "Tracking cookies and Google Analytics scripts fire immediately upon page load prior to visitors having an opportunity to accept, reject, or customize tracking preferences.")
    
    p_act = doc.add_paragraph()
    p_act.paragraph_format.space_before = Pt(2)
    p_act.paragraph_format.space_after = Pt(2)
    r_act = p_act.add_run("Action Required:")
    format_run(r_act, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    steps_2_1 = [
        "Deploy a compliant Consent Management Platform (such as Cookiebot, OneTrust, Termly, or a custom GDPR/CCPA-compliant modal).",
        "Configure the CMP to block non-essential scripts (Google Analytics gtag.js, marketing pixels) until the visitor explicitly clicks \"Accept\" or configures cookie preferences.",
        "Upgrade Google Analytics tags to GA4 (G-XXXXXXXXXX) and enforce Google Consent Mode v2 (analytics_storage: 'denied' by default until consent is granted)."
    ]
    for i, s in enumerate(steps_2_1, start=1):
        p_step = doc.add_paragraph()
        p_step.paragraph_format.left_indent = Inches(0.25)
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(2)
        r_num = p_step.add_run(f"{i}. ")
        format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
        r_txt = p_step.add_run(s)
        format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
        
    # 2.2
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(2)
    r = h3.add_run("2.2 Honor Global Privacy Control (GPC) Signals")
    format_run(r, font_name='Segoe UI', size_pt=11, bold=True, color_rgb=(0x33, 0x41, 0x55))
    
    add_problem_box(doc, "When a visitor's browser transmits the Sec-GPC: 1 HTTP header or sets navigator.globalPrivacyControl = true, third-party analytics and marketing scripts continue to load unchanged.")
    
    p_act = doc.add_paragraph()
    p_act.paragraph_format.space_before = Pt(2)
    p_act.paragraph_format.space_after = Pt(2)
    r_act = p_act.add_run("Action Required:")
    format_run(r_act, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    steps_2_2 = [
        "Ensure the cookie consent platform automatically listens for and detects navigator.globalPrivacyControl.",
        "If GPC is evaluated as true, automatically treat it as an opt-out: suppress non-essential tracking cookies and mark analytics tracking as rejected without requiring manual interaction."
    ]
    for i, s in enumerate(steps_2_2, start=1):
        p_step = doc.add_paragraph()
        p_step.paragraph_format.left_indent = Inches(0.25)
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(2)
        r_num = p_step.add_run(f"{i}. ")
        format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
        r_txt = p_step.add_run(s)
        format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))

    # 2.3
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(2)
    r = h3.add_run("2.3 Add \"Do Not Sell or Share My Personal Information\" Link")
    format_run(r, font_name='Segoe UI', size_pt=11, bold=True, color_rgb=(0x33, 0x41, 0x55))
    
    add_problem_box(doc, "Under CCPA/CPRA, websites collecting visitor data must provide a clear, conspicuous opt-out mechanism accessible on the homepage and across all site footers.")
    
    p_act = doc.add_paragraph()
    p_act.paragraph_format.space_before = Pt(2)
    p_act.paragraph_format.space_after = Pt(2)
    r_act = p_act.add_run("Action Required:")
    format_run(r_act, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    steps_2_3 = [
        "Add a prominent \"Do Not Sell or Share My Personal Information\" link to the website footer in templates/base.html.",
        "Link it either to a privacy preference center modal (re-triggering the CMP banner to manage opt-outs) or directly to privacy policy opt-out procedures.",
        "Note: If the organization qualifies for an exemption under CCPA thresholds, document the formal business justification as an \"Accepted Risk\" in compliance archives."
    ]
    for i, s in enumerate(steps_2_3, start=1):
        p_step = doc.add_paragraph()
        p_step.paragraph_format.left_indent = Inches(0.25)
        p_step.paragraph_format.space_before = Pt(1)
        p_step.paragraph_format.space_after = Pt(2)
        r_num = p_step.add_run(f"{i}. ")
        format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
        r_txt = p_step.add_run(s)
        format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))

    # Phase 3 Header
    h2_p3 = doc.add_paragraph()
    h2_p3.paragraph_format.space_before = Pt(14)
    h2_p3.paragraph_format.space_after = Pt(4)
    r_h2_p3 = h2_p3.add_run("Phase 3: Legal & Policy Updates (Legal & Content Team)")
    format_run(r_h2_p3, font_name='Segoe UI', size_pt=12, bold=True, color_rgb=(0x1E, 0x3A, 0x8A))
    
    # 3.1
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(2)
    r = h3.add_run("3.1 Privacy Policy Annual Refresh")
    format_run(r, font_name='Segoe UI', size_pt=11, bold=True, color_rgb=(0x33, 0x41, 0x55))
    
    add_problem_box(doc, "The website's privacy policy was last updated over 12 months ago. Major privacy regulations (CCPA/CPRA, GDPR) mandate regular annual reviews and up-to-date disclosure disclosures.")
    
    p_act = doc.add_paragraph()
    p_act.paragraph_format.space_before = Pt(2)
    p_act.paragraph_format.space_after = Pt(2)
    r_act = p_act.add_run("Action Required:")
    format_run(r_act, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    p_step = doc.add_paragraph()
    p_step.paragraph_format.left_indent = Inches(0.25)
    p_step.paragraph_format.space_before = Pt(1)
    p_step.paragraph_format.space_after = Pt(2)
    r_num = p_step.add_run("1. ")
    format_run(r_num, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
    r_txt = p_step.add_run("Review templates/privacy-policy.html and update the \"Effective Date / Last Updated\" to the current year/month.")
    format_run(r_txt, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
    
    p_step2 = doc.add_paragraph()
    p_step2.paragraph_format.left_indent = Inches(0.25)
    p_step2.paragraph_format.space_before = Pt(1)
    p_step2.paragraph_format.space_after = Pt(2)
    r_num2 = p_step2.add_run("2. ")
    format_run(r_num2, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
    r_txt2 = p_step2.add_run("Ensure the revised policy explicitly outlines the following requirements:")
    format_run(r_txt2, font_name='Segoe UI', size_pt=9.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
    
    policy_subitems = [
        "Categories of personal data collected (e.g., contact inquiry forms, server logs, analytics identifiers).",
        "Clear opt-out instructions and how Global Privacy Control (GPC) signals are recognized and honored.",
        "Consumer privacy rights (Right to Know, Delete, Correct, and Opt-Out of Data Sharing/Sale).",
        "Dedicated contact email address for privacy inquiries and data subject access requests (e.g., info@qhotels.co)."
    ]
    for sub in policy_subitems:
        p_sub = doc.add_paragraph()
        p_sub.paragraph_format.left_indent = Inches(0.5)
        p_sub.paragraph_format.space_before = Pt(1)
        p_sub.paragraph_format.space_after = Pt(2)
        r_bullet = p_sub.add_run("• ")
        format_run(r_bullet, font_name='Segoe UI', size_pt=9.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
        r_subtxt = p_sub.add_run(sub)
        format_run(r_subtxt, font_name='Segoe UI', size_pt=9.0, bold=False, color_rgb=(0x47, 0x55, 0x69))

    # --- Section 3: Action Checklist & Resolution Tracking ---
    h1_3 = doc.add_paragraph()
    h1_3.paragraph_format.space_before = Pt(16)
    h1_3.paragraph_format.space_after = Pt(4)
    r_h1_3 = h1_3.add_run("3. Action Checklist & Resolution Tracking")
    format_run(r_h1_3, font_name='Segoe UI', size_pt=14, bold=True, color_rgb=(0x0F, 0x17, 0x2A))
    
    p_check_intro = doc.add_paragraph()
    p_check_intro.paragraph_format.space_before = Pt(0)
    p_check_intro.paragraph_format.space_after = Pt(6)
    r_ci = p_check_intro.add_run("Use this checklist to record implementation progress and track sign-off for each remediation item:")
    format_run(r_ci, font_name='Segoe UI', size_pt=10, bold=False, color_rgb=(0x33, 0x41, 0x55))
    
    checklist_data = [
        ("Pending", "Firewall", "Close public access to MS SQL (Port 1433 on 13.65.148.90)", "DevOps / Infrastructure"),
        ("Pending", "Firewall", "Close public access to MySQL (Port 3306 on 144.76.101.11)", "DevOps / Infrastructure"),
        ("Pending", "Network", "Disable plain FTP (Port 21) across all hosts; enforce SFTP / FTPS", "DevOps / Infrastructure"),
        ("Done", "Web Server", "Configure 301 HTTP -> HTTPS redirection on all endpoints (Added in web.config)", "DevOps / Web Admin"),
        ("Done", "Web Server", "Add Strict-Transport-Security (HSTS) response header in IIS (Added in web.config)", "DevOps / Web Admin"),
        ("Done", "Frontend", "Install Cookie Consent Banner (CMP) for analytics tracking (Added in templates/base.html)", "Web Developer"),
        ("Done", "Frontend", "Halt Google Analytics / pixel loading until user consent is granted (Google Consent Mode v2)", "Web Developer"),
        ("Done", "Frontend", "Implement Global Privacy Control (GPC) opt-out signal detection (Added in static/js/cookie-consent.js)", "Web Developer"),
        ("Done", "Footer", "Add \"Do Not Sell My Personal Information\" link in templates/base.html (Added in templates/base.html)", "Web Developer / Legal"),
        ("Done", "Legal", "Update templates/privacy-policy.html with current date & disclosures (Updated in templates/privacy-policy.html)", "Legal / Web Content")
    ]
    
    table_chk = doc.add_table(rows=11, cols=4)
    table_chk.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_chk.autofit = False
    
    chk_col_w = [Inches(0.8), Inches(1.2), Inches(3.6), Inches(1.4)]
    chk_headers = ["Status", "Category", "Remediation Action Item", "Assigned Owner"]
    
    chk_hdr_cells = table_chk.rows[0].cells
    for i, title in enumerate(chk_headers):
        chk_hdr_cells[i].width = chk_col_w[i]
        set_cell_background(chk_hdr_cells[i], "1E3A8A")
        set_cell_margins(chk_hdr_cells[i], top=120, bottom=120, left=100, right=100)
        set_cell_borders(chk_hdr_cells[i], top="single", bottom="single", left="none", right="none", color="1E3A8A", sz="8")
        
        p = chk_hdr_cells[i].paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(title)
        format_run(r, font_name='Segoe UI', size_pt=9.0, bold=True, color_rgb=(0xFF, 0xFF, 0xFF))
        if i == 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
    for row_idx, (status, cat, desc, owner) in enumerate(checklist_data, start=1):
        row_cells = table_chk.rows[row_idx].cells
        bg_fill = "FFFFFF" if row_idx % 2 != 0 else "F8FAFC"
        
        for c_idx in range(4):
            row_cells[c_idx].width = chk_col_w[c_idx]
            set_cell_background(row_cells[c_idx], bg_fill)
            set_cell_margins(row_cells[c_idx], top=90, bottom=90, left=100, right=100)
            set_cell_borders(row_cells[c_idx], top="single", bottom="single", left="none", right="none", color="E2E8F0", sz="4")
            
            p = row_cells[c_idx].paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if status == "Done":
                    r = p.add_run("☑ Done")
                    format_run(r, font_name='Segoe UI', size_pt=8.5, bold=True, color_rgb=(0x16, 0xA3, 0x4A))
                else:
                    r = p.add_run("☐ Pending")
                    format_run(r, font_name='Segoe UI', size_pt=8.5, bold=False, color_rgb=(0x64, 0x74, 0x8B))
            elif c_idx == 1:
                r = p.add_run(cat)
                format_run(r, font_name='Segoe UI', size_pt=8.5, bold=True, color_rgb=(0x1E, 0x29, 0x3B))
            elif c_idx == 2:
                r_num = p.add_run(f"{row_idx}. ")
                format_run(r_num, font_name='Segoe UI', size_pt=8.5, bold=True, color_rgb=(0x02, 0x84, 0xC7))
                r = p.add_run(desc)
                format_run(r, font_name='Segoe UI', size_pt=8.5, bold=False, color_rgb=(0x33, 0x41, 0x55))
            elif c_idx == 3:
                r = p.add_run(owner)
                format_run(r, font_name='Segoe UI', size_pt=8.5, bold=False, color_rgb=(0x47, 0x55, 0x69))

    output_path = r"c:\wamp64\www\qhotel\RISK_REMEDIATION_PLAN.docx"
    doc.save(output_path)
    print(f"Successfully created: {output_path}")

if __name__ == "__main__":
    build_word_document()
