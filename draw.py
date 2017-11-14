import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

def drawFromData(flows):
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for flow in flows:
        ax.add_artist(Arrow3D([flow[1], flow[3]], [flow[2], flow[4]], [flow[5], flow[6]], mutation_scale=20, arrowstyle='-|>', color='r', linewidth='1', linestyle='solid'))
    ax.set_xlim(0,50)
    ax.set_ylim(0,50)
    ax.set_zlim(0,50)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('t')
    #ax.view_init(elev=-150, azim=60)
    #ax.set_axis_off()
    #plt.draw()
    plt.show()

def drawLabeledFlows(fileName, colors):
    flows = np.loadtxt(fileName, delimiter=',', skiprows=1)
    clusters = list(set(flows[:,-1]))
    print(clusters)
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    for flow in flows:
        print(clusters.index(flow[-1]))
        ax.add_artist(Arrow3D([flow[1], flow[3]], [flow[2], flow[4]], [flow[5], flow[6]], mutation_scale=20, arrowstyle='-|>',
                              color=colors[clusters.index(flow[-1])], linewidth='1', linestyle='solid'))
    ax.set_xlim(0,50)
    ax.set_ylim(0,50)
    ax.set_zlim(0,50)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('t')
    #ax.view_init(elev=-150, azim=60)
    #ax.set_axis_off()
    #plt.draw()
    plt.show()

if __name__ == '__main__':
    drawLabeledFlows('./data/lf_sim_0_0.7.csv', ['#f44242','#f4eb42','#42f445','#42ebf4','#6242f4','#f442ce'])