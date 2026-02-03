## TODO
* In Dockerfile: copy da_harbor_agent to /agent
* command to build docker image
* PythonController should not use container
* run.py should call run_agent.py inside the docker container

## DA-Harbor-Agent plot
```bash
python da_harbor_agent/run.py --task_config da_code/configs/task/visual.jsonl

python evaluate.py \
    --output_dir output_hb/??? \
    --eval_json da_code/configs/eval/eval_visual.jsonl \
    --timeout_seconds 300
```

## With fix for saving input files too

```bash
python run.py

python evaluate.py \
    --output_dir output/run1_inf \
    --eval_json da_code/configs/eval/eval_all.jsonl \
    --timeout_seconds 300

Number of results: 500
Average score: 0.3726867557666788
Average finished: 0.986
====================================
                         score  finished
type
data insight          0.366034  0.987342
data manipulation     0.345205  0.986301
data visualization    0.320513  0.987179
data wrangling        0.318760  0.970000
machine learning      0.457007  0.990000
statistical analysis  0.423571  1.000000
-------------------------------
             score  finished
hardness
Easy      0.493346  1.000000
Hard      0.318199  0.971154
Medium    0.349119  0.986301
-------------------------------
                     score  finished
big_type
EDA               0.362556      0.99
data wrangling    0.318760      0.97
machine learning  0.457007      0.99
-------------------------------
                          score  finished
result_type
binary classification  0.508875  1.000000
cluster                0.599188  1.000000
csv                    0.349448  0.993377
multi classification   0.469469  1.000000
plot                   0.320513  0.987179
regression             0.308455  0.968750
text                   0.436620  0.985915

python scripts/convert_results.py results/run1_inf.json -o results/run1_inf_results.json

  Trials: 500
  Errors: 0
  Mean score: 0.3727

harbor stats breakdown adapters/dacode/parity/parity-experiments/run1_inf_results.json
Found 1 result.json files
Loaded 500 trials across 500 tasks
Using datasets directory: /home/mrglass/tbench/harbor/datasets/dacode
    Overall Results
┏━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric      ┃ Value  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━┩
│ Mean Reward │ 0.3727 │
│ Std Dev     │ 0.4515 │
│ Tasks       │ 500    │
│ Trials      │ 500    │
└─────────────┴────────┘

             By Difficulty
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Difficulty ┃   Mean ┃    Std ┃ Count ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ easy       │ 0.4933 │ 0.4702 │   104 │
│ hard       │ 0.3182 │ 0.4225 │   104 │
│ medium     │ 0.3491 │ 0.4487 │   292 │
└────────────┴────────┴────────┴───────┘

               By Category
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Category     ┃   Mean ┃    Std ┃ Count ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ data-science │ 0.3727 │ 0.4515 │   500 │
└──────────────┴────────┴────────┴───────┘

          By Tag (non-common only)
┏━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ Tag            ┃   Mean ┃    Std ┃ Count ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ data           │ 0.3619 │ 0.4512 │   170 │
│ data-sa        │ 0.4236 │ 0.4739 │    70 │
│ data-wrangling │ 0.3188 │ 0.4317 │   100 │
│ di             │ 0.3660 │ 0.4652 │    79 │
│ di-csv         │ 0.3221 │ 0.4291 │    37 │
│ di-text        │ 0.4048 │ 0.4968 │    42 │
│ dm             │ 0.3452 │ 0.4452 │    73 │
│ dm-csv         │ 0.3452 │ 0.4452 │    73 │
│ ml             │ 0.4570 │ 0.4286 │   100 │
│ ml-binary      │ 0.6361 │ 0.4175 │    24 │
│ ml-cluster     │ 0.5992 │ 0.3460 │    21 │
│ ml-competition │ 0.0000 │ 0.0000 │    20 │
│ ml-multi       │ 0.6651 │ 0.3579 │    12 │
│ ml-regression  │ 0.4292 │ 0.4504 │    23 │
│ plot           │ 0.3205 │ 0.4697 │    78 │
│ plot-bar       │ 0.2174 │ 0.4217 │    23 │
│ plot-line      │ 0.4286 │ 0.5071 │    21 │
│ plot-pie       │ 0.4211 │ 0.5073 │    19 │
│ plot-scatter   │ 0.2000 │ 0.4140 │    15 │
└────────────────┴────────┴────────┴───────┘
```

```bash
python evaluate.py \
    --output_dir output/gpt-4o-42973f07 \
    --eval_json da_code/configs/eval/eval_all.jsonl \
    --timeout_seconds 300

Number of results: 500
Average score: 0.26915559849021103
Average finished: 0.974
====================================
                         score  finished
type
data insight          0.215190  0.974684
data manipulation     0.211187  0.972603
data visualization    0.371795  0.987179
data wrangling        0.122997  0.950000
machine learning      0.408614  0.980000
statistical analysis  0.285714  0.985714
-------------------------------
             score  finished
hardness
Easy      0.378785  0.990385
Hard      0.194081  0.942308
Medium    0.256848  0.979452
-------------------------------
                     score  finished
big_type
EDA               0.271389      0.98
data wrangling    0.122997      0.95
machine learning  0.408614      0.98
-------------------------------
                          score  finished
result_type
binary classification  0.456607  1.000000
cluster                0.629199  1.000000
csv                    0.135210  0.980132
multi classification   0.375221  0.882353
plot                   0.371795  0.987179
regression             0.236603  1.000000
text                   0.450704  0.971831
```

