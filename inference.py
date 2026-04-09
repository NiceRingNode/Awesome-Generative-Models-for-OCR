# -*- coding: utf-8 -*-

import json,os,argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--model',type=str,default='')
opt = parser.parse_args()

generate_func, edit_func = None, None
def get_model_functions(model_name):
    global generate_func, edit_func
    if model_name == 'longcat':
        from longcat import longcat_generate_func as generate_func, longcat_edit_func as edit_func
    elif model_name == 'your model name':
        ...
    else:
        raise ValueError('Unsupported Model.')

get_model_functions(opt.model)

def run_model_inference(prompt,input_image_path1=None,input_image_path2=None):
    if input_image_path1 is not None:
        image = edit_func(prompt,input_image_path1,input_image_path2)
    else:
        image = generate_func(prompt)
    return image

def main():
    base_output_dir = f'./output/{opt.model}'
    with open('./data/test_cases.json','r',encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs(base_output_dir, exist_ok=True)
    for i, case in enumerate(data):
        if edit_func is None and case['task_type'] != 'generation':
            continue
        if generate_func is None and case['task_type'] != 'editing':
            continue
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
        result_image = run_model_inference(
            prompt=case['prompt'],
            input_image_path1=case['input_image_path_1'],
            input_image_path2=case['input_image_path_2']
        )
        result_image.save(output_path)
    print('Inference done.')
    
if __name__ == '__main__':
    main()