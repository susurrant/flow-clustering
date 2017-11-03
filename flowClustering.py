#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
'''spatio-temporal clustering of flow data'''

__author__ = 'Xin Yao'

import os
import numpy as np
import time
import sys
import serialize

class Flow(object):
    def __init__(self, fid, c, t):
        self.fid = fid
        self.c = np.array(c)
        self.t = np.array(t)

# read OD coordinates
def readData(fileName):
    data = []
    w = []
    lst = []
    let = []
    
    with open(fileName, 'rb') as f:
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

# compute the spatio-temporal similarity between flows f1 and f2
def flowSim(f1, f2, dt=0):
    if f1.t[0] - f2.t[1] >= 2*dt or f2.t[0] - f1.t[1] >= 2*dt: # no overlap, even extended with dt
        return 0

    t = sorted([*f1.t, *f2.t])
    if np.prod(f1.t[0] - f2.t) <= 0 or np.prod(f2.t[0] - f1.t) <= 0: # overlap
        t[1:3] = max(t[1] - dt, t[0]), min(t[2] + dt, t[3])
    else:                                                            # overlap when extended with dt
        t[1:3] = (t[1] + t[2]) / 2 - dt, (t[1] + t[2]) / 2 + dt

    r1 = (np.array([max(t[1], f1.t[0]), min(t[2], f1.t[1])]) - f1.t[0]) / (f1.t[1] - f1.t[0])
    r2 = (np.array([max(t[1], f2.t[0]), min(t[2], f2.t[1])]) - f2.t[0]) / (f2.t[1] - f2.t[0])
    c1 = r1[:, np.newaxis] * (f1.c[1] - f1.c[0]) + f1.c[0]
    c2 = r2[:, np.newaxis] * (f2.c[1] - f2.c[0]) + f2.c[0]

    return (t[2]-t[1])/(t[3]-t[0])*np.exp(-0.5*np.sqrt(np.sum((c2-c1)**2)/(np.sum((c1[1]-c1[0])**2)*np.sum((c2[1]-c2[0])**2))))


# compute the similarity between clusters c1 and c2
def clusterSim(ci, cj, data, alpha):
    oix, oiy, dix, diy = calcClusterFlow(ci, data)
    ojx, ojy, djx, djy = calcClusterFlow(cj, data)

    vi = [dix-oix, diy-oiy]
    vj = [djx-ojx, djy-ojy]
    return flowSim(vi, vj, alpha)

# merge similar clusters
def merge(c, ci, cj, l):
    #保留小数字的clusterID
    if ci > cj:
        ci, cj = cj, ci
        
    for lid in c[cj]:
        l[lid] = ci
        c[ci].append(lid)
    c.pop(cj)
    

# output clustering result - clustered flows
def outputSLabeledData(filename, data, l, lst, let, w):
    flows = []
    for i in range(len(data)):
        r = [i]
        r.extend(data[i])
        r.append(lst[i])
        r.append(let[i])
        r.append(w[i])
        r.append(l[i])
        flows.append(r)
    serialize.serialize(flows, filename, header = ['id','x1','y1','x2','y2','st','et','w','cluster'] )


#输出空间类数据，包括clusterID，类中心流坐标，包含的流的个数
def outputSClusterData(filename, data, c):
    clusters = []
    for i in c.keys():
        if len(c[i]) > 0:
            ox, oy, dx, dy = calcClusterFlow(c[i], data)
            clusters.append([i, ox, oy, dx, dy, len(c[i])])
    serialize.serialize(clusters, filename, header=['clusterID','ox','oy','dx','dy','st','et','w'])

if __name__ == '__main__':
    print('Running ', sys.argv[0])

    #空间聚类参数  
    dt = 0
    simTh = 0.7
    dataFile = './data/f_td_0513_processed.csv'
    ldataFile = './data/lf_0513_'+str(dt)+'_'+str(simTh)+'.csv'
    clusterFile = './data/c_0513_'+str(dt)+'_'+str(simTh)+'.csv'

    print('file: ', dataFile)
    print('dt =', dt, '; sim threshold =', simTh)

    startTime = time.clock()
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
            print i, '%.2f' % ((et-st)/60.0), 'mins'
            st = et

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
