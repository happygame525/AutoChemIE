import os
import json
import math
import shutil

import warnings
warnings.filterwarnings("ignore")

class IDT():

    def __init__(self, prepare=False):
        self.root = './result/'
        self.image_root = './result/images/'
        self.coref_root = './result/result/'
        self.yolo_res = './result/yolores/'
        self.yolo_weight_path = './yolov5/runs/train/mol/weights/best.pt'
        self.molscribe_ckpt = './ckpts/swin_base_char_aux_1m.pth'
        self.tmp_path = './tmp/'
        
        self.trans = self.id2pdf()

        
    def id2pdf(self):
        dic = {}
        with open('paper.json', 'r') as f:
            data = json.load(f)
        for d in data:
            dic[d['id']] = d['filename'].split('.pdf')[0]
        return dic

    def Dis(self,b1,b2):
        return math.sqrt((b1[0]-b2[0])**2 + (b1[1]-b2[1])**2)

    def Get_Dis(self,xy1,xy2):
        res = []
        point1 = []
        point2 = []
        point1.append((xy1[0],xy1[1]))
        point1.append((xy1[2],xy1[1]))
        point1.append((xy1[0],xy1[3]))
        point1.append((xy1[2],xy1[3]))
        point1.append(((xy1[0]+xy1[2])/2,(xy1[1]+xy1[3])/2))
        point1.append(((xy1[0]+xy1[2])/2,xy1[1]))
        point1.append(((xy1[0]+xy1[2])/2,xy1[3]))
        point1.append((xy1[0],(xy1[1]+xy1[3])/2))
        point1.append((xy1[2],(xy1[1]+xy1[3])/2))

        point2.append((xy2[0],xy2[1]))
        point2.append((xy2[2],xy2[1]))
        point2.append((xy2[0],xy2[3]))
        point2.append((xy2[2],xy2[3]))
        point2.append(((xy2[0]+xy2[2])/2,(xy2[1]+xy2[3])/2))
        point2.append(((xy2[0]+xy2[2])/2,xy2[1]))
        point2.append(((xy2[0]+xy2[2])/2,xy2[3]))
        point2.append((xy2[0],(xy2[1]+xy2[3])/2))
        point2.append((xy2[2],(xy2[1]+xy2[3])/2))

        for i in range(len(point1)):
            res.append(self.Dis(point1[i],point2[i]))
        
        return min(res)

    def Get_Coref(self,pdf_name):
        try:
            with open(self.coref_root+pdf_name+'/coref_res.json', 'r') as f:
                data = json.load(f)
                return data
        except:
            return None


    def check(self,fileid,idt):
        idt = idt.lower()
        pdf_name = self.trans[fileid]
        try:
            with open(self.yolo_res+pdf_name+'/yolores.json','r') as f:
                res = json.load(f)
        except:
            res = []
        coref = self.Get_Coref(pdf_name)
        try:
            for k in coref.keys():
                if idt in k:
                    return coref[k]
        except:
            pass
        for dic in res:
            mol_res = dic['mol']
            ocr_res = dic['ocr']
            for bbox in ocr_res:
                xyxy = bbox[0]
                text = bbox[1]
                text = text.lower()
                if idt in text:
                    min_dis = 100000
                    smiles = None
                    for mol in mol_res:
                        dis = self.Get_Dis(mol[0],xyxy)
                        if dis < min_dis:
                            min_dis = dis
                            smiles = mol[-1]
                    return smiles
        return None

if __name__ == '__main__':
    idt = IDT()   
    idt.check(id, idt)

    idt = IDT()
    while True:
        fid = int(input('id:'))
        idt_ = input('idt:')

        print(idt.check(fid,idt_))
