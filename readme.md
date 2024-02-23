# Maybe, even cooler!
Perhaps, there's a cooler way to utilize models from platforms like Hugging Face and ModelScope more swiftly. Imagine, just with a few lines of code, having the capability of Serverless architecture-based model functionalities in our projects. How amazing that would be!

```python
from serverlessai.maas import modelscope
model_url = "https://modelscope.cn/models/iic/cv_resnet18_card_correction/summary"
ocr = modelscope(model_url, local=True).run("image url")
```
