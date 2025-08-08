from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher#导入我们需要的头文件
import pandas as pd
import os
import json
import csv

current_file_path = os.path.abspath(__file__)
base_dir=os.path.dirname(current_file_path)

graph = Graph('http://localhost:7474',auth=('neo4j','123456'), name = 'neo4j')
entity_matcher = NodeMatcher(graph)
rel_matcher=RelationshipMatcher(graph)


# A = Node("概念", name="向量")
# B = Node("概念", name="向量")
# graph.create(A)
# graph.create(B)

# graph.delete_all()
# print("删除成功")
# # 查询节点数量
# node_count_query = "MATCH (n) RETURN count(n) AS node_count"
# node_count_result = graph.run(node_count_query).data()

# # 查询关系数量
# relationship_count_query = "MATCH ()-[r]->() RETURN count(r) AS relationship_count"
# relationship_count_result = graph.run(relationship_count_query).data()

# # 打印结果
# print("Number of nodes:", node_count_result[0]['node_count'])
# print("Number of relationships:", relationship_count_result[0]['relationship_count'])

def delete_all():
    graph.delete_all()
    print("删除成功")


#增加实体
def add_ent(label,name):
    a=Node(label,name=name)
    existing_nodes = entity_matcher.match(label,name=name).first()
    # existing_nodes = entity_matcher.match(label).where("name = $name").params(name=name).first()
    if existing_nodes is None:
        graph.create(a)
    else:
        print("该实体已存在于图谱中")
#增加关系
def add_rel(head_name,head_label,tail_name,tail_label,label):
    head=entity_matcher.match(head_label,name=head_name).first()
    tail=entity_matcher.match(tail_label,name=tail_name).first()

    rel=Relationship(head,label,tail)

    existing_relationship = rel_matcher.match(nodes=[head, tail], r_type=label).first()

    if existing_relationship is None:
        graph.create(rel)
    
    else:
        print("该关系已经存在于图谱中")


# 向实体加入属性
def add_entity_properties(label, name, properties):
    existing_node = entity_matcher.match(label, name=name).first()
    if existing_node is None:
        # 如果实体不存在，则创建一个新的实体并添加属性
        new_node = Node(label, name=name, **properties)
        graph.create(new_node)
    else:
        # 如果实体已存在，则更新其属性
        for key, value in properties.items():
            existing_node[key] = value
        graph.push(existing_node)  # 将更新后的节点推送到图数据库中
        

def read_jsonl_file(file_path):
    data=[]
    with open(file_path, "r",encoding='utf-8') as f:
        for line in f.read().splitlines():
            tmp_data = json.loads(line)
            data.append(tmp_data)

    return data

def read_json_file(file_path):
    with open(file_path, "r",encoding='utf-8') as f:
        data=json.load(f)
    
    return data

def jsonl2csv(jsonl_dir,csv_dir):
    json_data=read_jsonl_file(jsonl_dir)
    df = pd.DataFrame(json_data)
    df.to_csv(csv_dir, encoding='utf-8',index=False)

