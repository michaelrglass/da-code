## TODO
* create controller.py, separating out stuff from da_agent.py
* make everything run in the docker container


```bash
python evaluate.py \
    --output_dir output/gpt4turbo \
    --gold_dir da_code/gold \
    --eval_json da_code/configs/eval/all.jsonl \
    --result_file results/gpt4.json \
    --timeout_seconds 300
```