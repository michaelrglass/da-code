import logging
import os
import subprocess
import tempfile
import time
from typing import Callable, Any, Optional, Tuple

from typing import List, Dict, Union
from docker.models.containers import Container
from docker.client import DockerClient
from docker.errors import ImageNotFound
import shutil, pathlib, docker, time, copy
from da_harbor_agent.controllers.python import PythonController
from da_harbor_agent.envs.utils import *
from da_harbor_agent import configs
from da_harbor_agent.agent.action import Bash, Action, Terminate, Python, SQL
import signal

logger = logging.getLogger("da_agent.env")

# constants
START_UP_DELAY = 2 # start up delay for docker container
DEFAULT_TIME_OUT = 60 # default waiting time for each action
MAX_OBS_LENGTH = 3000
EMPTY_DATA_PATH = 'da_agent/data/empty' # an empty data directory
DEFAULT_IMAGE_DIR = 'da_agent/images' # default directory to store docker images
DEFAULT_WORK_DIR = '/workspace' # default working directory in the container
DEFAULT_MNT_DIR = 'da_agent/mnt' # default directory to copy and mount data path, also the output directory
TASK_FINISHED = "task_finished" # infos key
ACTION_EXEC = "action_executed" # infos key


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
        
        self.controller = PythonController(container=self.container, work_dir=self.work_dir)

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
        extra_params = {'detach': True, 'tty': True, 'stdout': True, 'stderr': True, 'stdin_open': True, **kwargs}

        try:
            client: DockerClient = docker.from_env()
            image = client.images.get(self.image_name)
            self.container: Container = client.containers.run(image=image, volumes=volumes, **extra_params)
        except ImageNotFound as e:
            dockerfile_path = os.path.join(DEFAULT_IMAGE_DIR, self.image_name)
            if os.path.exists(dockerfile_path):
                logger.info(f"Image {self.image_name} not found, try to build from dockerfile {dockerfile_path} ...")
                image = client.images.build(path=dockerfile_path, tag=self.image_name, rm=True)[0]
            else:
                logger.info(f"Image {self.image_name} not found, try to pull from Dockerhub ...")
                image = client.images.pull(self.image_name)[0]
            self.container: Container = client.containers.run(image=image, volumes=volumes, **extra_params)
        except Exception as e:
            logger.info(f"Failed to construct container from image {self.image_name} with error: {e}")
            raise e

        time.sleep(START_UP_DELAY)
        logger.info(f"Connected to container[name={self.container.name}, id={self.container.id}] from image {self.image_name} ...")    
        
        return self.container
    
    def step(self, action: Action):
        try:
            with timeout(DEFAULT_TIME_OUT,"Action execution time exceeded!"):
                done = False
                if isinstance(action, Bash):
                    observation = self.execute_code_action(action)
                elif isinstance(action, SQL):
                    observation = self.execute_sql_action(action)
                # elif isinstance(action, CreateFile):
                #     observation = self.create_file_action(action)
                # elif isinstance(action, EditFile):
                #     observation = self.edit_file_action(action)
                elif isinstance(action, Python):
                    observation = self.execute_python_action(action)
                elif isinstance(action, Terminate):
                    observation = "Terminate"
                    done = True
                else:
                    raise ValueError(f"Unrecognized action type {action.action_type} !")
        except TimeoutError as e:
            observation = str(e)
        
        observation = self._handle_observation(observation)
        # logger.info("Observation: %s", observation)
        return observation, done
    
    def _handle_observation(self, observation):
        max_length = MAX_OBS_LENGTH  
        if len(observation) > max_length:
            truncated_observation = observation[:max_length] + "\n[Observation too long, truncated; Try other commands to get the left part.]"
            return truncated_observation
        return observation


    def execute_code_action(self, action: Bash):
        """ Execute action in bash shell """
        
        obs = self.controller.execute_command(action.code)
        if obs is None or obs == '':
            obs = "Command executed successfully. No output."
        
        return obs

    def execute_python_action(self, action: Python):
        """ Execute action in python """
        obs = self.controller.execute_python_file(action.filepath, action.code)
        if obs is None or obs == '':
            obs = f"{action.filepath} executed successfully. No output."
        
        return obs
    
    def execute_sql_action(self, action: Python):
        """ Execute action in sql"""
        obs = self.controller.execute_sql_code(action.file_path, action.code, action.output)
        if obs is None or obs == '':
            obs = f"SQL command executed successfully. No output."
        
        return obs
