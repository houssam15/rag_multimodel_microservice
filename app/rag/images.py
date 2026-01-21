import fitz
import base64
from PIL import Image
from langchain_core.messages import HumanMessage
from .llm import llm
import io

def extract_images_from_pdf(pdf_path):
    images = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                pil_image = Image.open(io.BytesIO(image_bytes))
                if pil_image.mode != "RGB":
                    pil_image = pil_image.convert("RGB")
                images.append(pil_image)
            except Exception as e:
                print(f"Error extracting image {img_index} from page {page_num}: {e}")
                continue
    doc.close()
    return images

def image_to_base64(image: Image.Image):
    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def describe_image(image: Image.Image):
    img_b64 = image_to_base64(image)

    message = HumanMessage(
        content=[
            {"type": "text", "text": "Describe this image clearly."},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_b64}"
                }
            }
        ]
    )

    response = llm.invoke([message])
    return response.content
