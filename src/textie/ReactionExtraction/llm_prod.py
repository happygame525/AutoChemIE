r'''
使用大模型抽取product实体
'''

from retrieval import *
from prompt_construct import *
from chat_llm import *
import ast
import re

r'''
product提取 
input:  train_data
        test_data 测试数据集
        k 选取的demonstration的数量

'''
def chem_prod(train_data,test_data,k=10):
    prev_set=[]
    for i,test_item in enumerate(test_data):
        #print("第{}条数据".format(i))
        sentence=test_item['text']
        #reactions=test_item['reactions']
        prev_dict={}
        prev_dict['text']=sentence
        prev_dict['products']=[]
        #生成demonstrations
        max_indices=prod_retrieval(sentence,k)
        demo_list=[train_data[idx] for idx in max_indices]
        demos=gen_product_demonstration(demo_list)
        prompt=gen_product_prompt(sentence,demos)
        answer=qwen_chat_vllm(prompt)[0]

        #加入一个正则表达式，提取出json部分
        pattern = r'\[[^\[\]]*\]'
        answer=re.findall(pattern,answer)[0]
        #print(answer)
        try:
            answer=ast.literal_eval(answer)
        except Exception as e:
            prev_set.append(prev_dict)
            continue
#             prompt='''
# The answer you generated is:{}
# The answer does not conform to the json format.Please change the format to json and return the revised answer
# '''.format(answer)
#             answer=qwen_chat_vllm(prompt)[0]   
#             #加入一个正则表达式，提取出json部分
#             pattern = r'\[[^\[\]]*\]'
#             answer=re.findall(pattern,answer)[0] 
#             answer=ast.literal_eval(answer)
        prev_dict['products']=answer

        prev_set.append(prev_dict)


    return prev_set
            
