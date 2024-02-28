from maas import Modelscope

modelscope_attr = Modelscope(
    "https://modelscope.cn/models/iic/cv_convnextTiny_ocr-recognition-general_damo/summary"
)
modelscope_attr.invoke(
    {
        "input": {
            "image": "http://modelscope.oss-cn-beijing.aliyuncs.com/demo/images/image_ocr_recognition.jpg"
        }
    }
)
