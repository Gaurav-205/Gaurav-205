import sys
import os
from PIL import Image, ImageOps, ImageEnhance

try:
    import onnxruntime
    import cv2
    import numpy as np
    from rembg import remove
    HAS_CV2_REMBG = True
except ImportError as e:
    print(f"Notice: CV2, onnxruntime, or rembg not imported ({e}). Fallback mode will be used.")
    HAS_CV2_REMBG = False

def prep_photo(image_path, output_path="source-prepped.png"):
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} does not exist.")
        sys.exit(1)

    print(f"Loading image {image_path}...")
    
    if HAS_CV2_REMBG:
        try:
            img = Image.open(image_path)
            print("Removing background using rembg...")
            nobg_img = remove(img)
            
            temp_nobg_path = "temp_nobg.png"
            nobg_img.save(temp_nobg_path)
            
            cv_img = cv2.imread(temp_nobg_path, cv2.IMREAD_UNCHANGED)
            
            if cv_img is not None:
                if cv_img.shape[2] == 4:
                    alpha = cv_img[:, :, 3]
                    rgb = cv_img[:, :, :3]
                    
                    white_bg = np.ones_like(rgb) * 255
                    alpha_factor = alpha[:, :, np.newaxis] / 255.0
                    composited = (rgb * alpha_factor + white_bg * (1 - alpha_factor)).astype(np.uint8)
                else:
                    composited = cv_img
                    
                gray = cv2.cvtColor(composited, cv2.COLOR_BGR2GRAY)
                
                print("Applying CLAHE contrast enhancement...")
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                clahe_img = clahe.apply(gray)
                
                cv2.imwrite(output_path, clahe_img)
                
                if os.path.exists(temp_nobg_path):
                    os.remove(temp_nobg_path)
                print(f"Prepped image saved to {output_path} (rembg + CLAHE)")
                return
        except Exception as ex:
            print(f"Error during rembg/CV2 prep: {ex}. Falling back to PIL-based prep...")

    # Fallback/PIL-only path
    try:
        img = Image.open(image_path)
        # Convert to grayscale
        gray_img = img.convert("L")
        # Auto-contrast
        gray_img = ImageOps.autocontrast(gray_img)
        # Boost contrast further
        enhancer = ImageEnhance.Contrast(gray_img)
        gray_img = enhancer.enhance(1.8)
        
        gray_img.save(output_path)
        print(f"Prepped image saved to {output_path} (PIL-based fallback)")
    except Exception as ex:
        print(f"Error during PIL prep: {ex}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <path_to_source_photo>")
        sys.exit(1)
        
    prep_photo(sys.argv[1])
