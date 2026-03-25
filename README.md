# <div align="center" id="awesome image generators">OCRGenBench: A Comprehensive Benchmark for Evaluating OCR Generative Capabilities🚀</div>

<div align="center">
  <a href="http://dlvc-lab.net/lianwen/"> <img alt="SCUT DLVC Lab" src="https://img.shields.io/badge/SCUT-DLVC_Lab-A85882?logo=Academia&logoColor=hsl"></a>
  <a href="https://arxiv.org/abs/2507.15085"> <img alt="Static Badge" src="https://img.shields.io/badge/arXiv-2507.15085-%23CE0000?logo=arXiv&logoColor=rgb&labelColor=gray"></a>
  <a href="https://huggingface.co/papers/2507.15085"> <img alt="Static Badge" src="https://img.shields.io/badge/HuggingFace-Paper-FFBF00?logo=HuggingFace&logoColor=rgb&labelColor=gray"></a>
  <a href="./LICENSE"> <img alt="Static Badge" src="https://img.shields.io/badge/License-Apache2.0-008844?logo=GNUBash&logoColor=rgb&labelColor=gray"></a>
<p></p>
<img src="https://img.shields.io/github/stars/NiceRingNode/Awesome-Generative-Models-for-OCR?color=yellow" alt="Stars"> <img src="https://img.shields.io/github/forks/NiceRingNode/Awesome-Generative-Models-for-OCR?color=yellow" alt="Forks">

<p align="center">
    <img src="asset/logo.png" width="500">
</p>

<a href="https://arxiv.org/abs/2507.15085"> <b>OCRGenBench: A Comprehensive Benchmark for Evaluating OCR Generative Capabilities</b> </a>

</div>

**OCRGenBench** is the most comprehensive benchmark to date for evaluating the OCR generative capabilities of generative models. It pioneers in the unification of T2I generation, text editing, and OCR-related image-to-image translation to universally reflect a model's visual text synthesis abilities, *i.e.*, OCR generative capabilities. The benchmark covers 5 common text categories and 33 OCR generative tasks, including 1,060 challenging, human-annotated samples with dense text, varied layouts, multiple aspect ratios, and bilingual content. We also design a unified metric OCRGenScore, assessing text accuracy, instruction following, visual quality, and structural consistency in visual text synthesis.

> *This repository was formerly known as **Awesome Generative Models for OCR**, and included only the empirical evaluation of image generation capabilities of 7 models. Now we expand empirical evaluation to a **benchmark** and an evaluation framework, facilitating reproducible evaluation on unlimited models.*

# <div align="center" id="news"> 📃News</div> <!-- omit in toc -->

### 📌Pinned

- :tada: **[March 2026]​** We propose **OCRGenBench**, a comprehensive benchmark to evaluate multi-dimensional OCR generative capabilities (visual text synthesis capbilities).

- :tada: **[August 2025]** We have included the evaluation of [Qwen-Image](https://github.com/QwenLM/Qwen-Image), and the results will be soon upated to the paper.

- :tada: **[July 2025]** Our [paper](https://arxiv.org/abs/2507.15085) is online at arXiv! Welcome citation and star if you found our work useful! :blush:

- :fire: **[June 2025]** Expanded evaluation now includes various closed-source and **open-source** models!

- 📢 **[March 2025]** Initial evaluation of GPT-4o's image generation capabilities now available!

## <div align="center" id="citation">🍺Data Categorization</div><!-- omit in toc -->

OCRGenBench encompasses five major text scenarios and 33 OCR generative tasks (including T2I generation, text editing, and OCR I2I translation tasks). The categorization is shown below:

![img](./asset/mindmap.png)

## <div align="center" id="citation">🍨Data Distribution</div><!-- omit in toc -->

OCRGenBench includes 1,060 high quality, manually annotated samples, whose distribution is shown as follows:

![img](./asset/example.png)

## <div align="center" id="citation">🎓Leaderboard</div><!-- omit in toc -->

> **Performance across task (main leaderboard)**

![img](./asset/task1.png)

![img](./asset/task2.png)
---
> Performance across text categories

![img](./asset/category.png)
---
> Performance across different T2I generation tasks

![img](./asset/only_gen.png)
---
> Performance across different text editing tasks

![img](./asset/only_editing.png)
---
> Performance across different tasks in Chinese and English

![img](./asset/zh_en1.png)

![img](./asset/zh_en2.png)

## <div align="center" id="citation">📋Citation</div> <!-- omit in toc -->

If you find our work helpful, please cite our paper:

```bibtex
@article{zhang2025ocrgenbench,
  title={{OCRGenBench: A Comprehensive Benchmark for Evaluating OCR Generative Capabilities}},
  author={Zhang, Peirong and Xu, Haowei and Zhang, Jiaxin and Zheng, Xuhan and Xu, Guitao and Zhang, Yuyi and Liu, Junle and Yang, Zhenhua and Zhou, Wei and Jin, Lianwen},
  journal={arXiv preprint arXiv:2507.15085},
  year={2025}
}
```

## <div align="center" id="contact">:e-mail:Contact</div> <!-- omit in toc -->

eeprzhang@mail.scut.edu.cn

## <div align="center" id="acknowledgement">🌊Acknowledgement<!-- omit in toc -->

Copyright 2025-2026, [Deep Learning and Vision Computing (DLVC) Lab](http://www.dlvc-lab.net), South China China University of Technology.

## <div align="center" id="star">⭐Star History<!--omit in toc -->

[![Star Rising](https://api.star-history.com/svg?repos=NiceRingNode/Awesome-Generative-Models-for-OCR&type=Timeline)](https://star-history.com/#NiceRingNode/Awesome-Generative-Models-for-OCR&Timeline)



