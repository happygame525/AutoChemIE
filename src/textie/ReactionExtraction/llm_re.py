r'''
使用大模型进行化学反应抽取
'''
from retrieval import *
from prompt_construct import *
from chat_llm import *

import ast
import re
r'''
化学反应式提取 
input:  train_data
        test_data 测试数据集
        k 选取的demonstration的数量

'''
def chem_re(train_data,test_data,k=3):
    prev_set=[]
    for i,test_item in enumerate(test_data):
        print("第{}条数据".format(i))
        sentence=test_item['text']
        reactions=test_item['reactions']
        prev_dict={}
        prev_dict['text']=sentence
        prev_dict['reactions']=[]

        for reaction_item in reactions:
            if 'Product' not in reaction_item: continue
            product=reaction_item['Product']

            #生成demonstrations
            max_indices=bge_retrieval(sentence)
            demo_list=[train_data[idx] for idx in max_indices]
            demos=gen_reaction_demonstration(demo_list)
            prompt=gen_reaction_prompt(sentence,product,demos)

            #answer=chat_llm(prompt)
            answer=qwen_chat_vllm(prompt)[0]
            #print(answer)

            #加入一个正则表达式，提取出json部分
            pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
            match = re.search(pattern, answer)
            if match:
                answer=match.group(0)
                try:
                    answer=ast.literal_eval(answer)
                except Exception as e:
                    # information='The json parsing format is wrong! Please regenerate the answer to ensure that the result meets the json parsing format\n'
                    # prompt=information+prompt
                    # answer=qwen_chat_vllm(prompt)[0]
                    # match = re.search(pattern, answer)
                    # if match:
                    #     answer=match.group(0)
                    
                    continue
                print(answer)
                prev_dict['reactions'].append(answer)
        
        prev_set.append(prev_dict)

    return prev_set
            

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
            
def chem_re_new(train_data,test_data,k=3):
    prev_set=[]
    for i,test_item in enumerate(test_data):
        print("第{}条数据".format(i))
        sentence=test_item['text']
        reactions=test_item['reactions']
        prev_dict={}
        prev_dict['text']=sentence
        prev_dict['reactions']=[]

        if reactions==[]:
            answers=increment_re(sentence)
            prev_dict['reactions']=answers
        else:
            for reaction_item in reactions:
                if 'Product' not in reaction_item: 
                    continue
                else:
                    product=reaction_item['Product']

                    #生成demonstrations
                    max_indices=bge_retrieval(sentence)
                    demo_list=[train_data[idx] for idx in max_indices]
                    demos=gen_reaction_demonstration(demo_list)
                    prompt=gen_reaction_prompt(sentence,product,demos)

                    #answer=chat_llm(prompt)
                    answer=qwen_chat_vllm(prompt)[0]
                    #print(answer)

                    #加入一个正则表达式，提取出json部分
                    pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
                    match = re.search(pattern, answer)
                    if match:
                        answer=match.group(0)
                        try:
                            answer=ast.literal_eval(answer)
                        except Exception as e:
                            # information='The json parsing format is wrong! Please regenerate the answer to ensure that the result meets the json parsing format\n'
                            # prompt=information+prompt
                            # answer=qwen_chat_vllm(prompt)[0]
                            # match = re.search(pattern, answer)
                            # if match:
                            #     answer=match.group(0)
                            
                            continue
                        print(answer)
                        prev_dict['reactions'].append(answer)
        
        prev_set.append(prev_dict)

    return prev_set
            