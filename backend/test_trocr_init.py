import sys
import site

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
print("HuggingFace Transformers TrOCR imports successful!")

print("Loading pre-trained Microsoft TrOCR Small Handwritten model...")
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-handwritten')
print("Microsoft TrOCR Small Handwritten model loaded successfully!")
