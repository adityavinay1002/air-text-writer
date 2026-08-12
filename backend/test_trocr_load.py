import os
import sys
import site

libs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libs")
if libs_dir not in sys.path:
    sys.path.append(libs_dir)

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

import torch
from PIL import Image
import numpy as np

print("Testing HuggingFace TrOCR import & model load (with use_fast=False)...")
try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    print("Transformers version imported cleanly!")
    
    print("Loading pre-trained Microsoft TrOCR Small Handwritten model...")
    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-small-handwritten', use_fast=False)
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-small-handwritten')
    model.eval()
    print("TrOCR Small Handwritten model loaded successfully!")

    # Test dummy inference
    dummy_img = Image.fromarray(np.full((100, 300, 3), 255, dtype=np.uint8))
    pixel_values = processor(images=dummy_img, return_tensors="pt").pixel_values
    with torch.no_grad():
        generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(f"TrOCR dummy test inference output: '{generated_text}'")

except Exception as e:
    print("TrOCR test error:", e)
    import traceback
    traceback.print_exc()
