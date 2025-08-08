import json
import shutil
import os
from urllib.request import urlretrieve
import requests
import csv
import random
import torch
from molscribe import MolScribe

def check(cid):
    pass


def scan_img(img_path="images/",ckpt_path="ckpts/swin_base_char_aux_1m.pth"):

    res = []
    model = MolScribe(ckpt_path,device=torch.device('cpu'))

    imglist = os.listdir(img_path)
    cnt = 1
    for img in imglist:
        d = {}
        cid = img.split('.png')[0]
        d['cid'] = cid
        
        p = img_path+img
        output = model.predict_image_file(p)
        d['smiles'] = output['smiles']
        res.append(d)
        print(str(cnt)+' / 400 done.')
        cnt += 1
    with open('output.json','w') as f:
        json.dump(res,f)



def get_url(cid):
    return "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"+cid+"/PNG"

def download_img(url,file_path):
    urlretrieve(url,file_path)

def read_csv(csv_path):
    csv_reader = csv.reader(open(csv_path))

    return csv_reader

def random_select(L,num=400):
    return random.sample(L,num)

def solve(csv_path="train.csv"):
    

    csv_reader = read_csv(csv_path)
    L = []
    for row in csv_reader:
        L.append(row)
    L = random_select(L)
    cnt = 1
    for mol in L:
        cid = mol[1]
        inchi = mol[2]
        smiles = mol[3]
        url = get_url(cid)
        img_name = cid+'.png'
        download_img(url,'images/'+img_name)
        print(str(cnt)+' / 400 done.')

if __name__ == '__main__':
    scan_img()
