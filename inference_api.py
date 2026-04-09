# -*- coding: utf-8 -*-

import json,os,argparse,mimetypes,base64,re,math
from pathlib import Path
from PIL import Image,ImageOps
from openai import OpenAI 
from google import genai
from google.genai import types
from io import BytesIO

parser = argparse.ArgumentParser()
parser.add_argument('--model',type=str,default='janus4o')
opt = parser.parse_args()

if opt.model in ['gpt-image-1.5','gpt-image-1']:
    base_url = os.getenv('OPENAI_BASE_URL')
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key,base_url=base_url)
elif opt.model in ['gemini-3-pro-image-preview']:
    base_url = os.getenv('GEMINI_BASE_URL')
    api_key = os.getenv('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key,http_options={"base_url": base_url})
elif opt.model == 'doubao-seedream-4-5-251128':
    base_url = os.getenv('OPENAI_BASE_URL')
    api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(base_url=base_url,api_key=api_key)

def encode_image_str(image_path):
    with open(image_path,'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def encode_image(image_path):
    with open(image_path,'rb') as image_file:
        return image_file.read()
    
def image_path_to_base64_data_url(path):
    mime_type, _ = mimetypes.guess_type(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

def pil_image_to_base64_bytes(img, path):
    ext_to_format = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
    suffix = path.split('.')[-1].lower()
    buffer = BytesIO()
    img.save(buffer, format=ext_to_format[suffix])
    image_bytes = buffer.getvalue()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type, _ = mimetypes.guess_type(path)
    return f"data:{mime_type};base64,{b64}"

def resize_if_aspect_ratio_exceed(image, max_ratio=16):
    w, h = image.size
    ratio = max(w / h, h / w)
    if ratio <= max_ratio:
        return image
    if w > h:
        new_w = w
        new_h = int(math.ceil(w / max_ratio))
    else:
        new_h = h
        new_w = int(math.ceil(h / max_ratio))
    image = image.resize((new_w, new_h), Image.BICUBIC)
    return image

def run_model_inference(prompt,input_image_path1=None,input_image_path2=None):
    if input_image_path1 is not None and input_image_path2 is None: # 编辑
        if opt.model in ['gpt-image-1.5','gpt-image-1']:
            image = encode_image(input_image_path1)
            result = client.images.edit(prompt=prompt,image=image,model=opt.model)
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
        elif opt.model in ['gemini-3-pro-image-preview']:
            image = Image.open(input_image_path1)
            result = client.models.generate_content(model=opt.model,contents=[prompt,image])
            if result.parts:
                for part in result.parts:
                    if part.text:
                        match = re.search(r'data:image/(png|jpeg|jpg|gif|webp);base64,([A-Za-z0-9+/=]+)', part.text)
                        if match:
                            image_format = match.group(1)
                            image_base64 = match.group(2)
                    elif hasattr(part, 'inline_data') and part.inline_data:
                        image_base64 = part.inline_data.data
            else:
                print(result.candidates[0].finish_reason)
            image_bytes = image_base64
        elif opt.model in ['doubao-seedream-4-5-251128']:
            image = Image.open(input_image_path1)
            image = resize_if_aspect_ratio_exceed(image,16)
            width,height = image.size
            if width * height >= (36000000 - 1):
                ratio = ((36000000 - 1) / (width * height)) ** 0.5
                resized_width = int(width * ratio)
                resized_height = int(height * ratio)
                image = image.resize((resized_width,resized_height))
            image = pil_image_to_base64_bytes(image,input_image_path1)
            result = client.images.generate(model=opt.model,prompt=prompt,response_format="b64_json",extra_body={"image": image,"watermark": False,"sequential_image_generation": "disabled"})
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
        return image_bytes
    elif input_image_path1 is not None and input_image_path2 is not None:
        if opt.model in ['gpt-image-1.5','gpt-image-1']:
            image1 = encode_image(input_image_path1)
            image2 = encode_image(input_image_path2)
            result = client.images.edit(prompt=prompt,image=[image1,image2],model=opt.model)
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
        elif opt.model in ['gemini-3-pro-image-preview']:
            image1 = Image.open(input_image_path1)
            image2 = Image.open(input_image_path2)
            result = client.models.generate_content(model=opt.model,contents=[prompt,image1,image2],config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE']))
            for part in result.parts:
                if part.text:
                    match = re.search(r'data:image/(png|jpeg|jpg|gif|webp);base64,([A-Za-z0-9+/=]+)', part.text)
                    if match:
                        image_format = match.group(1)
                        image_base64 = match.group(2)
                elif hasattr(part, 'inline_data') and part.inline_data:
                    image_base64 = part.inline_data.data
                image_bytes = image_base64
        elif opt.model in ['doubao-seedream-4-5-251128']:
            image1 = Image.open(input_image_path1)
            width,height = image1.size
            if width * height >= (36000000 - 1):
                ratio = ((36000000 - 1) / (width * height)) ** 0.5
                resized_width = int(width * ratio)
                resized_height = int(height * ratio)
                image1 = image1.resize((resized_width,resized_height))
            image2 = Image.open(input_image_path2)
            width,height = image2.size
            if width * height >= (36000000 - 1):
                ratio = ((36000000 - 1) / (width * height)) ** 0.5
                resized_width = int(width * ratio)
                resized_height = int(height * ratio)
                image2 = image2.resize((resized_width,resized_height))
            image1 = pil_image_to_base64_bytes(image1,input_image_path1)
            image2 = pil_image_to_base64_bytes(image2,input_image_path2)
            result = client.images.generate(model=opt.model,prompt=prompt,response_format="b64_json",extra_body={"image": [image1,image2],"watermark": False,"sequential_image_generation": "disabled"})
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
        return image_bytes
    else:
        if opt.model in ['gpt-image-1.5','gpt-image-1']:
            result = client.images.generate(model=opt.model,prompt=prompt)
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
        elif opt.model in ['gemini-3-pro-image-preview']:
            result = client.models.generate_content(model=opt.model,contents=prompt,config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE']))
            for part in result.parts:
                if part.text:
                    match = re.search(r'data:image/(png|jpeg|jpg|gif|webp);base64,([A-Za-z0-9+/=]+)', part.text)
                    if match:
                        image_format = match.group(1)
                        image_base64 = match.group(2)
                elif hasattr(part, 'inline_data') and part.inline_data:
                    image_base64 = part.inline_data.data
                image_bytes = image_base64
        elif opt.model in ['doubao-seedream-4-5-251128']:
            result = client.images.generate(model=opt.model,prompt=prompt,extra_body={'watermark': False},response_format='b64_json')
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
    return image_bytes

def main():
    base_output_dir = f'./output/{opt.model}'
    with open('./data/test_cases.json','r',encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs(base_output_dir, exist_ok=True)
    for i, case in enumerate(data):
        output_path = case['output_path'].replace('holder',opt.model)
        if os.path.exists(output_path):
            continue
        output_path = Path(output_path)
        print("-" * 80)
        print(f"Running test [{i + 1}/{len(data)}]:")
        print(f" - Text category: {case['field']}")
        print(f" - OCR generative task: {case['task']}")
        # print(f" - prompt: {case['prompt']}")
        print(f" - input_image_path 1: {case['input_image_path_1']}")
        print(f" - input_image_path 2: {case['input_image_path_2']}")
        print(f" - output_path: {output_path}")
        if not output_path:
            print(" - warning: output path not found, skipping.")
            continue
        
        os.makedirs(output_path.parent, exist_ok=True)
        image_bytes = run_model_inference(prompt=case['prompt'],input_image_path1=case['input_image_path_1'],input_image_path2=case['input_image_path_2'])
        if image_bytes is not None:
            with open(output_path, "wb") as f:
                f.write(image_bytes)
        else:
            print('skipping:',output_path)
    print('Inference done.')
    
if __name__ == '__main__':
    main()