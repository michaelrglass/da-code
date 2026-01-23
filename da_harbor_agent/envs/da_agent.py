import logging
import os
import time
from typing import Any, Dict

from docker.models.containers import Container
from docker.client import DockerClient
from docker.errors import ImageNotFound
import shutil, pathlib, docker
from da_harbor_agent.envs.utils import create_folder_if_not_exists, delete_files_in_folder
from da_harbor_agent.agent.action import Action

logger = logging.getLogger("da_agent.env")

# constants
START_UP_DELAY = 2
DEFAULT_IMAGE_DIR = 'da_harbor_agent/images'
DEFAULT_WORK_DIR = '/workspace'


class DA_Agent_Env:
    """
    Fixme: refactor the logic when implementing the multi-process version
    """
    def __init__(self, env_config, task_config, source_dir, mnt_dir):
        """
        Args:
            path_to_vm (str): path to .vmx file
            action_space (str): "computer_13" | "pyautogui"

            task_config (Dict[str, Any]): manages task configs integratedly,
              including
              * base snapshot
              * task id (uuid)
              * instruction

            tmp_dir (str): temporary directory to store trajectory stuffs like
              the extracted screenshots
            cache_dir (str): cache directory to cache task-related stuffs like
              reference file for evaluation
        """
        super().__init__()
        self.task_config = task_config
        self.container_name = env_config['init_args']['name']
        self.image_name = env_config['image_name']
        self.source_dir = source_dir
        self.mnt_dir = mnt_dir
        self.work_dir = DEFAULT_WORK_DIR
        self.kwargs = env_config['init_args']

        self._set_task_info(task_config)
        logger.info("Initializing...")
        self._construct_container()
        
        logger.info("Setting up environment...")
        
        dir = os.path.join(self.source_dir, self.task_id)
        assert os.path.isdir(dir), f"Task directory {dir} does not exist."
        
        self._setup_cp_dir(dir)  # TODO: how do the files look after this?
        time.sleep(2)
        logger.info("Environment setup complete.")

    def _setup_cp_dir(self, dir: str):
        """
        Args:
            dir (str): the directory to copy to the workspace
        """
        mnt_dir = [mount['Source'] for mount in self.container.attrs['Mounts']][0]
        if os.path.isfile(dir):
            print(f"Warning: {dir} is a file, not a directory. Copying the file to {mnt_dir}.")
            shutil.copy2(dir, mnt_dir)
        elif os.path.isdir(dir):
            print(f"Copying all files in {dir} to {mnt_dir}.")
            shutil.copytree(dir, mnt_dir, dirs_exist_ok=True)
        else:
            print(f"Warning: {dir} is neither a file nor a directory.")
        return

    def _set_task_info(self, task_config: Dict[str, Any]):
        self.task_id: str = task_config['id']
        self.instruction = task_config["instruction"]
        self.post_process_func = task_config["post_process"] if "post_process" in task_config else []
        
    def close(self):
        self.container.stop()
        self.container.remove()
        logger.info(f"Container {self.container_name} stopped and removed.")
        
    def _construct_container(self):
        client = docker.from_env()
        container_name = self.container_name
        #### delete existing container
        try:
            container = client.containers.get(container_name)
            container.stop()
            container.remove()
            print(f"Container {container_name} stopped and removed.")
        except docker.errors.NotFound:
            pass
        except docker.errors.APIError as e:
            pass
        
        create_folder_if_not_exists(self.mnt_dir)
        src_dir = pathlib.Path(self.mnt_dir).absolute().__str__()
        delete_files_in_folder(self.mnt_dir)
        
        volumes = {src_dir: {'bind': self.work_dir, 'mode': 'rw'}}
        allowed_params = ['command', 'ports', 'restart_policy', 'entrypoint', 'hostname', 'domainname', 'name', 'user', 
                          'mac_address', 'platform', 'network_mode', 'network_disabled', 'healthcheck', "environment"]
        kwargs = {k: self.kwargs[k] for k in self.kwargs if k in allowed_params}
        environment = {# "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
                       "IBM_LITELLM_API_KEY": os.environ.get("IBM_LITELLM_API_KEY"),}
        extra_params = {'detach': True, 'tty': True, 'stdout': True, 'stderr': True, 
                        'stdin_open': True, 'environment': environment, **kwargs}
        
        try:
            client: DockerClient = docker.from_env()
            image = client.images.get(self.image_name)
            self.container: Container = client.containers.run(image=image, volumes=volumes, **extra_params)
        except ImageNotFound as e:
            dockerfile_path = os.path.join(DEFAULT_IMAGE_DIR, self.image_name)
            logger.info(f"Image {self.image_name} not found, try to build from dockerfile {dockerfile_path} ...")
            image = client.images.build(path=os.getcwd(), 
                                        dockerfile=os.path.join(dockerfile_path, 'Dockerfile'),
                                        tag=self.image_name, rm=True)[0]
            self.container: Container = client.containers.run(image=image, volumes=volumes, **extra_params)
        except Exception as e:
            logger.info(f"Failed to construct container from image {self.image_name} with error: {e}")
            raise e

        time.sleep(START_UP_DELAY)
        logger.info(f"Connected to container[name={self.container.name}, id={self.container.id}] from image {self.image_name} ...")    
        
        return self.container
