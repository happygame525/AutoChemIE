export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
# VLLM_USE_V1=1 VLLM_WORKER_MULTIPROC_METHOD=spawn vllm serve models/deepseek-ai/DeepSeek-R1-Distill-Qwen/ --trust-remote-code --served-model-name deepseek --gpu-memory-utilization 0.95 --tensor-parallel-size 8 --port 8000 --max_num_seqs 50

VLLM_USE_MODELSCOPE=true vllm serve models/deepseek-ai/DeepSeek-R1-Distill-Qwen --tensor-parallel-size 8 --max-model-len 50000 --enforce-eager --gpu-memory-utilization 0.95 --served-model-name deepseek
