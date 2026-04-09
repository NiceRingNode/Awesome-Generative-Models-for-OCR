# -*- coding: utf-8 -*-

import json,os,argparse,editdistance,re,lpips,torch,cv2
from PIL import Image
from pytorch_msssim import ms_ssim
from dd.func import compute_dd
from paddleocr import PaddleOCR
from torchvision import transforms
import numpy as np
from copy import deepcopy
from collections import defaultdict
from natsort import natsorted

parser = argparse.ArgumentParser()
parser.add_argument('--model',type=str,default='bagel')
parser.add_argument('--disable_vie',action='store_true')
opt = parser.parse_args()

def detect_language(prompt):
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', prompt)
    english_chars = re.findall(r'[a-zA-Z]', prompt)
    num_chinese = len(chinese_chars)
    num_english = len(english_chars)
    total = num_chinese + num_english
    if total == 0:
        return "unknown"
    if num_chinese >= num_english:
        return "chinese"
    elif num_english > num_chinese:
        return "english"

def is_vertical_layout(result):
    rec_polys = result[0]['rec_polys']
    if len(rec_polys) < 3:
        return False
    ratios = []
    centers_x = []
    centers_y = []

    for poly in rec_polys:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        w = max(xs) - min(xs)
        h = max(ys) - min(ys)
        if w > 0:
            ratios.append(h / w)
        centers_x.append((xs[0] + xs[2]) / 2)
        centers_y.append((ys[0] + ys[2]) / 2)
    if not ratios:
        return False
    avg_ratio = sum(ratios) / len(ratios)
    x_span = max(centers_x) - min(centers_x)
    y_span = max(centers_y) - min(centers_y)
    return avg_ratio > 1.3 and x_span > y_span * 0.5

def sort_vertical(result):
    rec_polys = result[0]['rec_polys']
    rec_texts = result[0]['rec_texts']
    if not rec_polys:
        return result
    
    widths = [poly[2][0] - poly[0][0] for poly in rec_polys]
    median_width = np.median(widths)
    x_threshold = median_width * 0.8

    boxes = []
    for poly, text in zip(rec_polys, rec_texts):
        center_x = (poly[0][0] + poly[2][0]) / 2
        center_y = (poly[0][1] + poly[2][1]) / 2
        boxes.append({
            'poly': poly,
            'text': text,
            'center_x': center_x,
            'center_y': center_y
        })

    # right → left
    boxes.sort(key=lambda b: -b['center_x'])

    columns = []
    for box in boxes:
        added = False
        for col in columns:
            col_x = sum(b['center_x'] for b in col) / len(col)
            if abs(box['center_x'] - col_x) < x_threshold:
                col.append(box)
                added = True
                break
        if not added:
            columns.append([box])

    sorted_boxes = []
    for col in columns:
        col_sorted = sorted(col, key=lambda b: b['center_y'])
        sorted_boxes.extend(col_sorted)

    result[0]['rec_polys'] = [b['poly'] for b in sorted_boxes]
    result[0]['rec_texts'] = [b['text'] for b in sorted_boxes]
    return result

def sort_paddle_ocr_adaptive(result):
    rec_polys = result[0]['rec_polys']
    rec_texts = result[0]['rec_texts']
    
    if not rec_polys:
        return result

    heights = [poly[2][1] - poly[0][1] for poly in rec_polys]
    median_height = np.median(heights)
    y_threshold = median_height * 0.6
    
    boxes_with_text = []
    for poly, text in zip(rec_polys, rec_texts):
        center_x = (poly[0][0] + poly[2][0]) / 2
        center_y = (poly[0][1] + poly[2][1]) / 2
        
        boxes_with_text.append({'poly': poly, 'text': text, 'center_x': center_x, 'center_y': center_y})
    boxes_with_text.sort(key=lambda b: b['center_y'])
    lines = []
    for box in boxes_with_text:
        added = False
        for line in lines:
            line_y = sum(b['center_y'] for b in line) / len(line)
            if abs(box['center_y'] - line_y) < y_threshold:
                line.append(box)
                added = True
                break
        if not added:
            lines.append([box])

    sorted_lines = sorted(lines, key=lambda line: sum(b['center_y'] for b in line) / len(line))
    sorted_boxes = []
    for line in sorted_lines:
        sorted_line = sorted(line, key=lambda b: b['center_x'])
        sorted_boxes.extend(sorted_line)
    
    result[0]['rec_polys'] = [box['poly'] for box in sorted_boxes]
    result[0]['rec_texts'] = [box['text'] for box in sorted_boxes]
    return result

