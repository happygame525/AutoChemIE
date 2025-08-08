from datasets import Dataset

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1,3,2,0'
from transformers import AutoTokenizer,AutoModelForCausalLM
from vllm import LLM, SamplingParams
from tqdm import trange
import torch
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def prompt_construct(prompt):
    messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.Make sure to generate your answers exactly according to the given format and not have any other redundant information.And  generate the answer only once, stop repeating it"},
    {"role": "user", "content": prompt}
    ]
    return messages

        





#model_id ="/data/models/Qwen2-72B-Instruct"
#model_id ="/data/models/qwen2.5/qwen2.5-14B-Instruct"
#model_id='/data/models/llama3/Meta-Llama-3-8B-Instruct'
#model_id='/data/models/llama3/Meta-Llama-3-70B-Instruct'
#model_id='/data/lizh/LLaMA-Factory-main/models/qwen2.5_14b_sft_only'
#model_id='/data/lizh/LLaMA-Factory-main/models/qwen2.5_14b_ptsft'
#model_id='/data/lizh/LLaMA-Factory-main/models/qwen2.5_14b_product_sft'
#model_id='/data/models/qwen2.5/Qwen2.5-72B-Instruct'
#model_id='/data/lizh/LLaMA-Factory-main/models/qwen2.5_72b_reaction_sft'
model_id='/data/lizh/LLaMA-Factory-main/models/llama3_70b_reaction_sft'


# 初始化分词器
tokenizer = AutoTokenizer.from_pretrained(model_id)
# 设置采样参数 温度系数 top_p max_tokens
sampling_params = SamplingParams(temperature=0.1, top_p=0.7,max_tokens=512)
# 初始化语言模型
llm = LLM(model=model_id,tensor_parallel_size = 4,gpu_memory_utilization=0.6)
#设置分词器的填充方向
tokenizer.padding_side = "left"
batch_size = 1

def qwen_chat_vllm(messages):
    
    mess_list=[]
    mess_list.append(messages)
    mess_dict = {"messages":mess_list}
    dataset = Dataset.from_dict(mess_dict)

    res_list=[]
    for i in trange(0,len(dataset),batch_size):

        tail = i+batch_size
        if i+batch_size > len(dataset):
            tail = len(dataset)

        messages = dataset.select(range(i,tail))['messages']
        #print(messages)
        #应用聊天模板
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            padding = True,
        )
        outputs = llm.generate(text, sampling_params)

        for output in outputs:
            ans = output.outputs[0].text
            res_list.append(ans)
    #print(res_list)
    return res_list

# tokenizer = AutoTokenizer.from_pretrained(model_id)
# model = AutoModelForCausalLM.from_pretrained(
#     model_id,
#     torch_dtype=torch.bfloat16,
#     max_new_tokens=2560,
#     device_map="auto",
# )
# def chat_llm(messages):
    
#     input_ids = tokenizer.apply_chat_template(
#         messages,
#         add_generation_prompt=True,
#         return_tensors="pt"
#     ).to(model.device)

#     terminators = [
#         tokenizer.eos_token_id,
#         tokenizer.convert_tokens_to_ids("<|eot_id|>")
#     ]

#     outputs = model.generate(
#         input_ids,
#         max_new_tokens=2560,
#         eos_token_id=terminators,
#         do_sample=True,
#         temperature=0.3,
#         top_p=0.7,
#     )
#     response = outputs[0][input_ids.shape[-1]:]
#     res=tokenizer.decode(response, skip_special_tokens=True)
#     return res


# message=prompt_construct("introduce the Tranformer for me")
# qwen_chat_vllm(message)