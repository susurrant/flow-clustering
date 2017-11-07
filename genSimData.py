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
    flows.extend(genSimData(5,(0,3),(0,3),(27,30),(27,30),(0,3),(10,13)))
    flows.extend(genSimData(5,(0,3),(0,3),(27,30),(27,30),(7,10),(17,20)))
    flows.extend(genSimData(4,(0,3),(10,13),(2,5),(21,24),(4,7),(12,15)))
    #for flow in flows:
    #    print(flow)
    draw.drawFromData(flows)