# -*- coding: utf-8 -*-：
"""
This program is unfinished
"""



import os
import numpy as np
import sys


# 读取OD点坐标
def readData(fileName):
    data = []

    with open(fileName, 'r') as f:
        f.readline()
        while True:
            line = f.readline()
            if line:
                sl = line.split(',')
                if len(sl) > 1:
                    d = [float(sl[1]), float(sl[2]), float(sl[3]), float(sl[4])]
                    data.append(d)
            else:
                break

    return data


# 计算流不相似度
def flowDissim(flow_i, flow_j):
    oix, oiy, dix, diy = flow_i[0], flow_i[1], flow_i[2], flow_i[3]
    ojx, ojy, djx, djy = flow_j[0], flow_j[1], flow_j[2], flow_j[3]

    vi = [dix - oix, diy - oiy]
    vj = [djx - ojx, djy - ojy]

    return np.sqrt(((ojx-oix)**2+(ojy-oiy)**2+(djx-dix)**2+(djy-diy)**2)/(np.sqrt(vi[0]**2+vi[1]**2)*np.sqrt(vj[0]**2+vj[1]**2)))


def buildingMST(MReachD, FD):
    pass





if __name__ == '__main__':
    print('Running ', sys.argv[0])

    K = 3  # 近邻数
    dataFile = 'sim flows.csv'
    ldataFile = 'lData_sim_' + str(K) + '_Tao.csv'
    clusterFile = 'cData_sim_' + str(K) + '_Tao.csv'

    print('file: ', dataFile)

    if os.path.exists(ldataFile):
        os.remove(ldataFile)

    if os.path.exists(clusterFile):
        os.remove(clusterFile)

    data = readData(dataFile)
    dataLen = len(data)
    FD = np.zeros((dataLen, dataLen), dtype=np.float)
    CoreD = [0] * dataLen
    MReachD = np.zeros((dataLen, dataLen), dtype=np.float)

    for i in range(dataLen):
        FD[i, i] = 0
        for j in range(i+1, dataLen):
            FD[i, j] = FD[j, i] = flowDissim(data[i], data[j])

    for i in range(dataLen):
        CoreD = np.sort(FD[i])[K-1]

    for i in range(dataLen):
        for j in range(i+1, dataLen):
            MReachD[i, j] = MReachD[j ,i] = max(CoreD[i], CoreD[j], FD[i, j])

