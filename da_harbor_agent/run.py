import argparse
import datetime
import json
import logging
import os
import sys

from da_harbor_agent.envs.da_agent import DA_Agent_Env


#  Logger Configs {{{ #
logger = logging.getLogger("da_agent")
logger.setLevel(logging.DEBUG)

datetime_str: str = datetime.datetime.now().strftime("%Y%m%d@%H%M%S")

file_handler = logging.FileHandler(os.path.join("logs", "normal-{:}.log".format(datetime_str)), encoding="utf-8")
debug_handler = logging.FileHandler(os.path.join("logs", "debug-{:}.log".format(datetime_str)), encoding="utf-8")
stdout_handler = logging.StreamHandler(sys.stdout)
sdebug_handler = logging.FileHandler(os.path.join("logs", "sdebug-{:}.log".format(datetime_str)), encoding="utf-8")

file_handler.setLevel(logging.INFO)
debug_handler.setLevel(logging.DEBUG)
stdout_handler.setLevel(logging.INFO)
sdebug_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="\x1b[1;33m[%(asctime)s \x1b[31m%(levelname)s \x1b[32m%(module)s/%(lineno)d-%(processName)s\x1b[1;33m] \x1b[0m%(message)s")
file_handler.setFormatter(formatter)
debug_handler.setFormatter(formatter)
stdout_handler.setFormatter(formatter)
sdebug_handler.setFormatter(formatter)

stdout_handler.addFilter(logging.Filter("da_agent"))
sdebug_handler.addFilter(logging.Filter("da_agent"))

logger.addHandler(file_handler)
logger.addHandler(debug_handler)
logger.addHandler(stdout_handler)
logger.addHandler(sdebug_handler)
#  }}} Logger Configs # 



def config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run end-to-end evaluation on the benchmark"
    )
    
    parser.add_argument("--max_steps", type=int, default=20)
    
    parser.add_argument("--max_memory_length", type=int, default=15)
    
    parser.add_argument("--model",'-m',type=str, default="Azure/gpt-4o")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--max_tokens", type=int, default=1500)
    parser.add_argument("--stop_token", type=str, default=None)
    
    # example config
    parser.add_argument("--task_config","-t", type=str, default="da_code/configs/task/all.jsonl")
    parser.add_argument("--source_dir", type=str, default="da_code/source")
    parser.add_argument("--example_index", "-i", type=str, default="all", help="index range of the examples to run, e.g., '0-10', '2,3', 'all'")
    parser.add_argument("--example_name", "-n", type=str, default="", help="name of the example to run")
    parser.add_argument("--overwriting", action="store_true", default=False)
    parser.add_argument("--retry_failed", action="store_true", default=False)

    # output related
    parser.add_argument("--output_dir", type=str, default="output_hb")
    args = parser.parse_args()

    return args



def test(
    args: argparse.Namespace
) -> None:
    # log args
    logger.info("Args: %s", args)

    import uuid
    
    experiment_id = args.model.split("/")[-1] + "-" + uuid.uuid4().hex[:8]

    env_config = \
    {
        "image_name": "da_harbor_agent-image",
        "init_args": {
            "name": experiment_id,
            "work_dir": "/workspace",
        }
    }
    
    ## load task configs
    assert os.path.exists(args.task_config) and args.task_config.endswith(".jsonl"), f"Invalid task_config, must be a valid jsonl file: {args.task_config}"
    with open(args.task_config, "r", encoding="utf-8") as f:
        task_configs = [json.loads(line) for line in f]
    if args.example_name != "":
        task_configs = [task for task in task_configs if args.example_name in task["id"]]
    else:
        if args.example_index != "all":
            if "-" in args.example_index:
                start, end = map(int, args.example_index.split("-"))
                task_configs = task_configs[start:end]
            else:
                indices = list(map(int, args.example_index.split(",")))
                task_configs = [task_configs[i] for i in indices]
    
    for task_config in task_configs:
        instance_id = experiment_id +"/"+ task_config["id"]
        output_dir = os.path.join(args.output_dir, instance_id)
        result_json_path =os.path.join(output_dir, "dabench/result.json")
             
        if os.path.exists(result_json_path):
            logger.info("Overwriting %s", instance_id)
        else:
            logger.info("Running %s", instance_id)
            
        if os.path.exists(output_dir):
            os.system(f"rm -rf {output_dir}")
            logger.info("Removed existing %s", output_dir)

        os.makedirs(output_dir, exist_ok=True)

        env_config["init_args"]["name"] = experiment_id +"-"+ task_config["id"]
        env = DA_Agent_Env(
            env_config=env_config,
            task_config=task_config,
            source_dir=args.source_dir,
            mnt_dir=output_dir
        )
        post_process = task_config["post_process"] if "post_process" in task_config else []
        task = env.task_config['instruction']
        if post_process:
            assert len(post_process) == 1 and post_process[0] == "plot_process"
            # this is how we indicate to the DA-Harbor-Agent that we need to use plot post process
            task = task + "\nSave the code to produce the plot in `/app/output/plot.py`."

        # Run agent inside container
        cmd = [
            "python", "/da_harbor_agent/run_agent.py",
            "-t", task,
            "-m", args.model,
            "--max_steps", str(args.max_steps),
            "--max_memory_length", str(args.max_memory_length),
            "--max_tokens", str(args.max_tokens),
            "--temperature", str(args.temperature),
            "--top_p", str(args.top_p),
            "--logs_dir", "/workspace/logs",
        ]
        logger.info('Task input: %s', task)
        exit_code, output = env.container.exec_run(
            cmd, workdir="/workspace",
            environment={"PYTHONPATH": "/"}
        )
        logger.info("Agent output:\n%s", output.decode("utf-8"))

        # Results are written to dabench/result.json by run_agent.py
        # (already in mounted directory at output_dir)

        logger.info("Finished %s", instance_id)
        env.close()




if __name__ == '__main__':
    args = config()
    
    test(args)