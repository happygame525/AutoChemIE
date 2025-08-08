import easyocr
import os
import json
import math
import shutil
import torch
import numpy as np
from molscribe import MolScribe
from PIL import Image
from yolov5.yolo_out import run

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

        if prepare:
            self.mol_scribe = MolScribe(self.molscribe_ckpt, device=torch.device('cpu'))
            self.reader = easyocr.Reader(['en'], gpu=True)
            self.prepare()
        
        #self.trans = self.id2pdf()


    def prepare(self):
        self.CreateTMP()
        self.CreateYOLOres()
        pdf_name = os.listdir(self.image_root)
        for i in range(len(pdf_name)):
            pname = pdf_name[i]
            if os.path.exists(self.yolo_res+pname+'/yolores.json'):
                print(str(i+1)+'/'+str(len(pdf_name))+' is ready.')
                continue
            if not os.path.exists(self.yolo_res+pname):
                os.makedirs(self.yolo_res+pname)
            imglist = os.listdir(self.image_root+pname)
            res = []
            for iname in imglist:
                dic = {}
                img_path = self.image_root+pname+'/'+iname
                try:
                    mol_res = self.Get_Mol(img_path)
                except:
                    mol_res = []
                ocr_res = self.reader.readtext(img_path,detail=1)
                _ = []
                for item in ocr_res:
                    _.append((self.GetXY(item[0]),item[1]))
                ocr_res = _
                print(ocr_res)
                dic['name'] = iname
                dic['mol'] = mol_res
                dic['ocr'] = ocr_res
                res.append(dic)
            with open(self.yolo_res+pname+'/yolores.json','w') as f:
                json.dump(res,f)
            print(str(i+1)+'/'+str(len(pdf_name))+' done.')
            
        

    def CreateYOLOres(self):
        if not os.path.exists(self.yolo_res):
            os.makedirs(self.yolo_res)

    def CreateTMP(self):
        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path)
        '''
        else:
            shutil.rmtree(self.tmp_path)
        '''

    def GetXY(self,xylist):
        x1,y1 = xylist[0]
        x2,y2 = xylist[1]
        x3,y3 = xylist[2]
        x4,y4 = xylist[3]
        x1 = int(x1)
        x2 = int(x2)
        x3 = int(x3)
        x4 = int(x4)
        y1 = int(y1)
        y2 = int(y2)
        y3 = int(y3)
        y4 = int(y4)
        return (min(min(x1,x2),min(x3,x4)),min(min(y1,y2),min(y3,y4)),max(max(x1,x2),max(x3,x4)),max(max(y1,y2),max(y3,y4)))


    def Get_Mol(self,image_path):
        '''
        ([x1,y1,x2,y2],'smiles'),
        ...
        ...
        '''
        mol_res = run(weights=self.yolo_weight_path, device='4', source=image_path, imgsz=[640])
        mol_res = mol_res[0]
        res = []
        img = Image.open(image_path)
        for mol in mol_res:
            crop_box = (mol[0],mol[1],mol[2],mol[3])
            img_crop = img.crop(crop_box)
            img_crop.save(self.tmp_path + 'tmp.png')
            smiles_res = self.mol_scribe.predict_image_file(self.tmp_path+'tmp.png', return_atoms_bonds=False, return_confidence=False)
            smiles = smiles_res['smiles']
            res.append(([mol[0],mol[1],mol[2],mol[3]],smiles))
        return res

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


    def check(self,idt):
        idt = idt.lower()
        pdf_name = 'test123'
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
                        dic = self.Get_Dis(mol[0],xyxy)
                        if dis < min_dis:
                            min_dis = dis
                            smiles = mol[-1]
                    return smiles
        return None

def get_bbox(num,bboxes,w,h):
    #print(w,h,num)
    #print(bboxes[num]['bbox'])
    #print(transform(bboxes[num]['bbox'],w,h,pred=True))
    return transform(bboxes[num]['bbox'],w,h)

def get_text(name,bbox,reader,tmp_path='./tmp/'):
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    #print(bbox)
    img = Image.open('./result/images/newerror/'+name)
    img_crop = img.crop(bbox)
    img_crop.save(tmp_path+'tmp.png')
    ocr_res = reader.readtext(tmp_path+'tmp.png',detail=1)
    _ = []
    for item in ocr_res:
        _.append(item[1])
    if len(_) == 0:
        return None
    else:
        return _[0]

def get_bboxes(name,gold):
    for image in gold:
        if image['file_name'] == name:
            return image['bboxes'],image['width'],image['height']
    return None

def get_res(name,res):
    for d in res:
        if d['name'] == name:
            return d
    return None

def iou(bb1, bb2):   bb1 = {'x1': bb1[0], 'y1': bb1[1], 'x2': bb1[2], 'y2': bb1[3]}
    bb2 = {'x1': bb2[0], 'y1': bb2[1], 'x2': bb2[2], 'y2': bb2[3]}

    assert bb1['x1'] < bb1['x2']
    assert bb1['y1'] < bb1['y2']
    assert bb2['x1'] < bb2['x2']
    assert bb2['y1'] < bb2['y2']

    
    x_left = max(bb1['x1'], bb2['x1'])
    y_top = max(bb1['y1'], bb2['y1'])
    x_right = min(bb1['x2'], bb2['x2'])
    y_bottom = min(bb1['y2'], bb2['y2'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
    bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou

def transform(bbox,width,height,pred=False):
    if pred:
        x1,y1,x2,y2 = bbox
    else:
        x1,y1,w,h = bbox
        x2,y2 = x1+w,y1+h
        #x1,y1,x2,y2 = x1/width,y1/height,x2/width,y2/height
    #print(x1,y1,x2,y2)
    return (x1,y1,x2,y2)

def Dis(b1,b2):
        return math.sqrt((b1[0]-b2[0])**2 + (b1[1]-b2[1])**2)

def get_dis(xy1,xy2):
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
        res.append(Dis(point1[i],point2[i]))
        
    return min(res)

if __name__ == '__main__':

    pass



        

        

    
    

    


