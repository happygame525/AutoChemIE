r'''
使用bge进行向量嵌入 
'''
from FlagEmbedding import FlagModel
from data_process import *
import os
base_dir=os.path.dirname(os.path.abspath(__file__))

def bge_test():
    pass
    model = FlagModel('/data/lizh/models/bge-large-en',
                                      query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
                                      use_fp16=True)
    sentences_1 = ["I love NLP"]
    sentences_2 = ["I love BGE"]
    embeddings_1 = model.encode(sentences_1)
    embeddings_2 = model.encode(sentences_2)
    similarity = embeddings_1 @ embeddings_2.T
    print(similarity)

#bge_test()
# 生成相似度矩阵
def bge_matrix(train_data,test_data,save_dir):
    pass
    model = FlagModel('/data/lizh/models/bge-large-en',
                                      query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
                                      use_fp16=True)
    train_sentence=[]
    test_sentence=[]

    for item in train_data:
        train_sentence.append(item['text'])

    for item in test_data:
        test_sentence.append(item['text'])

    train_embeddings=model.encode(train_sentence)
    test_embeddings=model.encode(test_sentence)

    matrix=test_embeddings @ train_embeddings.T

    res=[]
    for i in range(len(test_sentence)):
        sentence=test_sentence[i]
        matrix_item={"sentence":"","sim_list":[]}
        matrix_item['sentence']=sentence
        matrix_item['sim_list']=matrix[i].tolist()
        res.append(matrix_item)
    write_dict_to_file(res,save_dir)

#生成product类实体的相似度矩阵
def prod_matrix(train_data,test_data,save_dir):
    model = FlagModel('/data/lizh/models/bge-large-en',
                                      query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
                                      use_fp16=True)
    train_sentence=[]
    test_sentence=[]

    for item in train_data:
        train_sentence.append(item['text'])

    for item in test_data:
        test_sentence.append(item['text'])

    train_embeddings=model.encode(train_sentence)
    test_embeddings=model.encode(test_sentence)

    matrix=test_embeddings @ train_embeddings.T

    res=[]
    for i in range(len(test_sentence)):
        sentence=test_sentence[i]
        matrix_item={"sentence":"","sim_list":[]}
        matrix_item['sentence']=sentence
        matrix_item['sim_list']=matrix[i].tolist()
        res.append(matrix_item)
    write_dict_to_file(res,save_dir)


if __name__=="__main__":
    pass
    train_data,test_data=get_devdata()
    bge_matrix(train_data,test_data,base_dir+'/bge_dev_matrix.json')

    # #生成product类实体的相似度矩阵
    # train_data,test_data=get_productdata()
    # prod_matrix(train_data,test_data,base_dir+'/prod_matrix.json')
