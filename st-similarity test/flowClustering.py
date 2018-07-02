#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
'''spatio-temporal clustering of flow data'''

__author__ = 'Xin Yao'

import numpy as np
import time
import sys
import serialize
from LL2UTM import LL2UTM_USGS

class Flow(object):
    def __init__(self, fid, c, t, w=1):
        self.fid = fid
        self.c = np.array(c)
        self.t = np.array(t)
        self.w = w

# read OD coordinates
def readData(fileName, co2xy = True):
    flows = []
    
    with open(fileName, 'r') as f:
        f.readline()
        if co2xy:
            while True:
                line = f.readline().strip()
                if line:
                    sl = line.split(',')
                    ox, oy = LL2UTM_USGS(float(sl[2]), float(sl[1]))
                    dx, dy = LL2UTM_USGS(float(sl[4]), float(sl[3]))
                    flows.append(Flow(int(sl[0]), [(ox,oy),(dx,dy)], [float(sl[5]), float(sl[6])]))
                else:
                    break
        else:
            while True:
                line = f.readline().strip()
                if line:
                    sl = line.split(',')
                    ox, oy = float(sl[1]), float(sl[2])
                    dx, dy = float(sl[3]), float(sl[4])
                    flows.append(Flow(int(sl[0]), [(ox, oy), (dx, dy)], [float(sl[5]), float(sl[6])]))
                else:
                    break

    return flows

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

    w = (t[2] - t[1]) / (t[3] - t[0])
    return w * np.exp(-0.5 * np.sqrt(
        np.sum((c2 - c1) ** 2) / (np.sqrt(np.sum((c1[1] - c1[0]) ** 2)) * np.sqrt(np.sum((c2[1] - c2[0]) ** 2)))))

# compute the similarity matrix. simMatrix[i, i] is 1 and not reserved
def calcSimMt(dataFile, dt, co2xy=True):
    flows = readData(dataFile, co2xy)
    print(flowSim(flows[13], flows[14]))

    fnum = len(flows)
    simMatrix = np.zeros((fnum, fnum))
    for i in range(fnum):
        for j in range(i+1, fnum):
            simMatrix[i, j] = simMatrix[j, i] = flowSim(flows[i], flows[j], dt)

    return simMatrix, fnum

# compute the similarity between clusters c1 and c2
def clusterSim(ci, cj, simMatrix):
    y, x = np.meshgrid(list(ci), list(cj))
    return np.sum(simMatrix[y, x]) / y.size

# merge similar clusters, and keep the smaller cluster ID
def merge(clusters, ci, cj, labels):
    if ci > cj:
        ci, cj = cj, ci

    labels[np.where(labels==cj)] = ci
    clusters[ci].update(clusters[cj])
    clusters.pop(cj)

# calculate the mean flow of a cluster
def calcClusterFlow(clusterFlowSet, flows):
    c = np.array([[0,0], [0,0]], dtype=np.float)
    t = np.array([0, 0], dtype=np.float)
    for fidx in clusterFlowSet:
        c += flows[fidx].c
        t += flows[fidx].t
    flowNum = len(clusterFlowSet)

    return [*((c/flowNum)[0]), *((c/flowNum)[1]), *(t/flowNum), flowNum]

# output clustering result - clusters and labeled flows
def outputResults(clusterFile, ldataFile, dataFile, clusters, l, co2xy):
    flows = readData(dataFile, co2xy)
    data = []
    for cid in clusters:
        if len(clusters[cid]) > 0:
            d = calcClusterFlow(clusters[cid], flows)
            d.insert(0, cid)
            data.append(d)
    serialize.serialize(data, clusterFile, header=['cid', 'ox', 'oy', 'dx', 'dy', 'st', 'et', 'w'])

    data = []
    for i, flow in enumerate(flows):

        data.append([flow.fid, *flow.c.flatten(), *flow.t.flatten(), l[i]])
    serialize.serialize(data, ldataFile, header = ['fid','x1','y1','x2','y2','st','et', 'cluster'] )

# get row-column pairs, when the corresponding flow sim >= simTh
def getIdx(simMatrix, simTh):
    rIdx, cIdx = np.where(simMatrix >= simTh)
    dIdx = np.where(rIdx > cIdx)
    rIdx, cIdx = np.delete(rIdx, dIdx), np.delete(cIdx, dIdx)
    order = np.argsort(simMatrix[rIdx, cIdx].flatten())[::-1]

    return rIdx[order], cIdx[order]

# clustering function
def clustering(dataFile, dt, simTh, co2xy):
    startTime = time.clock()
    simMatrix, flowNum = calcSimMt(dataFile, dt, co2xy)
    print('  Time for computing sim matrix: %.2f mins' % ((time.clock()-startTime)/60.0))

    clusters = {i: {i} for i in range(flowNum)}       # cluster set
    labels = np.arange(flowNum)                       # label list of flows

    st = time.clock()
    count = 0
    for i, j in zip(*getIdx(simMatrix, simTh)):
        # show time costs
        if count % 2000 == 0:
            print('  %d: %.2f mins' % (count, (time.clock()-st)/60.0))
            st = time.clock()
        count += 1

        # if flow_i and flows_j belong to different clusters
        if labels[i] != labels[j]:
            if clusterSim(clusters[labels[i]], clusters[labels[j]], simMatrix) >= simTh:
                merge(clusters, labels[i], labels[j], labels)

    return clusters, labels

if __name__ == '__main__':
    print('Running ', sys.argv[0])

    #------------------------parameter setting---------------------------------
    print('\n----parameter setting----')
    dt = 0
    simTh = 0.7
    dataFile = './data/simdata.csv'
    print('  file: ', dataFile)
    print('  delta time =', dt)
    print('  similarity threshold =', simTh)

    #----------------------------clustering------------------------------------
    print('\n----clustering----')
    startTime = time.clock()
    clusters, labels = clustering(dataFile, dt, simTh, co2xy=False)  # True: trasform lon-lat to xy coordinates
    print('  time for clustering: %.2f mins' % ((time.clock()-startTime)/60))

    # ----------------------------output--------------------------------------
    print('\n----output results----')
    ldataFile = './data/lf_sim_' + str(dt) + '_' + str(simTh) + '.csv'
    clusterFile = './data/c_sim_' + str(dt) + '_' + str(simTh) + '.csv'
		
    #outputResults(clusterFile, ldataFile, dataFile, clusters, labels, co2xy=False)
    print('\nclustering completed.')



