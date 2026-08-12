import sys
import site

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

try:
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR()
    print("RapidOCR initialized successfully!")
except Exception as e:
    print("RapidOCR init error:", e)

try:
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    print("EasyOCR initialized successfully!")
except Exception as e:
    print("EasyOCR init error:", e)