```bash
python scripts/convert_results.py results/gpt-4o-42973f07.json -o results/run2_results.json
  Trials: 500
  Errors: 0
  Mean score: 0.2692
```

```bash
python evaluate.py \
    --output_dir output/run1 \
    --eval_json da_code/configs/eval/eval_all.jsonl \
    --timeout_seconds 300

Number of results: 500
Average score: 0.2652818864446749
Average finished: 0.98
====================================
                         score  finished
type
data insight          0.202532  0.974684
data manipulation     0.180365  1.000000
data visualization    0.282051  0.974359
data wrangling        0.146221  0.970000
machine learning      0.428521  0.980000
statistical analysis  0.342857  0.985714
-------------------------------
             score  finished
hardness
Easy      0.328271  1.000000
Hard      0.226685  0.971154
Medium    0.256594  0.976027
-------------------------------
                     score  finished
big_type
EDA               0.250556  0.983333
data wrangling    0.146221  0.970000
machine learning  0.428521  0.980000
-------------------------------
                          score  finished
result_type
binary classification  0.493457  0.966667
cluster                0.537556  1.000000
csv                    0.133554  0.986755
multi classification   0.415716  0.941176
plot                   0.282051  0.974359
regression             0.302893  1.000000
text                   0.464789  0.985915

python scripts/convert_results.py results/run1.json -o results/run1_results.json
  Trials: 500
  Errors: 0
  Mean score: 0.2653
```
```
Let's redesign run.py and PythonController.  I want the PromptAgent (in agents.py) to run inside the docker container. So PythonController should not have a container object anymore, it will instead directly execute commands since it will be running inside the container. When run.py spins up a docker container it can call run_agent.py -t "task instructions" to run the agent inside the container. 
Try to keep the changes limited so it is clear that the effect is equivalent.
Start by making a plan.  
```

```
Look under harbor/agents/installed to see how Harbor allows agents to interface with its evaluation harness.
In particular, check out opencode since it is relatively simple.
I want da_harbor_agent to work as a Harbor installed agent. So create:
* install-da-agent.sh.j2: Base it on the images/da_agent-image/Dockerfile and the content of run.py
* da_agent.py: Base on the code that calls run_agent.py in run.py
The parts of run.py that use envs/da_agent.py will not be needed, since Harbor will take care of creating
the container that the agent runs in.
Avoid modifying the files under da_harbor_agent if possible.
```

```bash
python da_harbor_agent/run.py

python evaluate.py \
    --output_dir output_hb/gpt-4o-a59b4bd7 \
    --eval_json da_code/configs/eval/eval_sa.jsonl \
    --timeout_seconds 300

Number of results: 70
Average score: 0.3819047619047619
Average finished: 0.9857142857142858
====================================
                         score  finished
type
statistical analysis  0.381905  0.985714
-------------------------------
             score  finished
hardness
Easy      0.318182  1.000000
Hard      0.312500  1.000000
Medium    0.406536  0.980392
-------------------------------
             score  finished
big_type
EDA       0.381905  0.985714
-------------------------------
                score  finished
result_type
csv          0.319380  0.976744
text         0.481481  1.000000
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

### Run temp 0.0 all

python run.py -t da_code/configs/task/visual.jsonl

### Run temp 0.0
```bash
python run.py

python evaluate.py \
    --output_dir output/gpt-4o-f7c203d4 \
    --eval_json da_code/configs/eval/eval_sa.jsonl \
    --timeout_seconds 300

Processing Task id: data-sa-070: 100%|████████████████████████████████████████████████████████████| 70/70 [00:00<00:00, 727.18it/s]
Number of results: 70
Average score: 0.20714285714285716
Average finished: 1.0
====================================
                         score  finished
type
statistical analysis  0.207143       1.0
-------------------------------
             score  finished
hardness
Easy      0.090909       1.0
Hard      0.062500       1.0
Medium    0.254902       1.0
-------------------------------
             score  finished
big_type
EDA       0.207143       1.0
-------------------------------
                score  finished
result_type
csv          0.104651       1.0
text         0.370370       1.0

python scripts/convert_results.py results/gpt-4o-t0.json -o results/results_dacode_t0.json
```

### Run 1
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

### Run 2
```
python run.py

python evaluate.py \
    --output_dir output/gpt-4o-efd58557 \
    --eval_json da_code/configs/eval/eval_sa.jsonl \
    --timeout_seconds 300

Number of results: 70
Average score: 0.2714285714285714
Average finished: 0.9857142857142858
====================================
                         score  finished
type
statistical analysis  0.271429  0.985714
-------------------------------
             score  finished
hardness
Easy      0.181818     1.000
Hard      0.062500     0.875
Medium    0.323529     1.000
-------------------------------
             score  finished
big_type
EDA       0.271429  0.985714
-------------------------------
                score  finished
result_type
csv          0.162791  1.000000
text         0.444444  0.962963
```