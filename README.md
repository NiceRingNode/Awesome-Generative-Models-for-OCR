# <div align="center">GPT-4o Image Generation for OCR🚀

<div align="center">
  <a href="http://dlvc-lab.net/lianwen/"> <img alt="SCUT DLVC Lab" src="https://img.shields.io/badge/SCUT-DLVC_Lab-A85882?logo=Academia&logoColor=hsl"></a>
  <a href="./LICENSE"> <img alt="Static Badge" src="https://img.shields.io/badge/License-Apache2.0-FFBF00?logo=GNUBash&logoColor=rgb&labelColor=006622"></a>
<p></p>
</div>

GPT-4o can now [generate images natively](https://openai.com/index/introducing-4o-image-generation/). This repository is about evaluating GPT-4o’s image generation capability on various **Optical Character Recognition (OCR)** tasks. The evaluation include **generating** multiple types of text images (handwritten notes, printed documents, poster, street signs, historical manuscript, etc.) and **editing** specific content of text images. Beyond simple benchmarking, we aim to understand the boundaries of GPT-4o as a general image generation model applied to the specialized field of OCR, identify remaining challenges, and explore **how close we are to achieving AGI-level capabilities in this domain**.

Welcome **issues, PR, and stars** for more comprehensive testing or join us to uncover the potential of GPT-4o for next-gen OCR applications! ✨

## <div align="center">:book:Content</div> <!-- omit in toc -->

- [Slide Image](#slide-image)
- [Modern Document Image](#modern-document-image)
  - [Document Dewarping](#document-dewarping)
  - [Document Deshadowing](#document-deshadowing)
  - [Document Deblur](#document-deblur)
  - [Appearance Enhancement](#appearance-enhancement)
  - [Text Editing](#text-editing)
- [Historical Document Image](#historical-document-image)
  - [T2I Generation](#t2i-generation)
  - [Text Editing](#text-editing-1)
  - [Historical Document Restoration](#historical-document-restoration)
  - [Style Transfer](#style-transfer)
  - [Super Resolution](#super-resolution)
- [Handwritten Text Image](#handwritten-text-image)
  - [T2I Generation](#t2i-generation-1)
    - [Paragraph Level](#paragraph-level)
    - [Line Level](#line-level)
    - [Character (Font) Level](#character-font-level)
    - [Interleaved Image-Text](#interleaved-image-text)
  - [Text Editing](#text-editing-2)
    - [Page Level](#page-level)
    - [Paragraph Level](#paragraph-level-1)
    - [Line Level](#line-level-1)
  - [Handwritten Text Removal](#handwritten-text-removal)
    - [Paragraph Level](#paragraph-level-2)
  - [Style Transfer](#style-transfer-1)
- [Scene Text Image](#scene-text-image)
  - [T2I Generation](#t2i-generation-2)
  - [Text Editing](#text-editing-3)
  - [Scene Text Removal](#scene-text-removal)
- [Artistic Text Image](#artistic-text-image)
  - [T2I Generation](#t2i-generation-3)
    - [Line Level](#line-level-2)
    - [Character (Font) Level](#character-font-level-1)

## <div align="center">:milky_way:Slide Image</div> <!-- omit in toc -->

| Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| A highly detailed and visually rich PowerPoint slide in a modern and professional style, featuring a bold English title at the top, multiple content blocks with varied font sizes including bullet points, short paragraphs, and highlighted keywords. The slide includes colorful icons, infographic-style illustrations, and a blend of clean vector graphics with hand-drawn sketch elements. A vertical sidebar shows a step-by-step process or timeline, and a small pie chart or data visualization is placed in one corner, labeled in English. The background is subtle, with a soft gradient or abstract texture that enhances readability without distraction. The overall layout is well-balanced, with clear structure, effective use of whitespace, and a harmonious color palette. The slide should appear as a fully finished presentation page with meaningful English content, refined typography, and polished visual composition. | EN       | <p align="center"><img src="./images/slide/en-output.png" width=100%></p> | ✅<br>Most requirements fulfilled.                            |
| Generate a visually stunning and informative PowerPoint slide. The slide should be meticulously designed with a sophisticated layout, incorporating a diverse range of elements. <br />Text: Include well-written, concise English text in a professional font (e.g., Arial, Calibri, Times New Roman). The text should be logically organized and easy to read, with a clear title and supporting bullet points or short paragraphs.<br />Illustrations: Integrate intricate patterns, detailed drawings, and artistic paintings. These visual elements should be relevant to the text and enhance the overall message of the slide. Consider using a consistent color palette to create a harmonious aesthetic.<br />Layout: The slide should have a balanced and visually appealing layout. Experiment with different arrangements of text and images to create a dynamic and engaging design. Use whitespace effectively to avoid clutter.<br />Details: Pay attention to fine details such as shadows, gradients, and textures to add depth and realism to the image. The overall impression should be one of high quality and professionalism. | EN       | <p align="center"><img src="./images/slide/en-output2.png" width=100%></p> | ✅<br/>Most requirements  in the prompt are fulfilled.        |
| 一张视觉精美、信息丰富的长方形PPT幻灯片，主题为“未来科技与智能城市”。风格现代、科技感十足，整体排版清晰、专业，结构完整。幻灯片顶部是用中文写成的大标题“未来科技的城市图景”，使用无衬线字体，醒目现代。页面中部包含多个内容区域，展示有关智能交通系统、自动驾驶、物联网（IoT）、5G 网络基础设施等信息，每个部分配有简洁的中文段落说明和要点列表，如“智慧交通”、“数据中心”、“无人配送系统”等关键词以加粗或高亮方式呈现。页面中配有简洁清晰的图标、线条风格的插图、未来城市的建筑草图、以及科技设备的概念图。右下角是一个中文标注的数据图表（如柱状图或环形图）。背景为深蓝或渐变色调，带有抽象科技纹理。整体配色高对比，布局平衡有序，图文并茂，幻灯片应为完整内容，不能有留白或模板感。 | ZH       | <p align="center"><img src="./images/slide/zh-output.png" width=100%></p> | 🤔<br>Partially correct. Large text is good but smaller text is chaotic. |

## <div align="center">📄Modern Document Image</div> <!-- omit in toc -->

#### Document Dewarping

| Input Image                                                  | Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/document/dewarping-en-input.png" width=100%></p> | Please perform dewarping on this document to make it flat and clear. | EN       | <p align="center"><img src="./images/document/dewarping-en-output.png" width=100%></p> | ❌<br>Texts are chaotic and blurred. Three columns become two columns. |
| <p align="center"><img src="./images/document/dewarping-en-input2.png" width=100%></p> | Please perform dewarping on this document to make it flat and clear. | EN       | <p align="center"><img src="./images/document/dewarping-en-output2.png" width=100%></p> | ❌<br/>Embedded drawing is not correctly restored. Partial Texts are blurred. |
| <p align="center"><img src="./images/document/dewarping-zh-input.png" width=100%></p> | 请帮我把这张图片中的文档矫正成一张平铺、清晰的文档           | ZH       | <p align="center"><img src="./images/document/dewarping-zh-output.png" width=100%></p> | ❌<br/>Only the large text is good. Small text is incompletely restored and blurred. |
| <p align="center"><img src="./images/document/dewraping-zh-input2.jpg" width=100%></p> | 裁剪出演唱会的票                                             | ZH       | <p align="center"><img src="./images/document/dewraping-zh-output2.png" width=100%></p> | 🤔<br/>Direction is correct. The Chinese text is visual-like but meaningless. |
| <p align="center"><img src="./images/document/dewraping-zh-input3.jpg" width=100%></p> | 裁剪出票据                                                   | ZH       | <p align="center"><img src="./images/document/dewraping-zh-output3.png" width=100%></p> | 🤔<br/>Only the large text is good. Small text is blurred or lacks semantic. |

#### Document Deshadowing

| Input Image                                                  | Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/document/deshadowing-en-input.jpg" width=100%></p> | 请帮我去掉这张文档图片中的阴影                               | EN       | <p align="center"><img src="./images/document/deshadowing-en-output.png" width=100%></p> | 🤔<br/>Shadows are removed. But the image is over-rectified.  |
| <p align="center"><img src="./images/document/deshadowing-en-input2.jpg" width=100%></p> | Process this document image to eliminate shadow artifacts and produce a clean, evenly lit version. | LA       | <p align="center"><img src="./images/document/deshadowing-en-output2.png" width=100%></p> | 🤔<br/>Partially good. Shadows are removed. But texts are wrong. |
#### Document Deblur

| Input Image                                                  | Prompt                                              | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | --------------------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/document/deblur-en-input.png" width=100%></p> | Deblur this document image to enhance text clarity. | EN       | <p align="center"><img src="./images/document/deblur-en-output.png" width=100%></p> | 🤔<br/>Partially good. Texts are clear but unwanted content has been automatically added. |
#### Appearance Enhancement

| Input Image                                                  | Prompt                                            | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ------------------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/document/appearance-enhancement-zh-input.jpg" width=100%></p> | 请帮我增强这张文档图像，输出一个类似pdf的清晰文档 | ZH       | <p align="center"><img src="./images/document/appearance-enhancement-zh-output.png" width=100%></p> | 🤔<br/>Partially good. Enhanced appearance, but the table below wasn't in the input. |

#### Text Editing

| Input Image                                                  | Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| <p align="center"><img src="./images/document/text-editing-en-input.png" width=100%></p> | Please change the text "Stage 1: Domain-Specific Categorization" into "This is a paper of Qwen2.5-VL" | EN       | <p align="center"><img src="./images/document/text-editing-en-output.png" width=100%></p> | 🤔<br/>Modified successfully but some contents are missed. |
| <p align="center"><img src="./images/document/text-editing-en-input2.jpg" width=100%></p> | change "7.30pm" to "11.45 am"                                | EN       | <p align="center"><img src="./images/document/text-editing-en-output2.png" width=100%></p> | 🤔<br/>Modified successfully but some contents are missed. |
| <p align="center"><img src="./images/document/text-editing-zh-input.jpg" width=100%></p> | 帮我将图中的“人工智能”改为“深度学习”，“PyTorch”改为“TensorFlow” | ZH       | <p align="center"><img src="./images/document/text-editing-zh-output.png" width=100%></p> | 🤔<br/>Modified successfully but some contents are missed. |
| <p align="center"><img src="./images/document/text-editing-zh-input2.jpg" width=100%></p> | 将价格改为21.88                                              | ZH       | <p align="center"><img src="./images/document/text-editing-zh-output2.png" width=100%></p> | 🤔<br/>Modified successfully but some contents are missed. |

## <div align="center">📜Historical Document Image</div> <!-- omit in toc -->

### T2I Generation

| Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 生成一页中国古代书籍，泛黄的旧纸张，竖排的中文毛笔书法，传统木刻印刷风格，精美的边框，纸张边缘磨损，有古旧质感，明清风格，高细节，写实光影，从上往下的视角 | ZH       | <p align="center"><img src="./images/historical/t2i-generation-zh-output.png" width=100%></p> | ✅<br/>Requirements fulfilled.                                |
| 一张古籍书页的特写，纸张泛黄，带有明显的岁月痕迹。页面上书写着毛笔字，内容是《道德经》的第一章：“道可道，非常道；名可名，非常名。无名，天地之始；有名，万物之母。” 字迹工整，但部分笔画略有模糊。页面边缘有虫蛀的痕迹，并有一些墨迹晕染开来。背景是深色的木质书桌，桌面上散落着一些毛笔、砚台和镇纸。光线昏暗，从左上方照射下来，营造出一种古老而神秘的氛围。 | ZH       | <p align="center"><img src="./images/historical/t2i-generation-zh-output2.png" width=100%></p> | 🤔<br/>Most requirements are fulfilled but the content is incomplete and incorrect. |
| 生成三页连续的《史记·项羽本纪》古籍书页图片。书页采用明代风格，使用仿古宣纸，纸张略微泛黄，带有轻微的墨迹晕染。字体为工整的小楷，页面排版为传统的竖排版式，每页约20行，每行约15字。 书页边缘有轻微的磨损和虫蛀痕迹，但整体保存完好。背景为深色木质书桌，桌面干净整洁，仅有一盏古朴的油灯提供照明。光线柔和，营造出一种宁静而庄重的氛围。 请确保三页书页的风格、字体、纸张材质、墨迹晕染程度等细节保持高度一致，使它们看起来像是同一本书的连续页面。 | ZH       | <p align="center"><img src="./images/historical/t2i-generation-zh-output3.png" width=100%></p> | 🤔<br/>Most requirements fulfilled. But the content is not Chinese and its language is unidentified. |
| Generate a close-up image of an aged manuscript page written in English. The page is made of thick, parchment-like material, yellowed with age and showing subtle signs of wear and tear. The text is written in a formal, calligraphic script reminiscent of the 16th century, with ornate capital letters and flowing lines.<br />The text on the page is an excerpt from Shakespeare's Hamlet, Act 1, Scene 2, starting with the line: "O, that this too too solid flesh would melt, Thaw and resolve itself into a dew!" and continuing for several lines.<br />The page has faint water stains and minor ink smudges, adding to its aged appearance. The edges are slightly frayed and uneven. The background is a dark, out-of-focus surface, perhaps a wooden table or leather-bound book. The lighting is soft and diffused, creating a sense of antiquity and scholarly atmosphere.<br />Ensure the script is legible but clearly handwritten, not a modern font. The overall impression should be that of a genuine historical document. | EN       | <p align="center"><img src="./images/historical/t2i-generation-en-output.png" width=100%></p> | ✅<br/>Requirements fulfilled.                                |

### Text Editing

| Input Image                                                  | Prompt                                         | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ---------------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/historical/text-editing-en-input.jpg" width=100%></p> | Modify "CONGRESS" to "COVERING".               | EN       | <p align="center"><img src="./images/historical/text-editing-en-output.png" width=100%></p> | ✅<br/>Requirements fulfilled despite super-resolution is accidentally performed. |
| <p align="center"><img src="./images/historical/text-editing-zh-input.jpg" width=100%></p> | 将图片中的“所有不可得意界”修改成“今天天气很好” | ZH       | <p align="center"><img src="./images/historical/text-editing-zh-output.png" width=100%></p> | ❌<br/>Modifications incorrect and other texts are incorrect. |

### Historical Document Restoration

| Input Image                                                  | Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/historical/resotration-zh-input.png" width=100%></p> | 修复这张古籍图片中破损和缺失的文字                           | ZH       | <p align="center"><img src="./images/historical/resotration-zh-output.png" width=100%></p> | ❌<br/>Restoration failed. Original contents are changed and incorrect background. |
| <p align="center"><img src="./images/historical/resotration-zh-input2.png" width=100%></p> | 修复这张古籍图片中破损和缺失的文字，保持文字风格相同以及背景一致 | ZH       | <p align="center"><img src="./images/historical/resotration-zh-output2.png" width=100%></p> | ❌<br/>Restoration totally failed.                            |

### Style Transfer

| Input Image1                                                 | Input Image 2                                                | Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                   |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | --------------------------------------- |
| <p align="center"><img src="./images/historical/style-transfer-zh-input1.png" width=100%></p> | <p align="center"><img src="./images/historical/style-transfer-zh-input2.jpg" width=100%></p> | 请将第二张古籍图片的风格迁移到第一张古籍上，包括背景颜色、字体样式、笔画粗细等等。 | EN       | <p align="center"><img src="./images/historical/style-transfer-zh-output.png" width=100%></p> | ❌<br/>Style and content totally incorrect. |

### Super Resolution

| Input Image                                                  | Prompt                                  | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | --------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/historical/super-resolution-en-input.jpg" width=100%></p> | Perform super-resolution on this image. | EN       | <p align="center"><img src="./images/historical/super-resolution-en-output.png" width=100%></p> | ✅<br/>Requirements fulfilled despite some texts are cropped. |

## <div align="center">:pencil2:Handwritten Text Image</div> <!-- omit in toc -->

### T2I Generation

#### Paragraph Level

| Prompt                                                       | Language | Output Image                                                 | Correctness & Quality |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | --------------------- |
| 请给我生成一张手写文字图片，内容是“ICDAR是文档分析与识别领域的顶级会议。在数字化转型时代，这一领域的重要性日益凸显。该旗舰会议的第19届将于2025年9月16日至21日在中国武汉举行。”，要求书写风格潦草。 | ZH       | <p align="center"><img src="./images/handwritten/paragraph-t2i-generation-zh-output.png" width=100%></p> | ✅<br/>Well done!      |

#### Line Level

| Prompt                                                       | Language | Output Image                                                 | Correctness & Quality |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | --------------------- |
| Please generate an image with handwritten text that says: "OpenCV is open source, contains over 2500 algorithms, and is operated by the non-profit Open Source Vision Foundation." The handwriting style should be scribbled. | EN       | <p align="center"><img src="./images/handwritten/line-t2i-generation-en-output.png" width=100%></p> | ✅<br/>Well done!      |

#### Character (Font) Level

| Prompt                                       | Language | Output Image                                                 | Correctness & Quality         |
| -------------------------------------------- | -------- | ------------------------------------------------------------ | ----------------------------- |
| Please generate a handwritten character "P". | EN       | <p align="center"><img src="./images/handwritten/character-t2i-generation-en-output.png" width=20%></p> | ✅<br/>Requirements fulfilled. |
| 生成一个手写汉字“天”，风格任意               | ZH       | <p align="center"><img src="./images/handwritten/character-t2i-generation-zh-output.png" width=20%></p> | ✅<br/>Requirements fulfilled. |

#### Interleaved Image-Text

| Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Generate a hand-drawn physics diagram illustrating the law of reflection: 1. A flat horizontal surface representing a mirror. 2. An incident ray approaching the surface at an angle, drawn with an arrow. 3. A reflected ray bouncing off the surface symmetrically, also with an arrow. 4. A normal line drawn perpendicular to the surface at the point of incidence. 5. Clear angle markings: the angle of incidence (labeled as θᵢ) and the angle of reflection (labeled as θᵣ) 6. Degree values annotated next to the angles (e.g., 45°). 7. Dashed lines used as angle guides (from rays to the normal). 8. All elements labeled with clean, handwriting-style text. 9. Overall style: hand-drawn, minimalistic, like a whiteboard or notebook sketch. 10. Background: plain white or paper texture; no photographic elements. | EN       | <p align="center"><img src="./images/handwritten/interleaved-t2i-generation-output.png" width=100%></p> | ✅<br/>Requirements fulfilled despite the vertical line shifts from the center. |

### Text Editing

#### Page Level

| Input Image                                                  | Prompt                                                 | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/handwritten/page-text-editing-en-input.jpg" width=100%></p> | Erase text "Football, cricket, running" in this image. | EN       | <p align="center"><img src="./images/handwritten/page-text-editing-en-output.png" width=100%></p> | ❌<br/>Text not edited. Light, drawings, and background color change. |

#### Paragraph Level

| Input Image                                                  | Prompt                                                   | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | -------------------------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/handwritten/paragraph-text-edit-zh-input.png" width=100%></p> | 请将文字“演讲的力量”修改为“讲话的力量”。其他文字保持不变 | ZH       | <p align="center"><img src="./images/handwritten/paragraph-text-edit-zh-output.png" width=100%></p> | 🤔<br/>Partially correct. Modified successfully but the image becomes square and some texts are cropped. |

#### Line Level

| Input Image                                                  | Prompt                                      | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ------------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/handwritten/line-text-editing-en-input.jpg" width=100%></p> | Change "similarities" to "functionalities". | EN       | <p align="center"><img src="./images/handwritten/line-text-editing-en-output.png" width=100%></p> | 🤔<br/>Partially correct. Modified successfully, but the image is squared, and some text is cropped. Clarity unexpectedly improve. |

### Handwritten Text Removal

#### Paragraph Level

| Input Image                                                  | Prompt                                     | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/handwritten/paragraph-handwritten-text-removal-zh-input.jpg" width=100%></p> | 请擦除这张图片中所有的手写笔迹             | ZH       | <p align="center"><img src="./images/handwritten/paragraph-handwritten-text-removal-zh-output.png" width=100%></p> | ❌<br/>Totally failed.                                        |
| <p align="center"><img src="./images/handwritten/handwritten-text-removal-zh-input_2.png" width=100%></p> | 将"高考加油鸭"这句话擦除                   | ZH       | <p align="center"><img src="./images/handwritten/handwritten-text-removal-zh-output_2.png" width=100%></p> | 🤔<br/>Partially good. Successful removal. But the image is squared. Clarity unexpectedly improve. |
| <p align="center"><img src="./images/handwritten/paragraph-handwritten-text-removal-en-input.jpg" width=100%></p> | Remove all handwritten text in this image. | EN       | <p align="center"><img src="./images/handwritten/paragraph-handwritten-text-removal-en-output.png" width=100%></p> | 🤔<br/>Partially good. Successful removal. But the image is squared. Drawings unexpectedly change. |

### Style Transfer

| Input Image                                                  | Prompt                                     | Language | Output Image                                                 | Correctness & Quality         |
| ------------------------------------------------------------ | ------------------------------------------ | -------- | ------------------------------------------------------------ | ----------------------------- |
| <p align="center"><img src="./images/artistic/line-style-transfer-zh-input.png" width=100%></p> | 参照图中的汉字风格，生成“一起去旅行”这句话 | ZH       | <p align="center"><img src="./images/artistic/line-style-transfer-zh-output.png" width=100%></p> | ✅<br/>Requirements fulfilled. |
| <p align="center"><img src="./images/artistic/line-style-transfer-zh-input_2.png" width=100%></p> | 参照图中的汉字风格，生成“一起去旅行”这句话 | ZH       | <p align="center"><img src="./images/artistic/line-style-transfer-zh-output_2.png" width=100%></p> | ✅<br/>Requirements fulfilled. |

## <div align="center">📷Scene Text Image</div> <!-- omit in toc -->

### T2I Generation

| Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Create a street sign image with text "Tomorrow".             | EN       | <p align="center"><img src="./images/scene/t2i-generation-en-output.png" width=100%></p> | ✅<br/>Requirements fulfilled.                                |
| 生成一个街上商店的招牌，内容是“超级市场”。                   | ZH       | <p align="center"><img src="./images/scene/t2i-generation-zh-output.png" width=100%></p> | ✅<br/>Requirements fulfilled.                                |
| A bustling cyberpunk night market in a futuristic Asian metropolis, glowing with neon signs in multiple languages (Chinese, Japanese, Korean, Arabic, and English). The scene is filled with dense fog, reflections on wet pavement, flying cars above, and diverse crowds walking under neon umbrellas. Holographic advertisements float in the air, including a large glowing sign that reads "梦境集市" ("Dream Bazaar") in stylized Chinese calligraphy. Other floating signs display dynamic digital text such as "Now Open!", "未来食品", and "Quantum Noodles". The atmosphere is vibrant, chaotic, and immersive, with dramatic lighting and cinematic composition. Ultra-detailed, 4K, concept art style, with a blend of Blade Runner and Ghost in the Shell aesthetics. | Mixed    | <p align="center"><img src="./images/scene/t2i-generation-mixed-output.png" width=100%></p> | ✅<br/>Most requirements fulfilled. High quality. But some Chinese texts are incorrect or lack semantic. |

### Text Editing

| Input Image                                                  | Prompt                                          | Language | Output Image                                                 | Correctness & Quality                                        |
| ------------------------------------------------------------ | ----------------------------------------------- | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <p align="center"><img src="./images/scene/word-scene-text-editing-en-input.jpg" width=100%></p> | Change "2011" to "3120" and "MAPLES" to "LEAF". | EN       | <p align="center"><img src="./images/scene/word-scene-text-editing-en-output.png" width=100%></p> | 🤔<br/>Partially good. Successful removal. But the image is squared. Color unexpectedly brighten. |

### Scene Text Removal

| Input Image                                                  | Prompt                           | Language | Output Image                                                 | Correctness & Quality                                       |
| ------------------------------------------------------------ | -------------------------------- | -------- | ------------------------------------------------------------ | ----------------------------------------------------------- |
| <p align="center"><img src="./images/scene/word-scene-text-removal-en-input.jpg" width=100%></p> | Erase the "BEACH" in this image. | EN       | <p align="center"><img src="./images/scene/word-scene-text-removal-en-output.png" width=100%></p> | ✅<br/>Requirements fulfilled despite some details are lost. |
| <p align="center"><img src="./images/scene/word-scene-text-removal-en-input2.jpg" width=100%></p> | Erase all text in this image.    | EN       | <p align="center"><img src="./images/scene/word-scene-text-removal-en-output2.png" width=100%></p> | ✅<br/>Requirements fulfilled despite the image is squared.  |

## <div align="center">:rainbow:Artistic Text Image</div> <!-- omit in toc -->

### T2I Generation

#### Line Level

| Prompt                                                       | Language | Output Image                                                 | Correctness & Quality                                       |
| ------------------------------------------------------------ | -------- | ------------------------------------------------------------ | ----------------------------------------------------------- |
| Generate a line of artistic text with intricate details, creative typography, and visual appeal, ensuring that each character has a different color. The font should have a unique aesthetic, incorporating elegant curves, bold strokes, or decorative elements. The text content should be: 'OpenCV is open source, contains over 2500 algorithms, and is operated by the non-profit Open Source Vision Foundation.' | EN       | <p align="center"><img src="./images/artistic/line-t2i-generation-en-output.png" width=100%></p> | 🤔<br/>Partially good. Some texts are incorrect.             |
| 生成一行具有复杂细节、创意排版和视觉吸引力的艺术文本，要求每一个文字的颜色都不相同，字体应具有独特的美感，融入优雅的曲线、粗犷的笔触或装饰元素。文本的内容为“生活就像海洋，只有意志坚强的人才能到达彼岸”。 | ZH       | <p align="center"><img src="./images/artistic/line-t2i-generation-zh-output.png" width=100%></p> | 🤔<br/>Partially good. Some texts are incorrect.             |
| 生成一行具有复杂细节、创意排版和视觉吸引力的艺术文本，要求每一个文字的颜色都不相同，字体应具有独特的美感，融入优雅的曲线、粗犷的笔触或装饰元素。文本的内容为“龒厵䨫巴邑䶕脀勧忄”。 | ZH       | <p align="center"><img src="./images/artistic/line-t2i-generation-zh-output2.png" width=100%></p> | ❌<br/>Totally failed. Unable to handle complex Chinese text |

#### Character (Font) Level

| Prompt                                | Language | Output Image                                                 | Correctness & Quality         |
| ------------------------------------- | -------- | ------------------------------------------------------------ | ----------------------------- |
| Please generate an artistic font "A". | EN       | <p align="center"><img src="./images/artistic/character-t2i-generation-en-output.png" width=20%></p> | ✅<br/>Requirements fulfilled. |
| 请生成一个艺术字，内容为“瀧”。        | ZH       | <p align="center"><img src="./images/artistic/character-t2i-generation-zh-output.png" width=20%></p> | ✅<br/>Requirements fulfilled. |

## <div align="center">Contact</div> <!-- omit in toc -->

eeprzhang@mail.scut.edu.cn

## <div align="center">Acknowledgement<!-- omit in toc -->

[Peirong Zhang🐲](https://github.com/NiceRingNode), [Haowei Xu🔥](https://github.com/shallweiwei), [Guitao Xu😿](https://github.com/guitaoxu).

Copyright 2025, [Deep Learning and Vision Computing (DLVC) Lab](http://www.dlvc-lab.net), South China China University of Technology. 
