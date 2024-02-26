"""
The current file is used to configure default resource properties/configurations;
func name regex: {maas_class_name}_{vendor_class_name}_default_config (all letters in lowercase)
  like: modelscope_alibaba_default_config
:param: name: default resource name
:param: config: user specified configuration
:return: specific configuration information that will be used to create resources
"""

def modelscope_alibaba_default_config(name, config):
    """
    get modelscope alibaba function config
    :param name: function name
    :param config: user config
    :return: config
    """

    return {
        "cpu": 0.05,
        "customContainerConfig": {},
        "description": "Serverless AI Project, {model_id}-{model_version}",
        "environmentVariables": {},
        "gpuConfig": {
        },
        "role": "",
        "runtime": "custom-container",
        "timeout": 300,

    }
