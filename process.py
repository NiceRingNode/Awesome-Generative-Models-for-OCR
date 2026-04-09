# -*- coding: utf-8 -*-

import os,re,json,glob
from natsort import natsorted
from pathlib import Path

test_cases = []
cnt = 0
image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
records = {}

subfields = os.listdir('./OCRGenBench')
for field in subfields:
    if field == 'layout':
        files = [str(f) for f in Path(f'./OCRGenBench/{field}/').rglob('*') if f.is_file()]
        files = list(filter(lambda x:not x.endswith('.psd'),files))
        json_paths = list(filter(lambda x:x.endswith('.json'),files))
        images = list(set(files) - set(json_paths))
        gt_images = list(filter(lambda x:'-gt' in x,images))
        input_images = list(set(images) - set(gt_images))
        for json_path in natsorted(json_paths):
            name = json_path.split('/')[-1].replace('.json','')
            with open(json_path,'r',encoding='utf-8') as f:
                data = json.load(f)
            if len(gt_images) > 0:
                gt_matches = [path for path in gt_images if Path(path).stem == f"{name}-gt"]
                gt_image = gt_matches[0]
            else:
                gt_image = None
            matched_paths = [path for path in input_images if Path(path).stem == name]
            input_image = matched_paths[0]
            test_cases.append({
                'id': cnt,
                "field": field,
                "task": 'Layout-Gen',
                "prompt": data['prompt'],
                "input_image_path_1": input_image,
                "input_image_path_2": None,
                "gt_image_path": gt_image,
                'task_type': 'editing',
                'output_path': f'./output/holder/{field}/{name}.png'
            })
            cnt += 1
        records['layout'] = {'task':len(json_paths)}
    for task in os.listdir(f'./OCRGenBench/{field}'):
        inner_cnt = 0
        if field == 'historical' and task.lower() == 'style-transfer':
            files = [str(f) for f in Path(f'./OCRGenBench/{field}/{task}').rglob('*') if f.is_file()]
            files = list(filter(lambda x:not x.endswith('.psd'),files))
            json_paths = list(filter(lambda x:x.endswith('.json'),files))
            for json_path in natsorted(json_paths):
                name = json_path.split('/')[-1].replace('.json','')
                with open(json_path,'r',encoding='utf-8') as f:
                    data = json.load(f)
                images = glob.glob(f'./OCRGenBench/{field}/{task}/images/{name}/*')
                content_image = list(filter(lambda x:'content_' in x,images))[0]
                style_image = list(filter(lambda x:'style_' in x,images))[0]
                test_cases.append({
                    'id': cnt,
                    "field": field,
                    "task": 'Historical-Style-Transfer',
                    "prompt": data['prompt'],
                    "input_image_path_1": content_image,
                    "input_image_path_2": style_image,
                    'task_type': 'editing',
                    'output_path': f'./output/holder/{field}/{task}/{name}.png'
                })
                cnt += 1
                inner_cnt += 1
        elif field == 'artistic' and task.lower() == 'style-transfer':
            files = [str(f) for f in Path(f'./OCRGenBench/{field}/{task}').rglob('*') if f.is_file()]
            files = list(filter(lambda x:not x.endswith('.psd'),files))
            json_paths = list(filter(lambda x:x.endswith('.json'),files))
            images = list(set(files) - set(json_paths))
            gt_images = list(filter(lambda x:'-gt' in x,images))
            input_images = list(set(images) - set(gt_images))
            for json_path in natsorted(json_paths):
                name = json_path.split('/')[-1].replace('.json','')
                with open(json_path,'r',encoding='utf-8') as f:
                    data = json.load(f)
                if len(gt_images) > 0:
                    gt_matches = [path for path in gt_images if Path(path).stem == f"{name}-gt"]
                    gt_image = gt_matches[0]
                else:
                    gt_image = None
                matched_paths = [path for path in input_images if Path(path).stem == name]
                input_image = matched_paths[0]
                annotations = data['annotations'] if 'annotations' in data else None
                test_cases.append({
                    'id': cnt,
                    "field": field,
                    "task": 'Artistic-Style-Transfer',
                    "prompt": data['prompt'],
                    "input_image_path_1": input_image,
                    "input_image_path_2": None,
                    "gt_image_path": gt_image,
                    'annotations': annotations,
                    'task_type': 'editing',
                    'output_path': f'./output/holder/{field}/{task}/{name}.png'
                })
                cnt += 1
                inner_cnt += 1
        elif 'T2I' in task:
            json_paths = [str(f) for f in Path(f'./OCRGenBench/{field}/{task}').rglob('*') if f.is_file()]
            for json_path in natsorted(json_paths):
                name = json_path.split('/')[-1].replace('.json','')
                with open(json_path,'r',encoding='utf-8') as f:
                    data = json.load(f)
                test_cases.append({
                    'id': cnt,
                    "field": field,
                    "task": task,
                    "prompt": data['prompt'],
                    "input_image_path_1": None,
                    "input_image_path_2": None,
                    'task_type': "generation",
                    'output_path': f'./output/holder/{field}/{task}/{name}.png'
                })
                cnt += 1
                inner_cnt += 1
        else:
            files = [str(f) for f in Path(f'./OCRGenBench/{field}/{task}').rglob('*') if f.is_file()]
            files = list(filter(lambda x:not x.endswith('.psd'),files))
            json_paths = list(filter(lambda x:x.endswith('.json'),files))
            images = list(set(files) - set(json_paths))
            gt_images = list(filter(lambda x:'-gt' in x,images))
            input_images = list(set(images) - set(gt_images))
            for json_path in natsorted(json_paths):
                name = json_path.split('/')[-1].replace('.json','')
                with open(json_path,'r',encoding='utf-8') as f:
                    data = json.load(f)
                if len(gt_images) > 0:
                    gt_matches = [path for path in gt_images if Path(path).stem == f"{name}-gt"]
                    gt_image = gt_matches[0]
                else:
                    gt_image = None
                matched_paths = [path for path in input_images if Path(path).stem == name]
                input_image = matched_paths[0]
                annotations = data['annotations'] if 'annotations' in data else None
                if task == 'Removal' and field == 'handwriting':
                    cur_task_name = 'Handwriting-Removal'
                elif task == 'Removal' and field == 'scene':
                    cur_task_name = 'Scene-Text-Removal'
                else:
                    cur_task_name = task
                test_cases.append({
                    'id': cnt,
                    "field": field,
                    "task": cur_task_name,
                    "prompt": data['prompt'],
                    "input_image_path_1": input_image,
                    "input_image_path_2": None,
                    "gt_image_path": gt_image,
                    'annotations': annotations,
                    'task_type': 'editing',
                    'output_path': f'./output/holder/{field}/{task}/{name}.png'
                })
                cnt += 1
                inner_cnt += 1
        if records.get(field) is None:
            records[field] = {}
        records[field][task] = inner_cnt

os.makedirs('./data',exist_ok=True)
with open('data/test_cases.json','w',encoding='utf-8') as f:
    json.dump(test_cases,f,indent=4,ensure_ascii=False)

for k in records:
    print(k,sum(records[k].values()))
print('sum:',sum([v for k in records for v in records[k].values()]))