def calculate_order_free_CER(doc_pred, doc_gt):
    if not isinstance(doc_gt, list):
        doc_gt = [doc_gt]

    if not doc_gt:
        return {
            'CER': 0.0,
            'AR': 100.0,
            'edit_distance': 0,
            'gt_length': 0,
            'pred_length': len(' '.join(doc_pred)) if doc_pred else 0
        }

    if not doc_pred:
        gt_len = sum(len(g) for g in doc_gt)
        return {
            'CER': 100.0,
            'AR': 0.0,
            'edit_distance': gt_len,
            'gt_length': gt_len,
            'pred_length': 0
        }

    n_pred = len(doc_pred)

    max_gt_len = max(len(g) for g in doc_gt)
    avg_pred_len = sum(len(p) for p in doc_pred) / n_pred if n_pred > 0 else 1

    if avg_pred_len > 0:
        estimated_combo = int(max_gt_len / avg_pred_len * 1.5) + 1
    else:
        estimated_combo = 3

    max_combo_size = min(n_pred, max(2, estimated_combo))
    max_combo_size = min(max_combo_size, 30)

    pred_candidates = []
    for k in range(1, max_combo_size + 1):
        for start in range(n_pred - k + 1):
            indices = frozenset(range(start, start + k))
            text = ' '.join(doc_pred[i] for i in range(start, start + k))
            pred_candidates.append({
                'indices': indices,
                'text': text,
                'length': k
            })

    used_pred = set()
    total_distance = 0

    for gt in doc_gt:
        best_key = None
        best_cand = None
        best_d = None
        for cand in pred_candidates:
            # pred indices cannot be reused
            if cand['indices'] & used_pred:
                continue

            d = editdistance.eval(gt, cand['text'])
            char_len = max(len(cand['text']), 1)
            score = d / char_len          
            key = (score, -char_len)

            if best_key is None or key < best_key:
                best_key = key
                best_cand = cand
                best_d = d
        if best_cand is not None:
            used_pred |= best_cand['indices']
            total_distance += best_d
        else:
            # no valid pred segment left
            total_distance += len(gt)

    gt_len = sum(len(g) for g in doc_gt)
    cer = total_distance / gt_len * 100
    ar = max(0.0, 100.0 - cer)

    return {
        'CER': float(cer),
        'AR': float(ar),
        'edit_distance': int(total_distance),
        'gt_length': gt_len,
        'pred_length': len(' '.join(doc_pred))
    }

def calculate_strict_CER(doc_pred, doc_gt):
    gt_text = ''.join(doc_gt)
    pred_text = ''.join(doc_pred)
    dist = editdistance.eval(pred_text, gt_text)
    cer = dist / len(gt_text) * 100 if len(gt_text) > 0 else 0
    cer = min(cer, 100.0)
    ar = max(0.0, 100.0 - cer)
    return {
        'CER': cer,
        'AR': ar,
        'edit_distance': dist,
        'gt_length': len(gt_text),
        'pred_length': len(pred_text)
    }

def extract_quoted_text(prompt):
    pattern = r'''
        (?<!\\)"(.*?)(?<!\\)"     |   # "..."
        \\\"(.*?)\\\"             |   # \"...\"
        (?<!\\)“(.*?)(?<!\\)”     |   # “...”
    '''
    matches = re.findall(pattern, prompt, flags=re.DOTALL | re.VERBOSE)
    extracted = []
    for group in matches:
        for text in group:
            if text and text.strip():
                extracted.append(text.strip())
                break
    return extracted

def extract_gt_lines(prompt):
    parts = extract_quoted_text(prompt)
    gt_lines = []
    for part in parts:
        for line in part.split("\n"):
            line = line.strip()
            if line:
                gt_lines.append(line)
    return gt_lines

