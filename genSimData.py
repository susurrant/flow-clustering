#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
'''generate simulation flow data'''


import numpy as np
import draw
import serialize

fid = 0

def genSimData(num, oxRg, oyRg, dxRg, dyRg, otRg, dtRg):
    global fid
    fids = np.arange(fid, fid+num)
    fid += num
    ox = np.random.randint(*oxRg, size=num)
    oy = np.random.randint(*oyRg, size=num)
    dx = np.random.randint(*dxRg, size=num)
    dy = np.random.randint(*dyRg, size=num)
    ot = np.random.randint(*otRg, size=num)
    dt = np.random.randint(*dtRg, size=num)
    #print(fids.shape,ox.shape,dt.shape)
    return np.column_stack((fids,ox,oy,dx,dy,ot,dt))

def output(fileName, flows):
    serialize.serialize(flows, fileName, ['fid', 'ox', 'oy', 'dx', 'dy', 'ot', 'dt'])

if __name__ == '__main__':
    flows = []
    flows.extend(genSimData(5,(0,3),(0,3),(22,25),(22,25),(0,3),(20,23)))
    flows.extend(genSimData(5,(0,3),(0,3),(22,25),(22,25),(17,20),(37,43)))
    flows.extend(genSimData(3,(45,48),(45,48),(37,40),(13,16),(4,7),(12,15)))
    flows.extend(genSimData(3,(37,40),(13,16),(45,48),(45,48),(4,7),(12,15)))
    flows.extend(genSimData(4,(33,37),(42,45),(8,11),(40,43),(12,16),(46,50)))
    flows.extend(genSimData(1,(0,2),(42,45),(43,46),(3,7),(4,10),(25,30)))
    flows.extend(genSimData(1,(30,32),(1,4),(28,30),(46,49),(28,30),(38,42)))
    #for flow in flows:
    #    print(flow)
    #draw.drawFromData(flows)
    output('./data/simdata.csv', flows)