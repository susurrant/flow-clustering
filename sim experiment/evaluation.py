
import numpy as np


def distance(f, flows):
    return np.sqrt(np.sum(((f-flows)**2)[:, 1:5], axis=1))


def Silhouette_coefficient(idx, flows, size, labels):
    label = flows[idx, 8]
    bi = float('inf')
    ai = 0
    dis = distance(flows[idx], flows)
    for l in labels:
        t = np.mean(dis[np.where(flows[:, 8] == l)])
        if l != label and t < bi:
            bi = t
        elif l == label:
            ai = t
    return (bi-ai)/max(bi, ai)


def evaluate(filename):
    flows = np.loadtxt(filename, delimiter=',', skiprows=1, dtype=np.int16)
    labels = list(set(flows[:, 8]))
    size = len(flows)

    sc = 0
    for i in range(size):
        sc += Silhouette_coefficient(i, flows, size, labels)
    print(sc/size)


if __name__ == '__main__':
    evaluate('lData_sim 3 3.0.csv')
    evaluate('lData_sim 3_Zhu.csv')