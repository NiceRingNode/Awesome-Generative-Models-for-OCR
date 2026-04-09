import torch, math
from PIL import Image
from diffusers import LongCatImageEditPipeline, LongCatImagePipeline, LongCatImageTransformer2DModel, AutoencoderKL, FlowMatchEulerDiscreteScheduler
from transformers import Qwen2_5_VLForConditionalGeneration, Qwen2VLProcessor, AutoTokenizer
from diffusers.utils import load_image

class LongCatUnifiedPipeline:
    def __init__(self, model_id):        
        self.transformer = LongCatImageTransformer2DModel.from_pretrained(model_id, subfolder="transformer", torch_dtype=torch.bfloat16)
        self.vae = AutoencoderKL.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.bfloat16)
        self.text_encoder = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_id, subfolder="text_encoder", torch_dtype=torch.bfloat16)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, subfolder="tokenizer", fix_mistral_regex=True)
        self.text_processor = Qwen2VLProcessor.from_pretrained(model_id, subfolder="text_processor", tokenizer_kwargs={"fix_mistral_regex": True})
        self.scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")

        self.t2i_pipeline = self.create_t2i_pipeline()
        self.edit_pipeline = self.create_edit_pipeline()
            
    def create_t2i_pipeline(self):
        pipe = LongCatImagePipeline(
            transformer=self.transformer,
            vae=self.vae,
            text_encoder=self.text_encoder,
            tokenizer=self.tokenizer,
            scheduler=self.scheduler,
            text_processor=self.text_processor
        )
        pipe = pipe.to("cuda")
        return pipe
    
    def create_edit_pipeline(self):
        pipe = LongCatImageEditPipeline(
            transformer=self.transformer,
            vae=self.vae,
            text_encoder=self.text_encoder,
            tokenizer=self.tokenizer,
            scheduler=self.scheduler,
            text_processor=self.text_processor
        )
        return pipe
    
    @torch.inference_mode()
    def generate(self, prompt, negative_prompt="", num_inference_steps=50, guidance_scale=4.5, enable_cfg_renorm=True, enable_prompt_rewrite=True, **kwargs):
        image = self.t2i_pipeline(prompt=prompt,negative_prompt=negative_prompt,num_inference_steps=num_inference_steps,guidance_scale=guidance_scale,enable_cfg_renorm=enable_cfg_renorm,enable_prompt_rewrite=enable_prompt_rewrite,**kwargs).images[0]
        return image
    
    @torch.inference_mode()
    def edit(self, prompt, image, negative_prompt="", num_inference_steps=50, guidance_scale=4.5, **kwargs):
        if isinstance(image, str):
            image = load_image(image)
        result = self.edit_pipeline(image,prompt,negative_prompt=negative_prompt,guidance_scale=guidance_scale,num_inference_steps=num_inference_steps,num_images_per_prompt=1,**kwargs).images[0]
        return result

def load_and_concat_images(input_image_path1, input_image_path2):
    input_image1 = load_image(input_image_path1)
    input_image2 = load_image(input_image_path2)
    
    width1, height1 = input_image1.size
    width2, height2 = input_image2.size
    
    concat_width = width1 + width2
    concat_height = max(height1, height2)
    
    concat_image = Image.new('RGB', (concat_width, concat_height), (255, 255, 255))
    concat_image.paste(input_image1, (0, 0))
    concat_image.paste(input_image2, (width1, 0))

    resized_width = concat_width
    resized_height = concat_height
    
    return concat_image, resized_width, resized_height

def rounded_int(num):
    scale = int(round(num / 16,0))
    return 16 * scale

def resize_if_exceed(image, max_blocks=192):
    w, h = image.size
    max_size = 16 * max_blocks # 3072

    scale = 1.0
    if w / 16 > max_blocks or h / 16 > max_blocks:
        scale_w = max_size / w if w / 16 > max_blocks else 1.0
        scale_h = max_size / h if h / 16 > max_blocks else 1.0
        scale = min(scale_w, scale_h)

        new_w = int(math.floor(w * scale / 16) * 16)
        new_h = int(math.floor(h * scale / 16) * 16)
        image = image.resize((new_w, new_h), Image.BICUBIC)
    return image

model = LongCatUnifiedPipeline(model_id="/media/l/disk4/zpr/EvalBench/models/LongCat-Image-Edit")

def longcat_edit_func(input_prompt=None, input_image_path1=None, input_image_path2=None):
    torch.cuda.empty_cache()
    if input_image_path1 is not None and input_image_path2 is None:
        input_image = load_image(input_image_path1)
        image = model.edit(image=input_image,prompt=input_prompt)
        return image
    elif input_image_path1 is not None and input_image_path2 is not None:
        concat_image, _, _ = load_and_concat_images(input_image_path1, input_image_path2)
        image = model.edit(image=concat_image,prompt=input_prompt)
        return image

def longcat_generate_func(input_prompt=None):
    torch.cuda.empty_cache()
    image = model.generate(prompt=input_prompt)
    return image