import os
import time

from alibabacloud_devs20230714 import models
from alibabacloud_devs20230714.client import Client
from alibabacloud_tea_openapi.models import Config

prefix_to_func = {
    "dipperai-huggingface": "model_app_func",
    "dipperai-modelscope": "tgpu_basic_func"
}


class Devs:
    def __init__(self, access_key_id=None, access_key_secret=None, account_id=None, region=None, logger=None):
        """Initialize the Alibaba class with the provided parameters or environment variables.
        :param access_key_id: Alibaba Cloud Access Key ID
        :param access_key_secret: Alibaba Cloud Access Key Secret
        :param account_id: Alibaba Cloud Account ID
        :param region: Alibaba Cloud Region ID
        :param logger: Logger for the Alibaba class
        """
        access_key_id = access_key_id or os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
        access_key_secret = access_key_secret or os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        account_id = account_id or os.environ.get("FC_ACCOUNT_ID")
        self.region = region or os.environ.get("FC_REGION", "cn-hangzhou")

        if not (access_key_id and access_key_secret and account_id):
            raise ValueError("Access Key ID, Access Key Secret, and Account ID must be provided")

        self.role_arn = f"acs:ram::{account_id}:role/aliyundevscustomrole"

        config = Config(access_key_id=access_key_id, access_key_secret=access_key_secret)
        config.endpoint = f"devs.{self.region}.aliyuncs.com"
        self._client = Client(config)
        self.logger = logger

    def create(self, name, config) -> dict:
        """
        Create a new project using the Alibaba Serverless Devs Python SDK.
        :param name: Name of the project to be created.
        :param config: Configuration dictionary for the project.
        :return: A dictionary with the project details if creation and readiness checks succeed.
        """
        # Check if the deployment already exists
        model = self.check_model_status(name)
        if model:
            return model
        if not self._create_or_update(name, config, creating=True):
            return {}
        return self.check_model_status(name)

    def update(self, name, config) -> dict:
        """
        Update an existing project to the specify config.
        :param name: Name of the project to update.
        :param config: Configuration dictionary for the project.
        :return: A dictionary with the project details if the update and readiness checks succeed.
        """
        if not self._create_or_update(name, config, creating=False):
            return {}
        return self.check_model_status(name)

    def _create_or_update(self, name, config, creating=True) -> bool:
        """
        Helper function to create or update a project.
        :param name: The project name.
        :param config: Configuration dictionary for the project.
        :param creating: Boolean indicating if this is a creation (True) or an update (False) operation.
        :return: True if the operation succeeded, False otherwise.
        """
        try:
            project_spec = models.ProjectSpec(
                role_arn=self.role_arn,
                template_config=models.TemplateConfig(
                    template_name=config["template_name"],
                    parameters=config["parameters"]
                )
            )
            project = models.Project(name=name, spec=project_spec)
            self.logger.info(f"{'Creating' if creating else 'Updating'} model: {name}")
            if creating:
                req = models.CreateProjectRequest(body=project)
                resp = self._client.create_project(req).to_map()
            else:
                req = models.UpdateProjectRequest(body=project)
                resp = self._client.update_project(name, req).to_map()

            if resp["statusCode"] != 200:
                raise Exception(f"Failed to {'create' if creating else 'update'} model: {name}")
            self.logger.info(f"{'Created' if creating else 'Updated'} model successfully: {name}.")
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def check_model_status(self, name) -> dict:
        """
        Helper function to check project readiness using an exponential backoff strategy.
        :param name: The project name.
        :return: A dictionary with the project details if the project is ready; otherwise, an empty dictionary.
        """
        attempt = 0
        max_attempts = 45
        sleep_interval = 40
        while attempt < max_attempts:
            try:
                release_info = self.get_release_info(name)
                # If the project does not exist, return immediately
                if not release_info:
                    return {}
                if release_info.get("bizStatus") == "Failed":
                    raise Exception(f"Model {name} deploy failure.")
                if release_info.get("bizStatus") == "Finished":
                    return self._process_release_info(name, release_info)
            except Exception as e:
                self.logger.error(f"Failed to check model readiness: {e}")
                return {}
            attempt += 1
            time.sleep(sleep_interval)
        self.logger.error(f"Model {name} is not ready, but it is still being deployed, please try again later.")
        return {}

    def _process_release_info(self, name, release_info) -> dict:
        """
        Helper function to process release information.
        :param release_info: The release information to process.
        :return: A processed dictionary with project details.
        """
        main_func = None
        for prefix, func in prefix_to_func.items():
            if name.startswith(prefix):
                main_func = func
                break
        trigger_url = None
        if main_func:
            trigger_url = release_info["releaseOutputs"]["deploy"][main_func]["triggers"][0]["httpTrigger"][
                "urlInternet"]
        # Currently, the template config is not totally consistent between entry and exit.
        template_config_snapshot = release_info.get("templateConfigSnapshot", {})
        template_name = template_config_snapshot.pop("templateName", None)
        template_config_snapshot["template_name"] = template_name

        return {
            "config": template_config_snapshot,
            "url": trigger_url
        }

    def get_release_info(self, name):
        """
        Get the functions information of the project.
        :param name: Name of the project to be created, which must be unique within the Alibaba Cloud account.
        :returns: A response dictionary with the status code and body of the created project or an error message.
        :raises Exception: If any error occurs during the API call or within the method execution.
        """
        resp = self._client.get_project(name=name).to_map()
        if resp["statusCode"] == 200:
            return resp["body"]["status"]["latestReleaseDetail"]
        return None