def extract_gt_region(points, image):
    points = np.array(points, dtype=np.int32)
    if len(points) > 2: # 多边形情况
        x, y, w, h = cv2.boundingRect(points)
        roi = image[y:y + h, x:x + w]
        points_shifted = points - [x, y]
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [points_shifted], 255)
        result = np.ones((h, w, 3), dtype=np.uint8) * 255
        result = cv2.bitwise_and(roi, roi, mask=mask) + cv2.bitwise_and(result, result, mask=cv2.bitwise_not(mask))
        new_image = image.copy()
        cv2.fillPoly(new_image, [points], (128, 128, 128))
    else:
        x1, y1 = points[0]
        x2, y2 = points[1]
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        result = image[y1:y2, x1:x2].copy()
        new_image = image.copy()
        new_image[y1:y2, x1:x2] = (128, 128, 128)
    return result, new_image

if not opt.disable_vie:
    from viescore import VIEScore
    # backbone = 'gpt-5-chat-latest'
    backbone = 'gpt-5'
    vie_score_for_t2i = VIEScore(backbone=backbone, task='t2i')
    vie_score_for_lg = VIEScore(backbone=backbone, task='lg')
    vie_score_for_ast = VIEScore(backbone=backbone, task='artistic_st')
    vie_score_for_hst = VIEScore(backbone=backbone, task='historical_st')

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)

lpips_func = lpips.LPIPS(net='alex') 

transform = transforms.Compose([
    transforms.ToTensor()
])

with open('./data/test_cases.json','r',encoding='utf-8') as f:
    test_data = json.load(f)

output_json_path = f'./output/{opt.model}/record.json'
if os.path.exists(output_json_path):
    with open(output_json_path,'r',encoding='utf-8') as f:
        metrics = json.load(f)
    print('loading existing metric record')
else:
    print('creating empty metric record')
    metrics = deepcopy(test_data)

