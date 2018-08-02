# -*- coding: cp936 -*-
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def figure7a():
    sns.set(style="ticks")

    k = np.array([i for i in range(10,51,5)])
    c = [209967,194666,181877,171106,161484,152853,145283,138035,132001]
    lc = [9, 13, 20, 22, 25, 32, 49, 52, 69]

    c1 = '#44cef6'
    c2 = '#48c0a3'
    fs1 = 16
    fs2 = 14

    fig, ax1 = plt.subplots(figsize=(6,4)) #ax1为第一轴
    ax1.set_xlabel('k', fontname="Times New Roman", fontsize=fs1, fontstyle = 'italic')
    ax1.set_xlim(10, 50)
    ax1.set_xticks(k)
    xlabels = [str(item) for item in k]
    ax1.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=fs2)

    l1 = ax1.bar(k-1, lc, facecolor=c1, width = 2, label='# of large clusters')
    ax1.set_ylabel('# of large clusters', fontname="Times New Roman", fontsize=fs1)
    ax1.set_ylim(0, 75)

    y1s = [i for i in range(0, 76, 15)]
    ax1.set_yticks(y1s)
    y1labels = [str(item) for item in y1s]
    ax1.yaxis.set_ticklabels(y1labels, fontname="Times New Roman", fontsize=fs2)


    ax2 = ax1.twinx()       #ax2为第二轴
    l2, = ax2.plot(k, c, 'mo-', linewidth=2.0, color=c2, label='# of total clusters')
    ax2.set_ylabel('# of total clusters', fontname="Times New Roman", fontsize=fs1)
    y2s = [i*10000 for i in range(13, 22, 2)]
    ax2.set_yticks(y2s)
    y2labels = ['1.3e5', '1.5e5', '1.7e5', '1.9e5', '2.1e5']
    ax2.yaxis.set_ticklabels(y2labels, fontname="Times New Roman", fontsize=fs2)

    leg = plt.legend(handles=[l2,l1], loc=9)
    for l in leg.get_texts():
        l.set_fontsize(14)
        l.set_fontname("Times New Roman")

    plt.show()


def figure7b():
    sns.set(style="ticks")

    r = np.array([0.15, 0.25, 0.35, 0.45, 0.55])
    c = [206776, 171106, 133810, 96373, 63907]
    lc = [21, 22, 61, 123, 147]

    c1 = '#44cef6'
    c2 = '#48c0a3'
    fs1 = 16
    fs2 = 14

    fig, ax1 = plt.subplots(figsize=(6,4)) #ax1为第一轴
    ax1.set_xlabel(r'$\alpha$', fontname="Times New Roman", fontsize=fs1, fontstyle='italic')
    ax1.set_xlim(0.15, 0.55)
    ax1.set_xticks(r)
    xlabels = [str(item) for item in r]
    ax1.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=fs2)

    l1 = ax1.bar(r-0.02, lc, facecolor=c1, width = 0.04, label='# of large clusters')
    ax1.set_ylabel('# of large clusters', fontname="Times New Roman", fontsize=fs1)
    ax1.set_ylim(0, 150)
    y1s = [i for i in range(0, 151, 30)]
    ax1.set_yticks(y1s)
    y1labels = [str(item) for item in y1s]
    ax1.yaxis.set_ticklabels(y1labels, fontname="Times New Roman", fontsize=fs2)


    ax2 = ax1.twinx()       #ax2为第二轴
    l2, = ax2.plot(r, c, 'mo-', linewidth=2.0, color=c2, label='# of total clusters')
    ax2.set_ylabel('# of total clusters', fontname="Times New Roman", fontsize=fs1)
    y2s = [i * 10000 for i in range(6, 22, 3)]
    ax2.set_yticks(y2s)
    y2labels = ['6e4', '9e4', '1.2e5', '1.5e5', '1.8e5', '2.1e5']
    ax2.yaxis.set_ticklabels(y2labels, fontname="Times New Roman", fontsize=fs2)

    leg = plt.legend(handles=[l2,l1], loc=9)
    for l in leg.get_texts():
        l.set_fontsize(14)
        l.set_fontname("Times New Roman")

    plt.show()


def figure9():
    sns.set(style="whitegrid")
    clusterID = [318, 151]

    clen = len(clusterID)
    ts = [[0 for i in range(clen)] for j in range(24 * 60)]

    with open('./data/spatial clustering results/s_ld(May 13) 25 0.25.csv', 'r') as f:
        f.readline()
        while True:
            line = f.readline().strip()
            if line:
                sl = line.split(',')
                if int(sl[-1]) in clusterID:
                    idx = clusterID.index(int(sl[-1]))
                    for i in range(int(sl[5]), int(sl[6]) + 1):
                        ts[i][idx] += 1
            else:
                break

    # normalization
    for i in range(clen):
        maxt = ts[0][i]
        mint = ts[0][i]
        for j in range(len(ts)):
            if ts[j][i] > maxt:
                maxt = ts[j][i]
            if ts[j][i] < mint:
                mint = ts[j][i]
        mi = maxt - mint
        for j in range(len(ts)):
            ts[j][i] = (ts[j][i] - mint) / float(mi)

    x = [float(i) / 60 for i in range(0, 24 * 60, 3)]
    y = []
    for j in range(0, len(ts), 3):
        # ----------------此处控制显示。1：类151；0：类318---------------
        y.append(ts[j][1])

    fig, ax = plt.subplots()
    ax.set_xlabel('Time', fontname="Times New Roman", fontsize=16)
    ax.set_xlim(0, 24)
    ax.set_ylabel('Relative flow number', fontname="Times New Roman", fontsize=16)
    ax.set_ylim(0, 1)

    z = []
    for k in range(0, 25, 4):
        z.append(k)
    ax.set_xticks(z)
    xlabels = [str(item) for item in z]
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=14)

    z = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    ax.set_yticks(z)
    ylabels = [str(item) for item in z]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=14)

    ax.plot(x, y, '-', linewidth=1, color='#801dae')

    plt.show()


def figure10():
    sns.set_style("whitegrid")

    t = np.array([i/10.0 for i in range(0, 11)])
    c = [1, 41, 50, 61, 83, 115, 175, 281, 518, 1072, 1673]
    flc = [1724, 166, 140, 119, 94, 73, 51, 38, 20, 8, 3]

    c1 = '#44cef6'
    c2 = '#48c0a3'
    fs1 = 16
    fs2 = 14

    fig, ax = plt.subplots()
    ax.set_xlabel('t', fontname="Times New Roman", fontsize=fs1, fontstyle = 'italic')
    ax.set_ylabel('Number', fontname="Times New Roman", fontsize=fs1)

    ax.set_xlim(0, 1)
    ax.set_xticks(t)
    xlabels = [str(item) for item in t]
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=fs2)

    ax.set_ylim(0, 1800)
    ys = [i for i in range(0, 1801, 300)]
    ax.set_yticks(ys)
    ylabels = [str(item) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=fs2)

    ax.plot(t, c, 'mo-', linewidth=2.0, color=c1, label='# of clusters')
    ax.plot(t, flc, 'mo-', linewidth=2.0, color=c2, label='# of flows in the largest temporal cluster')

    leg = plt.legend(loc=9)
    for l in leg.get_texts():
        l.set_fontsize(14)
        l.set_fontname("Times New Roman")
    plt.show()


if __name__ == '__main__':
    figure10()