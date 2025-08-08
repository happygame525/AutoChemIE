import requests
import json
import csv
import random
from openai import OpenAI

def get_name(cid):
    url1 = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'
    url2 = '/property/Title/JSON'
    url = url1+cid+url2
    d = json.loads(get_txt(url))
    #print(cid,d)
    print(d)
    try:
        return d['PropertyTable']['Properties'][0]['Title']
    except:
        return cid
    '''
    try:
        return (d['PropertyTable']['Properties'][0]['Title'],0)
    except:
        url3 = '/property/InChI/JSON'
        url = url1+cid+url3
        d = json.loads(get_txt(url))
        print(d)
        return (d['PropertyTable']['Properties'][0]['InChI'],cid)
    '''
def get_url(name,utype=True):
    base = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/'

    if utype:
        return base+'name/'+name+'/JSON'
    else:
        return base+'smiles/'+name+'/JSON'

def get_txt(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None


def get_prompt(txt1,txt2,c1,c2,pad='\n'):
    head = "You are a chemistry expert, and now you need to determine whether two chemical names are the same chemical substance. Sometimes I will provide you with the chemical information corresponding to these two chemical compounds in JSON format. Please judge and output the result based on the provided information."
    info = "The following is information about two compounds. If the data is None, it means there is no information about this chemical compound and you have to judge by yourself.\n"
    query = "Please judge whether " + c1 + " and " + c2 + " is the same."
    res = "Result: (Directly output YES or NO, do not output explanatory notes)."

    #return head+info+txt1+pad+txt2+pad+res
    return (head,info,res,query,txt1,txt2)

def get_response(prompt):
    head,info,res,query,txt1,txt2 = prompt

    openai_api_key = 'KG'
    openai_api_base = 'http://localhost:8000/v1'

    client = OpenAI(
        api_key = openai_api_key,
        base_url = openai_api_base
    )
    
    response = client.chat.completions.create(
        model="deepseek",
        messages=[
            {"role": "system", "content": head},
            {"role": "user", "content": info},
            {"role": "user", "content": txt1},
            {"role": "user", "content": txt2},
            {"role": "user", "content": query},
            {"role": "user", "content": res},
        ]
    )
    '''
    response = client.chat.completions.create(
        model="deepseek",
        messages=[
            {"role": "system", "content": "You are a chemistry expert, and now you need to determine whether two chemical names are the same chemical substance. Please judge and output the result based on the provided information."},
            {"role": "user", "content": query},
            {"role": "user", "content": res},
        ]
    )
    '''
    res = response.choices[0].message.content
    res = res.split('</think>')[-1]
    res = res.split('\n')[-1]

    return res


def get_data():
    with open('output.json','r') as f:
        output = json.load(f)
    csv_reader = csv.reader(open('train.csv'))
    L = []
    for row in csv_reader:
        L.append(row)
    cnt = 1
    data = []
    for d in output:
        cid = d['cid']
        pred_smiles = d['smiles']
        
        for _ in L:
            cid_ = _[1]
            gold_smiles = _[3]
            if cid == cid_:
                ddd = {}

                ddd['cid'] = cid
                ddd['name'] = get_name(cid)
                ddd['gold_smiles'] = gold_smiles
                ddd['pred_smiles'] = pred_smiles
                data.append(ddd)
                print(cnt,' / ',len(output))
                cnt += 1
                break
    
    with open('data.json','w') as f:
        json.dump(data,f)

def save_metric(precision,recall,f1,p,k=-1,issum=False,filename='metric.json'):
    with open(filename, 'r') as f:
        metric = json.load(f)
    d = {}
    d['p'] = p
    if issum:
        d['precision_sum'] = precision
        d['recall_sum'] = recall
        d['f1'] = f1
    else:
        d['k'] = k
        d['precision'] = precision
        d['recall'] = recall
        d['f1'] = f1
    metric.append(d)
    with open(filename,'w') as f:
        json.dump(metric,f)

def main(K,P):
    with open('data.json','r') as f:
        data = json.load(f)
    for p in P:
        p *= 10
        for k in range(K):
            if k == 0 or k == 1:
                continue
            print(p/10,k)
            random.shuffle(data)

            tp = 0
            tn = 0
            fp = 0
            fn = 0

            num = 200
            for i in range(len(data)):
                name = data[i]['name']
                if i >= num:
                    smiles = data[i]['gold_smiles']
                else:
                    smiles = data[i]['pred_smiles']
                
                name_txt = get_txt(get_url(name))
                smiles_txt = get_txt(get_url(smiles,utype=False))

                if name_txt is None:
                    name_txt = 'None.'
                    rn = random.randint(0,9)
                    if rn < p:
                        name_txt = get_txt('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/'+data[i]['cid']+'/JSON')
                if smiles_txt is None:
                    smiles_txt = 'None.'

                res = get_response(get_prompt(name_txt,smiles_txt,name,smiles))
                res = res.lower()
                if i >= num and 'yes' in res:
                    tp += 1
                elif i < num and 'no' in res:
                    tn += 1
                elif i >= num and 'no' in res:
                    fn += 1
                elif i < num and 'yes' in res:
                    fp += 1
                #print(tp,tn,fn,fp,res)
                
            print('='*20)
            print('P = ',p/10,'k = ',k)
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            f1 = (2*precision*recall)/(precision+recall)
            print('Precision: ', precision)
            print('Recall: ', recall)
            print('F1: ', f1)
            print('='*20)
            save_metric(precision,recall,f1,p=p/10,k=k)
            

if __name__ == '__main__':
    with open('metric.json', 'r') as f:
        data = json.load(f)

    for p in [0.0,0.5,0.7,0.9,1.0]:
        precision_sum = 0
        recall_sum = 0
        f1_sum = 0
        error = 0
        for m in data:
            if m['p'] == p:
                precision_sum += m['precision']
                recall_sum += m['recall']
                f1_sum += m['f1']
                error += 1
        if error != 5:
            print('error')
            break
        precision_sum /= 5
        recall_sum /= 5
        f1_sum /= 5
        print('='*20)
        print('p = ', p)
        print('precision = ',precision_sum)
        print('recall = ',recall_sum)
        print('f1 = ',f1_sum)
        print('='*20)
