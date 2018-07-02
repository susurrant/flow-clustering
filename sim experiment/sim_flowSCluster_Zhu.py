# -*- coding: utf-8 -*-：

import os
import operator
import math
import csv
import sys


#读取OD点坐标
def readData(fileName):
    data = []
    sp = []
    ep = []
    w = []
    lst = []
    let = []
    
    with open(fileName, 'r') as f:
        f.readline()
        while True:
            line = f.readline()
            if line:
                sl = line.split(',')
                if len(sl) > 1:
                    d = [float(sl[1]),float(sl[2]),float(sl[3]),float(sl[4])]
                    sp.append((float(sl[1]),float(sl[2])))
                    ep.append((float(sl[3]),float(sl[4])))
                    data.append(d)
                    lst.append(int(sl[5]))
                    let.append(int(sl[6]))
                    w.append(int(sl[-1]))
            else:
                break

    return data, sp, ep, lst, let, w


def dis(p1, p2):
    return math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)

    
#计算第i个数据点的k个近邻点,返回近邻点序号列表
def KNN(i, p, k):
    n = []
    r = []
    for j in range(len(p)):
        if j != i:
            d = dis(p[i], p[j])
            r.append([j,d])
    orderedR = sorted(r, key = operator.itemgetter(1), reverse = False)
    
    for j in range(k):
        n.append(orderedR[j][0])
        
    return n

def KNNFlows(i, K, sp, ep):
    nf = []
    ksp = KNN(i, sp, K)
    kep = KNN(i, ep, K)
    for j in range(len(sp)):
        if i == j:
            continue
        if j in ksp and j in kep:
            nf.append(j)
    return nf

def NCO(op, pt):
    tp = None
    mindis = float('inf')
    for p in pt:
        if dis(op, p) < mindis:
            mindis = dis(op, p)
            tp = p
    return tp

#计算clusterID为no的中心流坐标
def calcClusterFlow(ci, data):
    ox = 0
    oy = 0
    dx = 0
    dy = 0
    d = float(len(ci))

    for k in ci:
        ox += data[k][0]
        oy += data[k][1]
        dx += data[k][2]
        dy += data[k][3]

    ox /= d
    oy /= d
    dx /= d
    dy /= d
    return ox, oy, dx, dy

def KNNP(tp, p, k):
    n = set()
    r = []
    for j in range(len(p)):
        if abs(tp[0]-p[j][0])<0.00001 and abs(tp[1]-p[j][1])<0.00001 :
            continue
        d = dis(tp, p[j])
        r.append([j,d])
    orderedR = sorted(r, key = operator.itemgetter(1), reverse = False)
    
    for j in range(k):
        n.add(orderedR[j][0])
        
    return n
    

#计算clusterID为ci和cj的两个类的相似性
def clusterSim(ci, cj, data, sp, ep, k):
    oix, oiy, dix, diy = calcClusterFlow(ci, data)
    ojx, ojy, djx, djy = calcClusterFlow(cj, data)

    oi = NCO((oix, oiy), sp)
    di = NCO((dix, diy), ep)
    oj = NCO((ojx, ojy), sp)
    dj = NCO((djx, djy), ep)

    knnoi = KNNP(oi, sp, k)
    knndi = KNNP(di, ep, k)
    knnoj = KNNP(oj, sp, k)
    knndj = KNNP(dj, ep, k)
    
    dist = 1 - float(len(knnoi&knnoj) * len(knndi&knndj)) / float(k*k)
    return dist

def clusterSim_origin(ci, cj, sp, ep, k):
    dis = 0
    n = 0
    for fi in ci:
        knnoi = set(KNN(fi, sp, k))
        knndi = set(KNN(fi, ep, k))
        for fj in cj:
            knnoj = set(KNN(fj, sp, k))
            knndj = set(KNN(fj, ep, k))
            tdis = 1 - float(len(knnoi&knnoj) * len(knndi&knndj)) / float(k*k)
            dis += tdis
            n += 1
    return dis/float(n)

#合并相似度高的类
def merge(c, ci, cj, l):
    # 保留小数字的clusterID
    if ci > cj:
        ci, cj = cj, ci

    for lid in c[cj]:
        l[lid] = ci
        c[ci].append(lid)
    c.pop(cj)


#输出带类标签的OD数据到csv格式文件
def outputSLabeledData(filename, data, l, lst, let, w):
    rf = open(filename, 'wb')
    sheet = csv.writer(rf)
    sheet.writerow(['id','x1','y1','x2','y2','st','et','w','cluster'])
    for i in range(len(data)):
        r = [i]
        r.extend(data[i])
        r.append(lst[i])
        r.append(let[i])
        r.append(w[i])
        r.append(l[i])
        sheet.writerow(r)
    rf.close()


#输出空间类数据，包括clusterID，类中心流坐标，包含的流的个数
def outputSClusterData(filename, data, c):
    rf = open(filename, 'wb')
    sheet = csv.writer(rf)
    sheet.writerow(['clusterID','ox','oy','dx','dy','flownum'])
    for i in c:
        if len(c[i]) > 0:
            ox, oy, dx, dy = calcClusterFlow(c[i], data)
            sheet.writerow([i, ox, oy, dx, dy, len(c[i])])
    rf.close()


if __name__ == '__main__':
    print('Running ', sys.argv[0])

    #空间聚类参数
    K = 3         #近邻数
    dataFile = 'sim flows.csv'
    ldataFile = 'lData_sim '+str(K)+'_Zhu.csv'
    clusterFile = 'cData_sim '+str(K)+'_Zhu.csv'

    print('file: ', dataFile)
    print('k =', K)

    if os.path.exists(ldataFile):
        os.remove(ldataFile)

    if os.path.exists(clusterFile):
        os.remove(clusterFile)

    #----------------------------初始化------------------------------------
    data, sp, ep, lst, let, w = readData(dataFile)
    dataLen = len(data)
    c = {} #类集合
    l = [] #数据标签集合
    #初始化时第i类只包括第i个数据，第i个数据的数据标签为第i类
    for i in range(dataLen):
        c[i] = [i] #类编号(整数编号)，包含的流编号
        l.append(i)        #流的类标签

    #----------------------------空间聚类----------------------------------
    for i in range(dataLen):
        knn = KNNFlows(i, K, sp, ep)
        #print knn
        for j in knn:
            if l[i] != l[j]: #如果第i条流和第j条流不属于同一类
                if clusterSim_origin(c[l[i]], c[l[j]], sp, ep, K) < 1:
                    merge(c, l[i], l[j], l)



    outputSLabeledData(ldataFile, data, l, lst, let, w)
    #outputSClusterData(clusterFile, data, c)
