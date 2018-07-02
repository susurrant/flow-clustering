# -*- coding: utf-8 -*-：

import os
import operator
import math
import csv
import sys



#读取OD点坐标
def readData(fileName):
    data = []
    midPnt = []
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
                    midPnt.append(((float(sl[1])+float(sl[3]))/2.0, (float(sl[2])+float(sl[4]))/2.0))
                    data.append(d)
                    lst.append(int(sl[5]))
                    let.append(int(sl[6]))
                    w.append(int(sl[-1]))
            else:
                break

    return data, midPnt, lst, let, w


def dis(p1, p2):
    return math.sqrt((p2[0]-p1[0])*(p2[0]-p1[0])+(p2[1]-p1[1])*(p2[1]-p1[1]))

    
#计算第i个数据中点的k个近邻点,返回近邻点序号列表
def KNN(i, k, midPnt):
    n = []
    r = []
    for j in range(len(midPnt)):
        if j != i:
            d = dis(midPnt[i], midPnt[j])
            r.append([j,d])
    orderedR = sorted(r, key = operator.itemgetter(1), reverse = False)
    
    for j in range(k):
        n.append(orderedR[j][0])
        
    return n

# 计算cluster的中心流坐标
def calcClusterFlow(c, data):
    ox = 0
    oy = 0
    dx = 0
    dy = 0
    for k in c:
        ox += data[k][0]
        oy += data[k][1]
        dx += data[k][2]
        dy += data[k][3]
    d = float(len(c))

    ox /= d
    oy /= d
    dx /= d
    dy /= d
    return ox, oy, dx, dy

#计算ci和cj的两个类的相似性
def clusterSim(ci, cj, data, rr):
    oix, oiy, dix, diy = calcClusterFlow(ci, data)
    ojx, ojy, djx, djy = calcClusterFlow(cj, data)

    vi = [dix-oix, diy-oiy]
    vj = [djx-ojx, djy-ojy]
    dvi = math.sqrt((vi[0]**2+vi[1]**2))/rr
    dvj = math.sqrt((vj[0]**2+vj[1]**2))/rr
    rdv = math.sqrt((vi[0]-vj[0])**2+(vi[1]-vj[1])**2)
    try:
        if dvi < dvj:
            rdv /= float(dvj)
        else:
            rdv /= float(dvi)
    except Exception as e:
        print(e)

    return rdv

# 合并相似度高的类
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
    rf = open(filename, 'w', newline='')
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


if __name__ == '__main__':
    print('Running ', sys.argv[0])

    #空间聚类参数
    rr = 3.0     #相似圆半径比
    K = 3         #近邻数
    dataFile = 'sim flows.csv'
    ldataFile = 'lData_sim '+str(K)+' '+str(rr)+'.csv'
    clusterFile = 'cData_sim '+str(K)+' '+str(rr)+'.csv'

    print('file: ', dataFile)
    print('rr =', rr, '; k =', K)

    if os.path.exists(ldataFile):
        os.remove(ldataFile)

    if os.path.exists(clusterFile):
        os.remove(clusterFile)

    #----------------------------初始化------------------------------------
    data, midPnt, lst, let, w = readData(dataFile)
    dataLen = len(data)
    c = {} #类集合
    l = [] #数据标签集合
    #初始化时第i类只包括第i个数据，第i个数据的数据标签为第i类
    for i in range(dataLen):
        c[i] = [i] #类编号(整数编号)，包含的流编号
        l.append(i)        #流的类标签


    #----------------------------空间聚类----------------------------------
    for i in range(dataLen):
        knn = KNN(i, K, midPnt)
        #print knn
        for j in knn:
            if l[i] != l[j]: #如果第i条流和第j条流不属于同一类
                if clusterSim(c[l[i]], c[l[j]], data, rr) < 1:
                    merge(c, l[i], l[j], l)



    outputSLabeledData(ldataFile, data, l, lst, let, w)
