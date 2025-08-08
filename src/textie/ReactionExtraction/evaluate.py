r'''
对化学反应抽取结果进行评估 使用F1分数
'''

r'''
数据格式：
{
        "text": "As observed for the glycosylations of the 4-OH acceptor 7 , the use of equimolar proportions of the donor 6 and the acceptor 16 , in glycosylation reactions , led to the isolation of significant quantities of the glucal 9 and low yields of the disaccharides.",
        "metainfo": "#\tpassage=10.1021/ja00144a001-8\tsegment=1",
        "reactions": [
            {
                "Yield": [
                    "significant quantities"
                ],
                "Product": [
                    "9"
                ]
            },
            {
                "Yield": [
                    "low"
                ],
                "Product": [
                    "disaccharides."
                ]
            }
        ]
    }
'''



class NER_f1():
    def __init__(self,std_data,pre_data) :
        num=len(std_data)
        self.TP=0
        self.FP=0
        self.FN=0

        for i in range(num):
            std_reactions=std_data[i]["reactions"]
            pre_reactions=pre_data[i]["reactions"]
            self.calculate(std_reactions,pre_reactions)
            # for std_reaction,pre_reaction in zip(std_reactions,pre_reactions):
            #     self.calculate(std_reaction,pre_reaction)
            

        print("TP, FP, FN", self.TP, self.FP, self.FN)

        self.precision = self.TP/(self.TP+self.FP)
        self.recall = self.TP/(self.TP+self.FN)

        print("NER:  precision, recall", self.precision, self.recall)

        self.f1_score = 2 * self.precision * self.recall/(self.precision + self.recall)
        print("NER:  f1_score", self.f1_score)


    def calculate(self,std_reactions,pre_reactions):
        std_res=[]
        pre_res=[]

        # for std_reaction in std_reactions:
        #     target_product=std_reaction['Product']
        #     for pre_reaction in pre_reactions:
        #         if pre_reaction['Product']==target_product:
        #             for std_key,std_values in std_reaction.items():
        #                 for pre_key,pre_values in pre_reaction.items():
        #                     if pre_key==std_key and pre_values==std_values:
        #                         self.TP+=1

        for std_reaction in std_reactions:
            for key,values in std_reaction.items():
                for value in values:
                    tuple=(value,key)
                    std_res.append(tuple)
        for pre_reaction in pre_reactions:
            for key,values in pre_reaction.items():
                for value in values:
                    tuple=(value,key)
                    pre_res.append(tuple)
        


        #开始统计指标
        for i in std_res:
            if i in pre_res:
                self.TP+=1
            else:
                self.FN+=1
        
        for i in pre_res:
            if i not in std_res:
                self.FP+=1


class Reaction_f1():
    def __init__(self,std_data,pre_data):
        pass
        num=len(std_data)
        self.TP=0
        self.FP=0
        self.FN=0

        for i in range(num):
            std_reactions=std_data[i]["reactions"]
            pre_reactions=pre_data[i]["reactions"]
            self.calculate(std_reactions,pre_reactions)

        print("TP, FP, FN", self.TP, self.FP, self.FN)

        self.precision = self.TP/(self.TP+self.FP)
        self.recall = self.TP/(self.TP+self.FN)

        print("NER:  precision, recall", self.precision, self.recall)

        self.f1_score = 2 * self.precision * self.recall/(self.precision + self.recall)
        print("NER:  f1_score", self.f1_score)

    def calculate(self,std_reactions,pre_reactions):
        pass
        std_res=[]
        pre_res=[]

        for std_reaction in std_reactions:
            product=std_reaction['Product'][0]
            for key,values in std_reaction.items():
                #if key=='Product':continue

                for value in values:
                    tuple=(product,key,value)
                    std_res.append(tuple)

        for pre_reaction in pre_reactions:
            if 'Product' not in pre_reaction:continue
            if pre_reaction['Product']==[]:continue
            product=pre_reaction['Product'][0]
            for key,values in pre_reaction.items():
                #if key=='Product':continue
                for value in values:
                    tuple=(product,key,value)
                    pre_res.append(tuple)
        


        #开始统计指标
        for i in std_res:
            if i in pre_res:
                self.TP+=1
            else:
                self.FN+=1
        
        for i in pre_res:
            if i not in std_res:
                self.FP+=1
        


class Product_f1():
    def __init__(self,std_data,pre_data):
        pass
        num=len(std_data)
        self.TP=0
        self.FP=0
        self.FN=0

        for i in range(num):
            std_products=std_data[i]['products']
            pre_products=pre_data[i]['products']
            self.calculate(std_products,pre_products)
           
        

        print("TP, FP, FN", self.TP, self.FP, self.FN)

        self.precision = self.TP/(self.TP+self.FP)
        self.recall = self.TP/(self.TP+self.FN)

        print("NER:  precision, recall", self.precision, self.recall)

        self.f1_score = 2 * self.precision * self.recall/(self.precision + self.recall)
        print("NER:  f1_score", self.f1_score)


    def calculate(self,std_products,pre_products):
        pass
        std_res=[]
        pre_res=[]

        for std_product in std_products:
            tuple=('Product',std_product)
            std_res.append(tuple)
            
        for pre_product in pre_products:
            tuple=('Product',pre_product)
            pre_res.append(tuple)


        #开始统计指标
        for i in std_res:
            if i in pre_res:
                self.TP+=1
            else:
                self.FN+=1
        
        for i in pre_res:
            if i not in std_res:
                self.FP+=1
    
    def getf1(self):
        return self.precision,self.recall,self.f1_score