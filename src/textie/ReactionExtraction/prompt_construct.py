r'''
设计反应提取的prompt
input:sentence、抽取出的product实体(单个)
output:与反应相关的其他实体 包括:   如果不存在则返回None
函数的output:封装好的messages
'''
r'''
You are a chemical information extraction model
# CONTEXT #
I'm in the planning to build a knowledge graph about chemical organic reactions. I hope to construct this Knowledge Graph by extracting organic reactions from the chemical literature.
# AUDIENCE #
This Chemical Knowledge Graph is for Chemical Experts.I hope that the knowledge graph I build can provide chemistry experts with meaningful knowledge about organic reactions.
# LANGUAGE #
English

'''

r'''
# OBJECTIVE #
From the given <<<CHEMICAL LITERATURE>>> and the Identified <<<Product Entity>>>, Please identify other reaction role entities related to the reaction that produced this product,include: Reactants Catalyst_Reagents Workup_reagents Solvent Yield Temperature and Time
# ANALYSIS #
In the given sentence, we have identified the product entity of the chemical reaction. You need to reason with the context and focus on how to find the other participating role entities of the chemical reaction corresponding to the product entity.Please think step by step.
# Response Format #
You will respond with a JSON object in this format and will not respond to anything else:
<format>\n{
“entity_type”:[entity1,entity2,...],...
}
</format>
If there is no entity of the corresponding entity type, the value of the corresponding entity type is None
# DEMONSTRATION #
{DEMO}
# QUESTION #
<CHEMICAL LITERATURE>\n"{sentence}"\n</CHEMICAL LITERATURE>
<Product Entity>\n'{product}'\n</Product Entity>
Output:
'''

def gen_reaction_prompt(sentence,product,demos):
    system_prompt='''
You are a chemical information extraction model
# CONTEXT #
I'm in the planning to build a knowledge graph about chemical organic reactions. I hope to construct this Knowledge Graph by extracting organic reactions from the chemical literature.
# AUDIENCE #
This Chemical Knowledge Graph is for Chemical Experts.I hope that the knowledge graph I build can provide chemistry experts with meaningful knowledge about organic reactions.
# LANGUAGE #
English
'''
    user_prompt='''
# OBJECTIVE #
From the given <<<CHEMICAL LITERATURE>>> and the Identified <<<Product Entity>>>, Please identify other reaction role entities related to the reaction that produced this product,include: Reactants Catalyst_Reagents Workup_reagents Solvent Yield Temperature and Time
# ANALYSIS #
In the given sentence, we have identified the product entity of the chemical reaction. You need to reason with the context and focus on how to find the other participating role entities of the chemical reaction corresponding to the product entity.Please think step by step.
# Response Format #
You will respond with a JSON object in this format and will not respond to anything else:
<format>\n  {{"entity_type":[entity1,entity2,...],...}}
</format>
If there is no entity of the corresponding entity type, The answer does not need to include the entity type.Please ensure that the returned answer meets the JSON parsing format.
# DEMONSTRATION #
{demos}
# QUESTION #
<CHEMICAL LITERATURE>\n"{sentence}"\n</CHEMICAL LITERATURE>
<Product Entity>\n'{product}'\n</Product Entity>
Output:
'''.format(demos=demos,sentence=sentence,product=product)
    messages = [
        {"role": "system", "content": system_prompt},
        {'role': 'user', 'content': user_prompt}
        
    ]
    return messages

#print(gen_reaction_prompt("hello","111","fsdfsdfds"))
entity_types=['Reactants','Catalyst_Reagents','Workup_reagents', 'Solvent' ,'Yield' ,'Temperature' ,'Time']



r'''
生成demonstration部分的prompt
'''
def gen_reaction_demonstration(demo_list):
    res_demo=''
    template_str='''
Demonstration {}:
<CHEMICAL LITERATURE>\n"{}"\n</CHEMICAL LITERATURE>
<Product Entity>\n'{}'\n</Product Entity>
Output:
'''
    idx=1
    for demo in demo_list:
        sentence=demo['text']
        for reaction in demo['reactions']:
            product=reaction['Product']
            demo_str=template_str.format(idx,sentence,product)
            idx +=1
            output_dict={}
            for key,values in reaction.items():
                output_dict[key]=[]
                for value in values:
                    output_dict[key].append(value)
            demo_str+=str(output_dict)
            res_demo+=demo_str
            res_demo+='\n'

    return res_demo


r'''
抽取product 生成demonstration部分的prompt
'''
def gen_product_demonstration(demo_list):
    res_demo=""
    template_str='''
Demonstration {}:
<CHEMICAL LITERATURE>\n"{}"\n</CHEMICAL LITERATURE>
Output:
'''
    idx=1
    for demo in demo_list:
        sentence=demo['text']
        product_list=demo['products']
        demo_str=template_str.format(idx,sentence)
        idx +=1
        demo_str+=str(product_list)
        res_demo+=demo_str
        res_demo+='\n'
    
    return res_demo



