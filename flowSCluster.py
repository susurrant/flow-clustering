# -*- coding: utf-8 -*-

import os
import math
import csv
import psycopg2
import time
import sys


#读取OD点坐标
def readData(fileName):
    data = []
    w = []
    lst = []
    let = []
    
    with open(fileName, 'r') as f:
        while True:
            line = f.readline()
            if line:
                sl = line.split(',')
                if len(sl) > 1:
                    d = [float(sl[1]),float(sl[2]),float(sl[3]),float(sl[4])]
                    data.append(d)
                    lst.append(int(sl[5]))
                    let.append(int(sl[6]))
                    w.append(int(sl[-1]))
            else:
                break

    return data, lst, let, w

#计算第i个数据中点的k个近邻点,返回近邻点序号列表
def KNN(i, k):
    conn = psycopg2.connect(database="flow clustering", user="postgres", password="123", host='localhost', port="5432")
    cur = conn.cursor()

    cur.execute('select tgid, midpnt <-> (select midpnt from taxi_odt where tgid = '+str(i)+') dist from taxi_odt order by dist limit '+str(k+1)+';')
    results = cur.fetchall()
    n = []
    for row in results:
        if row[0] != i:
            n.append(row[0])
    
    conn.commit()
    cur.close()
    conn.close()
    return n

#计算cluster的中心流坐标
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

def flowSim(vi, vj, alpha):
    leni = math.sqrt((vi[0]**2+vi[1]**2))
    lenj = math.sqrt((vj[0]**2+vj[1]**2))
    dv = math.sqrt((vi[0] - vj[0]) ** 2 + (vi[1] - vj[1]) ** 2)
    if leni > lenj:
        return dv/(alpha*leni)
    else:
        return dv/(alpha*lenj)

#计算clusterID为ci和cj的两个类的相似性
def clusterSim(ci, cj, data, alpha):
    oix, oiy, dix, diy = calcClusterFlow(ci, data)
    ojx, ojy, djx, djy = calcClusterFlow(cj, data)

    vi = [dix-oix, diy-oiy]
    vj = [djx-ojx, djy-ojy]
    return flowSim(vi, vj, alpha)

#合并相似度高的类
def merge(c, ci, cj, l):
    #保留小数字的clusterID
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


#输出空间类数据，包括clusterID，类中心流坐标，包含的流的个数
def outputSClusterData(filename, data, c):
    rf = open(filename, 'w', newline='')
    sheet = csv.writer(rf)
    sheet.writerow(['clusterID','ox','oy','dx','dy','flownum'])
    for i in c.keys():
        if len(c[i]) > 0:
            ox, oy, dx, dy = calcClusterFlow(c[i], data)
            sheet.writerow([i, ox, oy, dx, dy, len(c[i])])
    rf.close()


if __name__ == '__main__':
    print('Running ', sys.argv[0])
    startTime = time.clock()

    #空间聚类参数  
    alpha = 0.55     # 边界圆尺度系数
    K = 25           # 近邻数
    dataFile = 'taxi data(May 13)_processed.csv'
    ldataFile = 's_ld(May 13) '+str(K)+' '+str(alpha)+'.csv'
    clusterFile = 's_c(May 13) '+str(K)+' '+str(alpha)+'.csv'

    print('file: ', dataFile)
    print('alpha =', alpha, '; k =', K)

    #----------------------------初始化------------------------------------
    print('\ninitialize...')
    data, lst, let, w = readData(dataFile)
    dataLen = len(data)
    c = {} #类集合
    l = [] #数据标签集合


    #----------------------------空间聚类----------------------------------
    # 初始化时第i类只包括第i个数据，第i个数据的数据标签为第i类
    for i in range(dataLen):
        c[i] = [i]  # 类编号(整数编号)，包含的流编号
        l.append(i)  # 流的类标签

    print('start clustering...')
    st = time.clock()
    for i in range(dataLen):
        if i%5000 == 0:
            et = time.clock()
            print(i, '%.2f' % ((et-st)/60.0), 'mins')
            st = et
        
        knn = KNN(i, K) #计算k近邻点

        for j in knn:
            if l[i] != l[j]: #如果第i条流和第j条流不属于同一类
                if not (clusterSim(c[l[i]], c[l[j]], data, alpha) > 1):
                    merge(c, l[i], l[j], l)
              
    if os.path.exists(ldataFile):
        os.remove(ldataFile)
    if os.path.exists(clusterFile):
        os.remove(clusterFile)
		
    outputSLabeledData(ldataFile, data, l, lst, let, w)
    outputSClusterData(clusterFile, data, c)

    endTime = time.clock()
    print('Total running time: %.2f' % ((endTime-startTime)/3600.0), 'hours')
