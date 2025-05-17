import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
from PyPDF2 import PdfWriter,PdfReader
import os


def add_custom_text(page, text_length=50, x_range=(50, 500), y_range=(50, 700),
                    opacity_range=(0.3, 0.7), font_size_range=(8, 16)):
    """在PDF页面上添加自定义参数的随机文本"""
    # 1. 生成随机文本内容
    text = ''.join(random.choices(
        string.ascii_letters + string.digits + string.punctuation,
        k=text_length
    ))

    # 2. 设置文本样式参数
    styles = {
        'font': random.choice(['helvetica', 'times-roman', 'courier']),
        'fontsize': random.randint(*font_size_range),
        'color': tuple(random.randint(50, 200) / 255 for _ in range(3)),  # 修改这里
        'opacity': random.uniform(*opacity_range),
    }

    # 3. 计算位置，确保不超出页面边界
    x_min, x_max = x_range
    y_min, y_max = y_range
    x_pos = random.randint(x_min, min(x_max, page.rect.width - 10))
    y_pos = random.randint(y_min, min(y_max, page.rect.height - 10))

    # 4. 添加文本到页面
    page.insert_text(
        (x_pos, y_pos),
        text,
        fontsize=styles['fontsize'],
        color=styles['color'],
        fill_opacity=styles['opacity'],
        fontname=styles['font']
    )

def process_pdf(input_path, output_path, **kwargs):
    """处理PDF文件的主函数"""
    doc = fitz.open(input_path)
    for page in doc:
        add_custom_text(page, **kwargs)
    doc.save(output_path)
    doc.close()

def pdf_to_image(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def save_images_as_pdf(images, output_path):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(images[0].width, images[0].height))
    temp_files = []

    for img in images:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            img.save(temp_file.name, format='PNG')
            temp_files.append(temp_file.name)
            can.drawImage(temp_file.name, 0, 0, width=img.width, height=img.height)
            can.showPage()

    can.save()
    packet.seek(0)

    new_pdf = PdfReader(packet)
    output = PdfWriter()

    for i in range(len(new_pdf.pages)):
        page = new_pdf.pages[i]
        output.add_page(page)

    outputStream = open(output_path, "wb")
    output.write(outputStream)
    outputStream.close()

    # Clean up temporary files
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"Error removing {temp_file}: {e}")

def main():
    input_pdf_path = "input.pdf"
    output_pdf_path = "output.pdf"
    output2_pdf_path = "output2.pdf"

    images = pdf_to_image(input_pdf_path)
    save_images_as_pdf(images, output_pdf_path)

    process_pdf(output_pdf_path, output2_pdf_path,
                text_length=80,  # 文本长度（默认50）
                x_range=(100, 400),  # 横向位置范围（单位：点）
                y_range=(200, 600),  # 纵向位置范围（单位：点）
                opacity_range=(0.4, 0.6),  # 透明度范围（0-1）
                font_size_range=(10, 14)  # 字体大小范围
                )

if __name__ == "__main__":
    main()