try:
    for i,item in enumerate(test_data):
        if item['task'] == 'T2I' or item['task'] == 'naturally_embedded_T2I':
            img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = img_path
            if not os.path.exists(img_path):
                continue
            if metrics[i].get('metrics') is not None:
                print('skip:',i,img_path)
                continue
            print('evaluating:',i,img_path)
            prompt = item['prompt']
            _, _, overall_score = vie_score_for_t2i.evaluate(img_path, prompt)
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['VIEScore'] = overall_score
            
            if not (item['task'] == 'naturally_embedded_T2I' or (item['task'] == 'T2I' and item['field'] == 'slide')):
                result = ocr.predict(input=img_path)
                if item['field'] == 'historical' and is_vertical_layout(result) and "zh" in os.path.basename(img_path).lower():
                    sorted_result = sort_vertical(result)
                else:
                    sorted_result = sort_paddle_ocr_adaptive(result)
                lines = extract_gt_lines(prompt)
                out = calculate_order_free_CER(sorted_result[0]['rec_texts'],lines)
                metrics[i]['metrics']['AR'] = out['AR']
        elif item['task'] == 'Editing' or item['task'] == 'naturally_embedded_Editing':
            img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = img_path
            if not os.path.exists(img_path):
                continue
            gt_image_path = item['gt_image_path']
            if gt_image_path is None:
                continue
            if metrics[i].get('metrics') is not None:
                print('skip:',i,img_path)
                continue
            if img_path == './output/firered/scene/Editing/zh_3.png':
                import pdb;pdb.set_trace()
            print('evaluating:',i,img_path)
            gt_image = Image.open(gt_image_path).convert('RGB')
            width,height = gt_image.size
            pred_image = Image.open(img_path).convert('RGB').resize((width, height), resample=Image.LANCZOS)
            with torch.no_grad():
                lpips_score = lpips_func(transform(pred_image),transform(gt_image))
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['LPIPS'] = lpips_score.item()

            gt_image_array = np.array(gt_image)
            pred_image_array = np.array(pred_image)
            annotations = item['annotations']
            if annotations is None:
                continue
            
            metrics[i]['metrics']['AR'] = []
            for anno in annotations:
                points = anno['points']
                gt_text = anno['text']
                points = np.array(points)
                # cropped_gt = extract_gt_region(points,gt_image)
                cropped_pred,masked_pred = extract_gt_region(points,pred_image_array)
                # import pdb;pdb.set_trace()
                ocr_result_in = ocr.predict(cropped_pred)
                ocr_result_in = sort_paddle_ocr_adaptive(ocr_result_in)
                ar_in = calculate_strict_CER(ocr_result_in[0]['rec_texts'],gt_text)
                metrics[i]['metrics']['AR'].append(ar_in['AR'])
        elif item['task'] == 'Restoration':
            img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = img_path
            if not os.path.exists(img_path):
                continue
            gt_image_path = item['gt_image_path']
            if gt_image_path is None:
                continue
            if metrics[i].get('metrics') is not None:
                print('skip:',i,img_path)
                continue
            print('evaluating:',i,img_path)
            gt_image = Image.open(gt_image_path).convert('RGB')
            width,height = gt_image.size
            pred_image = Image.open(img_path).convert('RGB').resize((width, height), resample=Image.LANCZOS)
            with torch.no_grad():
                lpips_score = lpips_func(transform(pred_image),transform(gt_image))
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['LPIPS'] = lpips_score.item()
        elif item['task'] == 'Handwriting-Removal' or item['task'] == 'Scene-Text-Removal' or item['task'] == 'Deblurring' or item['task'] == 'Deshadowing' or item['task'] == 'Appearance' or item['task'] == 'Super-Resolution':
            img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = img_path
            if not os.path.exists(img_path):
                continue
            gt_image_path = item['gt_image_path']
            if gt_image_path is None:
                continue
            if metrics[i].get('metrics') is not None:
                print('skip:',i,img_path)
                continue
            print('evaluating:',i,img_path)
            gt_image = Image.open(gt_image_path).convert('RGB')
            width,height = gt_image.size
            pred_image = Image.open(img_path).convert('RGB').resize((width, height), resample=Image.LANCZOS)
            gt_image = transform(gt_image)[None,:]
            pred_image = transform(pred_image)[None,:]
            ms_ssim_value = ms_ssim(gt_image, pred_image, data_range=1.0, size_average=True)
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['MSSSIM'] = ms_ssim_value.item()
        elif item['task'] == 'Layout-Gen':
            org_img_path = item['input_image_path_1']
            img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = img_path
            if not os.path.exists(img_path):
                continue
            prompt = item['prompt']
            if metrics[i].get('metrics') is not None:
                print('skip:',i,img_path)
                continue
            print('evaluating:',i,img_path)
            _, _, overall_score = vie_score_for_lg.evaluate([org_img_path,img_path], prompt)
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['VIEScore'] = overall_score

            result = ocr.predict(input=img_path)
            sorted_result = sort_paddle_ocr_adaptive(result)
            lines = extract_gt_lines(prompt)
            out = calculate_order_free_CER(sorted_result[0]['rec_texts'],lines)
            metrics[i]['metrics']['AR'] = out['AR']
        elif item['task'] == 'Artistic-Style-Transfer':
            input_path1 = item['input_image_path_1']
            output_img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = output_img_path
            if not os.path.exists(output_img_path):
                continue
            if metrics[i].get('metrics') is not None:
                print('skip:',i,input_path1)
                continue
            print('evaluating:',i,output_img_path)
            prompt = item['prompt']
            _, _, overall_score = vie_score_for_ast.evaluate([input_path1,output_img_path], prompt)
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['VIEScore'] = overall_score

            result = ocr.predict(input=output_img_path)
            sorted_result = sort_paddle_ocr_adaptive(result)
            lines = extract_gt_lines(prompt)
            out = calculate_order_free_CER(sorted_result[0]['rec_texts'],lines)
            metrics[i]['metrics']['AR'] = out['AR']
        elif item['task'] == 'Historical-Style-Transfer':
            input_path1 = item['input_image_path_1']
            input_path2 = item['input_image_path_2']
            output_img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = output_img_path
            if not os.path.exists(output_img_path):
                continue
            if metrics[i].get('metrics') is not None:
                print('skip:',i,input_path1,input_path2)
                continue
            print('evaluating:',i,output_img_path)
            prompt = item['prompt']
            _, _, overall_score = vie_score_for_hst.evaluate([input_path1,input_path2,output_img_path], prompt)
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['VIEScore'] = overall_score
        elif item['task'] == 'Dewarping':
            img_path = item['output_path'].replace('holder',opt.model)
            metrics[i]['output_path'] = img_path
            if not os.path.exists(img_path):
                continue
            gt_image_path = item['gt_image_path']
            if gt_image_path is None:
                continue
            if metrics[i].get('metrics') is not None:
                print('skip:',i,img_path)
                continue
            print('evaluating:',i,img_path)
            dd = compute_dd(pred_path=img_path,gt_path=gt_image_path)
            dd = np.exp(-dd.item() / 10)
            metrics[i]['metrics'] = {}
            metrics[i]['metrics']['DD'] = dd
