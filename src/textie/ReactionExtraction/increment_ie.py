r'''
    针对第一阶段没抽出来prod的情况，尝试直接一步抽取
'''

from prompt_construct import *
from chat_llm import *
import ast
import re

def increment_re(sentence):

    prompt=gen_zeroshot_prompt(sentence=sentence)
    answer=qwen_chat_vllm(prompt)[0]

    #加入一个正则表达式，提取出json部分
    pattern = r'\{[^{}]*\}'
    matches = re.findall(pattern, answer)
    answers=[]
    for match in matches:
        
        try:
            dict_obj = ast.literal_eval(match)
            answers.append(dict_obj)
        except ValueError as e:
            print(f"Error parsing string: {match}")
            
            continue
    print("answers:{}".format(answers))
    return answers