def read_csv(csv_dir):
    with open(csv_dir, 'r', encoding='utf-8',newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            print(type(row[2]))

r'''
抽取的json格式:
{
    "battery_name":"",
    "anode":"",
    "cathode":"",
    "partition":"",
    "electrolyte":{
        "name":"",
        "solute":"",
        "solvent":"",
        "diluent":"",
        "proportion":"",
        "temperature":""
    }
}

知识图谱的格式：
实体： Reactants Product Catalyst_Reagents Workup_reagents Reaction Solvent Yield Temperature Time 


关系:
(Reaction,has_Reactants,Reactants)
(Reaction,gen_product,Product)
(Reaction,has_Catalyst,Catalyst_Reagents)
(Reaction,has_Workup,Workup_reagents)
(Reaction,has_Solvent,Solvent)
Yield Temperature Time 作为reaction的属性




'''
def check(item):
    if 'None' in item or "None specified" in item:
        return False
    return True

def handle_chem(data_dir):
    data=read_json_file(data_dir)
    for i,item in enumerate(data):
        battery=item["battery_name"]
        anode=item['anode']
        cathode=item['cathode']
        partition=item['partition']
        electrolyte_set=item['electrolyte']
        electrolyte=electrolyte_set['name']
        solute=electrolyte_set['solute']
        solvent=electrolyte_set['solvent']
        diluent=electrolyte_set['diluent']
        proportion=electrolyte_set['proportion']
        temperature=electrolyte_set['temperature']

        #实体
        if check(battery):
            add_ent("battery_name",battery)
        if check(anode):
            add_ent("anode",anode)
        if check(cathode):
            add_ent("cathode",cathode)
        if check(partition):
            add_ent("partition",partition)
        if check(electrolyte):
            add_ent("electrolyte",electrolyte)
        if check(solute):
            add_ent("solute",solute)
        if check(solvent):
            add_ent("solvent",solvent)
        if check(diluent):
            add_ent("diluent",diluent)
        if check(proportion):
            add_ent("proportion",proportion)
        if check(temperature):
            add_ent("temperature",temperature)

        #关系
        if check(battery) and check(anode):
            add_rel(anode,"anode",battery,"battery_name","belong_to")

        if check(battery) and check(cathode):
            add_rel(cathode,"cathode",battery,"battery_name","belong_to")

        if check(battery) and check(partition):
            add_rel(partition,"partition",battery,"battery_name","belong_to")

        if check(battery) and check(electrolyte):
            add_rel(electrolyte,"electrolyte",battery,"battery_name","belong_to")

        if check(solvent) and check(electrolyte):
            add_rel(solvent,"solvent",electrolyte,"electrolyte","belong_to")

        if check(solute) and check(electrolyte):
            add_rel(solute,"solute",electrolyte,"electrolyte","belong_to")

        if check(diluent) and check(electrolyte):
            add_rel(diluent,"diluent",electrolyte,"electrolyte","belong_to")

        if check(proportion) and check(electrolyte):
            add_rel(proportion,"proportion",electrolyte,"electrolyte","belong_to")

        if check(temperature) and check(electrolyte):
            add_rel(temperature,"temperature",electrolyte,"electrolyte","belong_to")

        print("第{}条数据处理完成！".format(i))

def handle_data(data_dir):
    data=read_json_file(data_dir)
    for i ,data_item in enumerate(data):
        print("正在处理第{}条数据".format(i))
        add_ent('Reaction',i)
        
        for key,value_list in data_item.items():
            
            if key=='text' or key=='Reaction':continue
           
            if key=='Reactants':
                for value in value_list:
                    add_ent(key,value)
                    add_rel(i,'Reaction',value,'Reactants','has_Reactants')
            elif key=='Product':
                for value in value_list:
                    add_ent(key,value)
                    add_rel(i,'Reaction',value,'Product','gen_product')
            elif key=='Catalyst_Reagents':
                for value in value_list:
                    add_ent(key,value)
                    add_rel(i,'Reaction',value,'Catalyst_Reagents','has_Catalyst')
            elif key=='Workup_reagents':
                for value in value_list:
                    add_ent(key,value)
                    add_rel(i,'Reaction',value,'Workup_reagents','has_Workup')
            elif key=='Solvent':
                for value in value_list:
                    add_ent(key,value)
                    add_rel(i,'Reaction',value,'Solvent','has_Solvent')    
            elif key=='Yield':
                f_dict={}
                data=value_list[0]
                f_dict[key]=data
                add_entity_properties('Reaction',i,f_dict)
            elif key=='Temperature':
                f_dict={}
                data=value_list[0]
                f_dict[key]=data
                add_entity_properties('Reaction',i,f_dict)
            elif key=='Time':
                f_dict={}
                data=value_list[0]
                f_dict[key]=data
                add_entity_properties('Reaction',i,f_dict)
                

if __name__=="__main__":
    #delete_all()
    # data_dir=base_dir+"/paper_res.json"
    # data=read_json_file(data_dir)
    # print(len(data))
    #handle_data(data_dir)
    
    data_dir=base_dir+"/paper_merge_res.json"
    handle_data(data_dir)
    pass
    # dir=base_dir="valid.json"
    # res=[]
    # for i in range(1,81):
    #     str="{}.pdf".format(i)
    #     dict={}
    #     dict['source']=str
    #     dict['result']=""
    #     res.append(dict)

    # with open(dir,"w",encoding='utf-8') as f:
    #     json.dump(res,f,indent=4,ensure_ascii=False)