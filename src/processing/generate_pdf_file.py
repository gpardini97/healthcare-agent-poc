# Standard library imports
import os
import platform
import re
from pathlib import Path

# Third-party imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Image, Spacer


def build_pdf_report(
        output_path: Path, IMAGES_DIR: Path, 
        report_text: str, title: str = "Generated Report"
    ):
    """
    Build a professional PDF report with title, text (justified), images on the same page, 
    page numbers, and open it automatically. Hyperlinks are converted to plain text so they
    can be copied from the PDF.

    Args:
    output_path (Path): Folder where the final PDF report will be saved. 
                        The folder will be created if it does not exist.
    IMAGES_DIR (Path): Folder containing the PNG images to include in the report.
    report_text (str): The textual content of the report.
    title (str, optional): Title to display at the top of the PDF report. 
                            Defaults to "Generated Report".
    """
    
    # Ensure output folder exists
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "final_report.pdf"

    # Setup the document
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleStyle", fontSize=18, leading=22, spaceAfter=1*cm))
    styles.add(ParagraphStyle(name="Justify", parent=styles["Normal"], alignment=4))  # justify

    story = []

    # Add title page
    story.append(Paragraph(title, styles["TitleStyle"]))
    story.append(Spacer(1, 1*cm))

    # Add report text (justified), removing <a href> markup and leaving plain links
    for paragraph in report_text.split("\n\n"):
        # Regex para substituir <a href="url">texto</a> por "texto (url)"
        clean_paragraph = re.sub(
            r'<a href="([^"]+)">([^<]+)</a>',
            r'\2 (\1)',
            paragraph
        )
        story.append(Paragraph(clean_paragraph, styles["Justify"]))
        story.append(Spacer(1, 0.5*cm))

    # Get image paths
    image_paths = sorted(IMAGES_DIR.glob("*.png"))  # optional: order by name
    image_paths = [str(p) for p in image_paths]

    # Page constraints
    max_width = A4[0] - 4*cm
    max_height = (A4[1] - 6*cm) / len(image_paths) if image_paths else 0  # divide height among images

    # Add all images on the same page
    for img_path in image_paths:
        img = Image(img_path)

        # Maintain aspect ratio
        img_ratio = img.imageWidth / img.imageHeight
        img.drawWidth = min(img.imageWidth, max_width)
        img.drawHeight = img.drawWidth / img_ratio
        if img.drawHeight > max_height:
            img.drawHeight = max_height
            img.drawWidth = max_height * img_ratio

        story.append(img)
        story.append(Spacer(1, 0.5*cm))

    # Build PDF with page numbers
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    # Open PDF automatically
    pdf_path_str = str(output_file)
    if platform.system() == "Darwin":       # macOS
        os.system(f"open '{pdf_path_str}'")
    elif platform.system() == "Windows":    # Windows
        os.startfile(pdf_path_str)
    else:                                   # Linux variants
        os.system(f"xdg-open '{pdf_path_str}'")


def add_page_number(canvas, doc):
    """Add page numbers at the bottom of each page"""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(A4[0] - 2*cm, 1*cm, text)
