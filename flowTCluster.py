# -*- coding: utf-8 -*-
import csv
import sys
import time
import os


#读取带空间聚类标签的数据
def readSLData(fileName, clusterID):
    flows = []
    with open(fileName,'r') as f:
        f.readline()
        while True:
            line = f.readline().strip()
            if line:
                sl = line.split(',')
                if int(sl[-1]) == clusterID:
                    flows.append(sl)
            else:
                break
            
    return flows

#计算类的CTS
def calCTS(ck, flows):
    st = 0
    et = 0
    for j in ck:
        st += float(flows[j][5])
        et += float(flows[j][6])
    d = float(len(ck))

    st /= d
    et /= d
    return int(round(st)), int(round(et))

#计算类的时间相似度
def tsim(ci, cj, flows):
    st1, et1 = calCTS(ci, flows)
    st2, et2 = calCTS(cj, flows)

    s1 = set([i for i in range(st1, et1)])
    s2 = set([i for i in range(st2, et2)])
    a = len(s1 & s2)
    b = len(s1 | s2)
    similarity = float(a) / b
    return similarity

#合并类  
def merge(c, ci, cj, l):
    if ci > cj:
        ci, cj = cj, ci

    for lid in c[cj]:
        l[lid] = ci
        c[ci].append(lid)
    c.pop(cj)

#输出带类标签的OD数据到csv格式文件
def outputTLabeledData(fileName, flows, l):
    with open(fileName, 'w', newline='') as rf:
        sheet = csv.writer(rf)
        sheet.writerow(['id','x1','y1','x2','y2','st','et','w','s_cluster', 't_cluster'])
        for i in range(len(flows)):
            f = flows[i]
            f.append(l[i])
            sheet.writerow(f)


#输出时间类数据，包括clusterID，起止时间，包含的流的个数
def outputTClusterData(fileName, flows, c):
    with open(fileName, 'w', newline='') as rf:
        sheet = csv.writer(rf)
        sheet.writerow(['t_clusterID','st', 'et', 'flowNum'])
        for i in c.keys():
            if len(c[i]) > 0:
                st, et = calCTS(c[i], flows)
                sheet.writerow([i, st, et, len(c[i])])


def temporalClustering(ldataFile, clusterID, thredshold, output = 'True'):
    startTime = time.clock()
    print('labeled data file: ', ldataFile)
    print('cluster ID =', clusterID, '; thredshold =', thredshold)

    flows = readSLData('.\\spatial clustering results\\' + ldataFile, clusterID)
    c = {}  # 类集合
    l = []  # 数据标签集合
    nflows = len(flows)

    # 初始化时第i类只包括第i个数据，第i个数据的数据标签为第i类
    for i in range(nflows):
        c[i] = [i]  # 类编号(整数编号)，包含的流编号，基于flows
        l.append(i)  # 流的类标签

    for i in range(nflows - 1):
        for j in range(i + 1, nflows):
            if l[i] == l[j]:
                continue

            if tsim(c[l[i]], c[l[j]], flows) >= thredshold:
                merge(c, l[i], l[j], l)

    if output:
        stdataFile = 'st_ld' + ldataFile[4:-4] + ' c' + str(clusterID) + ' ' + str(thredshold) + '.csv'
        stclusterFile = 'st_c' + ldataFile[4:-4] + ' c' + str(clusterID) + ' ' + str(thredshold) + '.csv'

        if os.path.exists(stdataFile):
            os.remove(stdataFile)
        if os.path.exists(stclusterFile):
            os.remove(stclusterFile)

        outputTLabeledData(stdataFile, flows, l)
        outputTClusterData(stclusterFile, flows, c)

    print('Total running time: %.2f' % (time.clock() - startTime), 'seconds')
    print('--------------------------')

if __name__ == '__main__':
    print('Running ', sys.argv[0])

    ldataFile = 's_ld(May 13) 25 0.25.csv'
    thredshold = 0.5
    clusterID = 318

    temporalClustering(ldataFile, clusterID, thredshold)
