r'''
针对输入的句子检索相似度最高的k条句子返回
'''
from  data_process import  *

#注意:下面的代码返回的仅仅是一个索引 
def bge_retrieval(sentence,k=3):
    save_dir='/data/lizh/ChemRxnExtractor-main/llm_role/bge_matrix.json'
    matrix=read_json_file(save_dir)
    

    for pre_item in matrix:
        if pre_item['sentence']==sentence:
            candidate_data=pre_item['sim_list']

            max_indices=find_max_k_indices(candidate_data,k)

    return max_indices
    
def prod_retrieval(sentence,k=3):
    save_dir='/data/lizh/ChemRxnExtractor-main/llm_role/prod_matrix.json'
    matrix=read_json_file(save_dir)
    

    for pre_item in matrix:
        if pre_item['sentence']==sentence:
            candidate_data=pre_item['sim_list']

            max_indices=find_max_k_indices(candidate_data,k)

    return max_indices


def find_max_k_indices(lst, k):
    indexed_lst = [(i, val) for i, val in enumerate(lst)]
    indexed_lst.sort(key=lambda x: x[1], reverse=True)
    max_indices = [indexed[0] for indexed in indexed_lst[:k]]
    return max_indices

if __name__=="__main__":
    pass
    matrix=read_json_file('/data/lizh/ChemRxnExtractor-main/llm_role/bge_matrix.json')
    item=matrix[0]
    candidate=item['sim_list']
    max_indices=find_max_k_indices(candidate,3)
    print(max_indices)