except Exception as e:
    print(e)
finally:
    class Summarizer:
        def normalize_metric(self, value, metric_name, higher_better=True):
            if metric_name == 'VIEScore':
                normalized = value / 10.0
            elif metric_name == 'AR':
                normalized = value / 100.
            elif metric_name == 'LPIPS':
                normalized = 1 - value
            elif metric_name == 'MSSSIM':
                normalized = value
            else:
                normalized = value
            return np.clip(normalized, 0, 1)
        
        def calculate_task_score(self, metrics, task_name):
            metric_values = defaultdict(lambda: defaultdict(list))
            for item in metrics:
                if task_name not in item.get("task"):
                    continue
                if item.get('metrics') is None:
                    continue
                for key, value in item['metrics'].items():
                    if detect_language(item['prompt']) == 'chinese':
                        language_key = 'zh'
                    else:
                        language_key = 'en'
                    if isinstance(value, (int, float)):
                        metric_values[key][language_key].append(value)
                    elif isinstance(value, list):
                        metric_values[key][language_key].append(np.mean(value)) # AR
            scores = []
            zh_scores,en_scores = [],[]
            metric_details = {}

            for metric_name, values in metric_values.items():
                if not values:
                    continue
                avg_value = np.mean(values['zh'] + values['en'])
                zh_avg_value = np.mean(values['zh']) if len(values['zh']) > 0 else 0
                en_avg_value = np.mean(values['en']) if len(values['en']) > 0 else 0
                if metric_name == 'LPIPS':
                    zh_avg_value = np.mean(values['zh']) if len(values['zh']) > 0 else 1
                    en_avg_value = np.mean(values['en']) if len(values['en']) > 0 else 1
                normalized = self.normalize_metric(avg_value, metric_name)
                zh_normalized = self.normalize_metric(zh_avg_value, metric_name)
                en_normalized = self.normalize_metric(en_avg_value, metric_name)
                scores.append(normalized)
                zh_scores.append(zh_normalized)
                en_scores.append(en_normalized)
                metric_details[metric_name] = {
                    "normalized": normalized,
                    "num_samples": len(values),
                    'zh': zh_normalized,
                    'en': en_normalized
                }
            task_score = np.mean(scores) if scores else 0.0
            zh_task_score = np.mean(zh_scores) if scores else 0.0
            en_task_score = np.mean(en_scores) if scores else 0.0
            return task_score, metric_details, zh_task_score, en_task_score
        
        def calculate_overall_score(self, metrics, return_details=False):
            task_scores = {}
            task_language_scores = {'zh': {}, 'en': {}}
            task_details = {}
            task_names = set([t['task'] for t in metrics])
            task_names.remove('naturally_embedded_T2I')
            task_names.remove('naturally_embedded_Editing')
            for task_name in task_names:
                score, details, zh_score, en_score = self.calculate_task_score(metrics, task_name)
                task_scores[task_name] = score
                task_details[task_name] = details
                if zh_score != 0.:
                    task_language_scores['zh'][task_name] = zh_score
                if en_score != 0.:
                    task_language_scores['en'][task_name] = en_score
            
            overall = sum(task_scores.get(task, 0) * 1 for task in task_names) / len(task_names)
            overall_score = overall * 100
            zh_overall_score = sum(task_language_scores['zh'].get(task, 0) * 1 for task in task_language_scores['zh']) / len(task_language_scores['zh']) * 100
            en_overall_score = sum(task_language_scores['en'].get(task, 0) * 1 for task in task_language_scores['en']) / len(task_language_scores['en']) * 100
            if return_details:
                details = {
                    'overall': overall_score,
                    'task_scores': {k: v * 100 for k, v in task_scores.items()},
                    'task_details': task_details
                }
                return overall_score, details, zh_overall_score, en_overall_score
            return overall_score, zh_overall_score, en_overall_score

        def calculate_field_score(self,metrics):
            grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
            for item in metrics:
                field = item["field"]
                task = item["task"]
                if item.get('metrics') is None:
                    continue

                for key, value in item['metrics'].items():
                    if isinstance(value, (int, float)):
                        grouped[field][task][key].append(value)
                    elif isinstance(value, list):
                        grouped[field][task][key].append(np.mean(value)) # AR
            
            metric_details = {}
            for field_name, values in grouped.items():
                if not values:
                    continue
                task_scores = []
                for task in values:
                    scores = []
                    for metric_name in values[task]:
                        avg_value = np.mean(values[task][metric_name])
                        normalized = self.normalize_metric(avg_value, metric_name)
                        scores.append(normalized)
                    task_scores.append(np.mean(scores))
                metric_details[field_name] = np.mean(task_scores)
            return metric_details
        
        def calculate_T2I_Editing_score(self,metrics,task_name='T2I'):
            score_items = list(filter(lambda t:task_name in t['task'],metrics))
            text_types = set([t['field'] for t in score_items])
            if score_items[0].get('metrics') is None:
                return None,None
            field_to_score = {}
            field_to_details = {}
            for text in text_types:
                cur_score_items = list(filter(lambda t:t['field'] == text,score_items))
                score, details, _, _ = self.calculate_task_score(cur_score_items, task_name)
                field_to_score[text] = score
                field_to_details[text] = details
            overall = sum(field_to_score.get(field, 0) for field in field_to_score) / len(field_to_score)
            overall_score = overall * 100
            return overall_score,field_to_details

    with open(output_json_path,'w',encoding='utf-8') as f:
        json.dump(metrics,f,indent=4,ensure_ascii=False)
    
    evaluator = Summarizer()
    overall, task_details, zh_overall_score, en_overall_score = evaluator.calculate_overall_score(metrics, return_details=True)
    field_details = evaluator.calculate_field_score(metrics)
    T2I_overall,T2I_metrics = evaluator.calculate_T2I_Editing_score(metrics,'T2I')
    Editing_overall,Editing_metrics = evaluator.calculate_T2I_Editing_score(metrics,'Editing')
    print('Current testing model:', opt.model)
    print(f'\nOverall Score: {overall:.2f}')
    print(f"\n[Task Breakdown]:")

    for task in natsorted(task_details['task_scores'].keys()):
        metrics_str = ", ".join([f"{m}: {info['normalized'] * 100:.4f}" for m, info in task_details['task_details'].get(task, {}).items()])
        print(f"* {task}: {task_details['task_scores'][task]:.2f} ({metrics_str})")

    print('\n>>> Chinese and English Performance')
    print(f'Overall Score ZH: {zh_overall_score:.2f} Overall Score EN: {en_overall_score:.2f}')
    
    latex_details = task_details['task_details']
    for task in natsorted(task_details['task_scores'].keys()):
        metrics_str = ", ".join([f"{m}: (ZH: {info['zh'] * 100:.2f}, EN: {info['en'] * 100:.2f})" for m, info in task_details['task_details'].get(task, {}).items()])
        print(f"* {task}: {metrics_str}")

    print('\n[Field Breakdown]:')
    for field, score in field_details.items():
        print(f"* {field}: {score * 100:.2f}")

    if T2I_overall is not None and T2I_metrics is not None:
        print('\n[T2I in Different Fields]:')
        print(f'Overall Score: {T2I_overall:.2f}')
        for k in natsorted(T2I_metrics.keys()):
            metrics_str = ", ".join([f"{m}: {info['normalized'] * 100:.4f}" for m, info in T2I_metrics[k].items()])
            print(f'* {k}: {metrics_str}')

    if Editing_overall is not None and Editing_metrics is not None:
        print('\n[Editing in Different Fields]:')
        print(f'Overall Score: {Editing_overall:.2f}')
        for k in natsorted(Editing_metrics.keys()):
            metrics_str = ", ".join([f"{m}: {info['normalized'] * 100:.4f}" for m, info in Editing_metrics[k].items()])
            print(f'* {k}: {metrics_str}')