def gen_product_prompt(sentence,demos):
    system_prompt='''
You are a chemical information extraction model
# CONTEXT #
I'm in the planning to build a knowledge graph about chemical organic reactions. I hope to construct this Knowledge Graph by extracting organic reactions from the chemical literature.First, I want to identify the 'Product' entities in the reaction.
# AUDIENCE #
This Chemical Knowledge Graph is for Chemical Experts.I hope that the knowledge graph I build can provide chemistry experts with meaningful knowledge about organic reactions.
# LANGUAGE #
English
'''
    user_prompt='''
# OBJECTIVE #
From the given <<<CHEMICAL LITERATURE>>>, Please identify all entities of Product type.
# ANALYSIS #
Product-type entities are compounds that are produced by chemical reactions.Note: In a given sentence, there may be multiple chemical reactions, and correspondingly there may be multiple Product entities. Please think carefully based on the semantics of the sentence and return a correct and comprehensive recognition result.
# Response Format #
You will respond with a List object in this format and will not respond to anything else:
<format>\n  [Product1,product2,...]
</format>
If there is no product entity in the sentence, return an empty List [] .Please ensure that the returned answer meets the List format
# DEMONSTRATION #
{demos}
# QUESTION #
<CHEMICAL LITERATURE>\n"{sentence}"\n</CHEMICAL LITERATURE>
Output:
'''.format(demos=demos,sentence=sentence)
    messages = [
        {"role": "system", "content": system_prompt},
        {'role': 'user', 'content': user_prompt}
        
    ]
    return messages



def gen_product_sft(sentence):
    instruction='''
You are a chemical information extraction model
# CONTEXT #
I'm in the planning to build a knowledge graph about chemical organic reactions. I hope to construct this Knowledge Graph by extracting organic reactions from the chemical literature.First, I want to identify the 'Product' entities in the reaction.
# AUDIENCE #
This Chemical Knowledge Graph is for Chemical Experts.I hope that the knowledge graph I build can provide chemistry experts with meaningful knowledge about organic reactions.
# LANGUAGE #
English
# OBJECTIVE #
From the given <<<CHEMICAL LITERATURE>>>, Please identify all entities of Product type.
# ANALYSIS #
Product-type entities are compounds that are produced by chemical reactions.Note: In a given sentence, there may be multiple chemical reactions, and correspondingly there may be multiple Product entities. Please think carefully based on the semantics of the sentence and return a correct and comprehensive recognition result.
# Response Format #
You will respond with a List object in this format and will not respond to anything else:
<format>\n  [Product1,product2,...]
</format>
If there is no product entity in the sentence, return an empty List [] .Please ensure that the returned answer meets the List format
'''
    input='''
<CHEMICAL LITERATURE>\n"{sentence}"\n</CHEMICAL LITERATURE>
'''.format(sentence=sentence)
    return instruction,input


def gen_sft_template(sentence,product):
    instruction='''
You are a chemical information extraction model
# CONTEXT #
I'm in the planning to build a knowledge graph about chemical organic reactions. I hope to construct this Knowledge Graph by extracting organic reactions from the chemical literature.
# AUDIENCE #
This Chemical Knowledge Graph is for Chemical Experts.I hope that the knowledge graph I build can provide chemistry experts with meaningful knowledge about organic reactions.
# LANGUAGE #
English
# OBJECTIVE #
From the given <<<CHEMICAL LITERATURE>>> and the Identified <<<Product Entity>>>, Please identify other reaction role entities related to the reaction that produced this product,include: Reactants Catalyst_Reagents Workup_reagents Solvent Yield Temperature and Time
# ANALYSIS #
In the given sentence, we have identified the product entity of the chemical reaction. You need to reason with the context and focus on how to find the other participating role entities of the chemical reaction corresponding to the product entity.Please think step by step.
# Response Format #
You will respond with a JSON object in this format and will not respond to anything else:
<format>\n  {{"entity_type":[entity1,entity2,...],...}}
</format>
If there is no entity of the corresponding entity type, The answer does not need to include the entity type
'''
    input='''
<CHEMICAL LITERATURE>\n"{sentence}"\n</CHEMICAL LITERATURE>
<Product Entity>\n'{product}'\n</Product Entity>
'''.format(sentence=sentence,product=product)
    
    return instruction,input



# zero-shot指的是：在没抽取出product实体的情况下，尝试直接再抽一遍
def gen_zeroshot_prompt(sentence):
    prompt='''
You are a chemical reaction extractor.Based on the given sentence , you need to identify entities associated with the chemical reaction and combine these chemical entities into reactions.Note that there may be multiple reactions in one sentence.\nPlease return in json format.Every reaction's format is as follows:
{{
    "Product":[],
    "Reactants":[],
    "Catalyst_Reagents":[],
    "Workup_reagents":[],
    "Solvent":[],
    "Yield":[],
    "Temperature":[],
    "Time":[]
}}
If there is no corresponding entity in the sentence, the reaction does not need to contain the corresponding entity type
Here is an example of the format:

{{
    "Reactants": [
        "GABA"
    ],
    "Catalyst_Reagents": [
        "GABA aminotransferase"
    ],
    "Product": [
        "succinic semialdehyde"
    ]
}},
{{
    "Reactants": [
        "GABA"
    ],
    "Catalyst_Reagents": [
        "GABA aminotransferase"
    ],
    "Product": [
        "L-glutamate."
    ]
}}

\nIf it does not exist any reaction, answer: {{}}\n
Sentence:"{sentence}"
Answer:
'''.format(sentence=sentence)
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant.Make sure to generate your answers exactly according to the given format and not have any other redundant information.And  generate the answer only once, stop repeating it"},
        {'role': 'user', 'content': prompt}
        
    ]
    return messages