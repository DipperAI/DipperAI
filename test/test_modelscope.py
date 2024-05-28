from maas import Modelscope

if __name__ == '__main__':
    modelscope = Modelscope(
        model_id="damo/nlp_structbert_sentiment-classification_chinese-ecommerce-base",
        # service_config={
        #     "parameters": {
        #         "gpuMemorySize": "15360",
        #         "memorySize": "30720"
        #     }
        # }
    )
    print(modelscope.invoke({"input": "你好"}))
