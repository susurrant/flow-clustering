# -*- coding: utf-8 -*-
import csv
import sys
import os


def readSimData(filename):
    flows = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        del lines[0]
        for line in lines:
            sl = line.strip().split(',')
            if sl[-2] == '-1':
                continue
            flows.append(list(map(int, sl)))

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

    if et1 <= st2 or et2 <= st1:
        return 0

    return min(et1-st2, et1-st1, et2-st1, et2-st2)/max(et1-st2, et1-st1, et2-st2, et2-st1)

#合并类
def merge(c, ci, cj, l):
    if ci > cj:
        ci, cj = cj, ci

    for lid in c[cj]:
        l[lid] = ci
        c[ci].append(lid)
    c.pop(cj)


def outputTLabeledData(fileName, flows, l):
    with open(fileName, 'w', newline='') as rf:
        sheet = csv.writer(rf)
        sheet.writerow(['id','x1','y1','x2','y2','st','et','w','t_cluster'])
        for i in range(len(flows)):
            f = flows[i]
            f.append(l[i])
            sheet.writerow(f)


if __name__ == '__main__':
    flows = readSimData('sim flows.csv')
    threshold = 0.6

    c = {}  # 类集合
    l = []  # 流的类标签
    nflows = len(flows)

    # 初始化
    for i in range(nflows):
        c[i] = [i]
        l.append(i)

    for i in range(nflows - 1):
        for j in range(i + 1, nflows):
            if l[i] == l[j]:
                continue

            if tsim(c[l[i]], c[l[j]], flows) >= threshold:
                merge(c, l[i], l[j], l)

    outputTLabeledData('stl_flows_t'+str(threshold)+'.csv', flows, l)