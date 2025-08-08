import json
import sys
import os
import random
from seqeval.metrics.sequence_labeling import get_entities
base_dir=os.path.dirname(os.path.abspath(__file__))

r'''
    功能：将实体识别的BIO的数据格式转换为我们需要的数据格式
    数据的格式示例：
        [
            {
                "text":,
                'metainfo':,
                'reactions':[{},{}]
            },
        ]
'''
def data_transfer(input_file,out_file=None):
    pass
    data_list=[]
    
    with open(input_file, encoding="utf-8") as f:
        words, labels = [], []
        metainfo = None
        for line in f:
            line = line.rstrip()#去除右侧空白字符
            if line.startswith("#\tpassage"):
                metainfo = line
            elif line == "":
                if words:
                        data_item={}
                        text=''
                        for i,word in enumerate(words):
                             text+=word
                             if i !=len(words)-1:
                                text+=' '
                        data_item['text']=text
                        data_item['metainfo']=metainfo
                        labels_by_prod = list(zip(*labels))
                        #print(labels_by_prod)
                        data_item['reactions']=[]
                        for y in labels_by_prod:
                            #针对一条反应的 标注序列
                            entities = get_entities(list(y))
                            #[('Prod', 9, 9), ('Reactants', 17, 17), ('Reactants', 21, 21), ('Solvent', 25, 25), ('Temperature', 27, 29)]
                            #print(entities)
                            reaction_item={}
                            for entity in entities:
                                entity_label=entity[0]
                                if entity_label=='Reaction':continue
                                if entity_label=='Prod':
                                     entity_label='Product'
                                entity_beg=entity[1]
                                entity_end=entity[2]
                                entity_words=""
                                for i in range(entity_beg,entity_end+1):
                                     entity_words+=words[i]
                                     if i !=entity_end:
                                        entity_words+=' '
                                if entity_label not in reaction_item:
                                    reaction_item[entity_label]=[]
                                reaction_item[entity_label].append(entity_words)
                            data_item['reactions'].append(reaction_item)
                        data_list.append(data_item)
                        words, labels = [], []
                        
                       
            else:
                cols = line.split("\t")
                words.append(cols[0])
                if len(cols) > 1:
                    labels.append(cols[1:])
                else:
                    labels.append(["O"])
    #print(data_list)
    return data_list


def write_dict_to_file(data,file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False,indent=4)
    

def read_json_file(data_dir):
    with open(data_dir,'r',encoding='utf-8') as file:
            data=json.load(file)
    return data

def get_data():
    train_dir=base_dir+'/data/train.json'
    test_dir=base_dir+'/data/test.json'
    train_data=read_json_file(train_dir)
    test_data=read_json_file(test_dir)
    return train_data,test_data

def get_devdata():
    train_dir=base_dir+'/data/train.json'
    dev_dir=base_dir+'/data/dev.json'
    train_data=read_json_file(train_dir)
    dev_data=read_json_file(dev_dir)
    return train_data,dev_data

def get_productdata():
    train_dir='/data/lizh/ChemRxnExtractor-main/llm_role/data/prod/train.json'
    dev_dir='/data/lizh/ChemRxnExtractor-main/llm_role/data/prod/test.json'
    train_data=read_json_file(train_dir)
    dev_data=read_json_file(dev_dir)

    return train_data,dev_data


if __name__ == "__main__":
    biodir=base_dir+"/data/roledata"
    output_dir=base_dir+'/data'
    for fdir in os.listdir(biodir):
        data_dir=os.path.join(biodir,fdir)
        data_list=data_transfer(data_dir)
        if 'dev' in fdir:
            write_dict_to_file(data_list,os.path.join(output_dir,'dev.json'))
        elif 'train' in fdir:
            write_dict_to_file(data_list,os.path.join(output_dir,'train.json'))
        elif 'test' in fdir:
            write_dict_to_file(data_list,os.path.join(output_dir,'test.json'))
    pass
    
