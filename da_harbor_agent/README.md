## TODO
* In Dockerfile: copy da_harbor_agent to /agent
* command to build docker image
* PythonController should not use container
* run.py should call run_agent.py inside the docker container

```
Let's redesign run.py and PythonController.  I want the PromptAgent to run inside the docker container. So PythonController should not have a container object anymore, it will instead directly execute commands since it will be running inside the container. The Dockerfile should also copy the da_harbor_agent source directory inside the Docker environment, so when run.py spins up a docker container it can call run_agent.py -t "task instructions" to run the agent inside the container. 
Try to keep the changes limited so it is clear that the effect is equivalent.  
```

```bash
python da_harbor_agent/run.py

python evaluate.py \
    --output_dir output_hb/gpt-4o-8123ac9f \
    --eval_json da_code/configs/eval/eval_sa.jsonl \
    --timeout_seconds 300

Number of results: 70
Average score: 0.33476190476190476
Average finished: 1.0
====================================
                         score  finished
type
statistical analysis  0.334762       1.0
-------------------------------
             score  finished
hardness
Easy      0.363636       1.0
Hard      0.250000       1.0
Medium    0.341830       1.0
-------------------------------
             score  finished
big_type
EDA       0.334762       1.0
-------------------------------
                score  finished
result_type
csv          0.312403       1.0
text         0.370370       1.0
```

```bash
python run.py

python evaluate.py \
    --output_dir output/gpt-4o-787dbe9b \
    --eval_json da_code/configs/eval/eval_sa.jsonl \
    --timeout_seconds 300

Number of results: 70
Average score: 0.20714285714285716
Average finished: 0.9857142857142858
====================================
                         score  finished
type
statistical analysis  0.207143  0.985714
-------------------------------
             score  finished
hardness
Easy      0.090909  0.909091
Hard      0.062500  1.000000
Medium    0.254902  1.000000
-------------------------------
             score  finished
big_type
EDA       0.207143  0.985714
-------------------------------
                score  finished
result_type
csv          0.104651  0.976744
text         0.370370  1.000000
```