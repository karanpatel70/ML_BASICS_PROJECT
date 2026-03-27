from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open(r'C:\Users\karan\OneDrive\Desktop\pythonprojects\Resume_screener\JD.png')
text = pytesseract.image_to_string(img)

print(text)