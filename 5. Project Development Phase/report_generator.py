import os
import re
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas to handle two-pass page numbering ("Page X of Y")
    and dynamic header/footer drawing.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (Top of each page)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#555555"))
        self.drawString(54, 750, "Voice-Based Concept Understanding Analyser (VBCUA) - Evaluation Report")
        
        # Header Line
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer (Bottom of each page)
        self.line(54, 50, 558, 50)
        self.setFont("Helvetica", 8)
        self.drawString(54, 38, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Page Number right-aligned
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, page_text)
        
        self.restoreState()


def generate_pdf_report(
    output_pdf_path: str,
    user_name: str,
    concept_title: str,
    reference_text: str,
    transcribed_text: str,
    scores: dict,
    audio_features: dict,
    waveform_png_path: str = None
):
    """
    Generates a highly-stylized educational evaluation report in PDF format.
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    
    # Target page width budget: Letter size is 612 x 792 pt. Printable area margins: 54pt (0.75 in)
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,  # Give room for top header
        bottomMargin=72 # Give room for footer
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY_COLOR = colors.HexColor("#0f4c81") # Deep Blue
    SECONDARY_COLOR = colors.HexColor("#2a75d3") # Mid Blue
    TEXT_COLOR = colors.HexColor("#333333") # Off black
    
    # Determine colors for understanding levels
    level = scores.get("understanding_level", "Moderate")
    if level == "Strong":
        LEVEL_COLOR = colors.HexColor("#2e7d32") # Green
        LEVEL_BG = colors.HexColor("#e8f5e9")
    elif level == "Moderate":
        LEVEL_COLOR = colors.HexColor("#ef6c00") # Orange
        LEVEL_BG = colors.HexColor("#fff3e0")
    else:
        LEVEL_COLOR = colors.HexColor("#c62828") # Red
        LEVEL_BG = colors.HexColor("#ffebee")
        
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_COLOR,
        spaceAfter=6
    )
    
    label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555")
    )
    
    val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_COLOR
    )

    story = []
    
    # Title
    story.append(Paragraph("Conceptual Understanding Assessment", title_style))
    story.append(Spacer(1, 8))
    
    # Metadata Block Table
    meta_data = [
        [Paragraph("Candidate Name:", label_style), Paragraph(user_name, val_style),
         Paragraph("Date evaluated:", label_style), Paragraph(datetime.datetime.now().strftime('%Y-%m-%d'), val_style)],
        [Paragraph("Target Concept:", label_style), Paragraph(concept_title, val_style),
         Paragraph("Audio Duration:", label_style), Paragraph(f"{round(audio_features.get('duration_sec', 0.0), 1)} seconds", val_style)]
    ]
    meta_table = Table(meta_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#eeeeee")),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Scores Grid Table
    score_p_overall = ParagraphStyle('OvrScore', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=PRIMARY_COLOR, alignment=1)
    score_p_comp = ParagraphStyle('CompScore', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=SECONDARY_COLOR, alignment=1)
    score_p_flue = ParagraphStyle('FlueScore', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor("#777777"), alignment=1)
    
    level_label_style = ParagraphStyle('LvlLbl', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=LEVEL_COLOR, alignment=1)
    
    scores_data = [
        [
            Paragraph("COMPREHENSION SCORE", ParagraphStyle('ScoreH1', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#666666"), alignment=1)),
            Paragraph("SPEECH FLUENCY SCORE", ParagraphStyle('ScoreH2', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#666666"), alignment=1)),
            Paragraph("OVERALL ASSESSMENT", ParagraphStyle('ScoreH3', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#666666"), alignment=1))
        ],
        [
            Paragraph(f"{scores.get('comprehension_score', 0.0)}%", score_p_comp),
            Paragraph(f"{scores.get('fluency_score', 0.0)}%", score_p_flue),
            Paragraph(f"{scores.get('overall_score', 0.0)} / 100", score_p_overall)
        ],
        [
            Paragraph("", val_style),
            Paragraph("", val_style),
            Paragraph(level.upper(), level_label_style)
        ]
    ]
    
    scores_table = Table(scores_data, colWidths=[2.3*inch, 2.3*inch, 2.4*inch])
    scores_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (2,0), (2,-1), LEVEL_BG),
        ('BOX', (0,0), (0,-1), 1, colors.HexColor("#e2e8f0")),
        ('BOX', (1,0), (1,-1), 1, colors.HexColor("#e2e8f0")),
        ('BOX', (2,0), (2,-1), 1.5, LEVEL_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,1), (-1,1), 2),
        ('BOTTOMPADDING', (0,2), (-1,2), 8),
    ]))
    story.append(scores_table)
    story.append(Spacer(1, 15))
    
    # Detailed Acoustic & Speech Delivery Metrics Table
    story.append(Paragraph("Detailed Delivery Metrics", h2_style))
    metrics_data = [
        [
            Paragraph("Metric", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)),
            Paragraph("Value Detected", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)),
            Paragraph("Healthy Baseline", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)),
            Paragraph("Diagnostic Status", ParagraphStyle('TH4', fontName='Helvetica-Bold', fontSize=9, textColor=colors.white))
        ],
        [
            Paragraph("Filler Word Ratio", body_style),
            Paragraph(f"{round(audio_features.get('filler_ratio', 0.0) * 100, 1)}% ({audio_features.get('filler_word_count', 0)} fillers)", val_style),
            Paragraph("< 5.0%", val_style),
            Paragraph("Optimal" if audio_features.get('filler_ratio', 0.0) < 0.05 else "Frequent Hesitation", val_style)
        ],
        [
            Paragraph("Pause Ratio", body_style),
            Paragraph(f"{round(audio_features.get('pause_ratio', 0.0) * 100, 1)}%", val_style),
            Paragraph("15.0% - 25.0%", val_style),
            Paragraph("Healthy Pacing" if 0.15 <= audio_features.get('pause_ratio', 0.0) <= 0.25 else "Rushed" if audio_features.get('pause_ratio', 0.0) < 0.15 else "Hesitant", val_style)
        ],
        [
            Paragraph("RMS Energy (Average Volume)", body_style),
            Paragraph(f"{round(audio_features.get('rms_energy', 0.0), 4)}", val_style),
            Paragraph("> 0.01", val_style),
            Paragraph("Clear Signal" if audio_features.get('rms_energy', 0.0) > 0.01 else "Faint/Low Audio", val_style)
        ],
        [
            Paragraph("Zero-Crossing Rate (Noisiness)", body_style),
            Paragraph(f"{round(audio_features.get('zero_crossing_rate', 0.0), 3)}", val_style),
            Paragraph("0.05 - 0.25", val_style),
            Paragraph("Normal Voicing", val_style)
        ]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2.2*inch, 1.8*inch, 1.3*inch, 1.7*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 15))
    
    # Waveform Display Section
    if waveform_png_path and os.path.exists(waveform_png_path):
        wave_block = []
        wave_block.append(Paragraph("Acoustic Waveform Plot", h2_style))
        # Letter width is 612, margins 108 total, so maximum width is 504.
        # We target 480 width and 140 height.
        wave_block.append(Image(waveform_png_path, width=6.6*inch, height=2.2*inch))
        wave_block.append(Spacer(1, 15))
        story.append(KeepTogether(wave_block))
        
    # Content Comparison Section
    compare_block = []
    compare_block.append(Paragraph("Concept Coverage Comparison", h2_style))
    compare_data = [
        [
            Paragraph("Target Reference Concept", ParagraphStyle('TComp1', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.white)),
            Paragraph("Transcribed Explanation", ParagraphStyle('TComp2', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.white))
        ],
        [
            Paragraph(reference_text.replace('\n', '<br/>'), ParagraphStyle('RefP', fontName='Helvetica', fontSize=8, leading=11, textColor=TEXT_COLOR)),
            Paragraph(transcribed_text.replace('\n', '<br/>') if transcribed_text.strip() else "[No speech transcribed]", ParagraphStyle('TrP', fontName='Helvetica', fontSize=8, leading=11, textColor=TEXT_COLOR))
        ]
    ]
    compare_table = Table(compare_data, colWidths=[3.5*inch, 3.5*inch])
    compare_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    compare_block.append(compare_table)
    compare_block.append(Spacer(1, 15))
    story.append(KeepTogether(compare_block))
    
    # Qualitative Feedback (AI Generated Summary)
    feedback_block = []
    feedback_block.append(Paragraph("Qualitative Educational Feedback", h2_style))
    
    feedback_text = scores.get("feedback_text", "")
    if not feedback_text:
        feedback_text = "No qualitative feedback summary was generated."
        
    # Format markdown segments inside ReportLab paragraph
    # We will strip hashes and basic markdown bolding to make it clean for a Paragraph, 
    # or divide into separate sub-paragraphs.
    lines = feedback_text.split('\n')
    for line in lines:
        line_str = line.strip()
        if not line_str:
            feedback_block.append(Spacer(1, 4))
            continue
            
        # Parse titles
        if line_str.startswith("###"):
            title = line_str.replace("###", "").strip()
            feedback_block.append(Paragraph(title, ParagraphStyle('FeedbackH3', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=PRIMARY_COLOR, spaceBefore=4, spaceAfter=2)))
        elif line_str.startswith("##"):
            title = line_str.replace("##", "").strip()
            feedback_block.append(Paragraph(title, ParagraphStyle('FeedbackH2', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=PRIMARY_COLOR, spaceBefore=6, spaceAfter=3)))
        elif line_str.startswith("**") and line_str.endswith("**"):
            # A bold line
            bold_text = line_str.replace("**", "")
            feedback_block.append(Paragraph(bold_text, ParagraphStyle('FeedbackB', fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=TEXT_COLOR, spaceAfter=4)))
        else:
            # Inline bold conversions **text** -> <b>text</b>
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line_str)
            # Bullet point handling
            if formatted_line.startswith("-") or formatted_line.startswith("*"):
                bullet_text = formatted_line[1:].strip()
                feedback_block.append(Paragraph(bullet_text, ParagraphStyle('FeedbackBullet', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=TEXT_COLOR, leftIndent=15, firstLineIndent=-10, spaceAfter=3)))
            else:
                feedback_block.append(Paragraph(formatted_line, ParagraphStyle('FeedbackBody', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=TEXT_COLOR, spaceAfter=3)))
                
    story.append(KeepTogether(feedback_block))
    
    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
