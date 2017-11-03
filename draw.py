import numpy as np
from numpy import *
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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

fig = plt.figure()
ax = fig.gca(projection='3d')
a = Arrow3D([0, 5], [0,5], [0,5], mutation_scale=30, arrowstyle='-|>', color='r', linewidth='3', linestyle='dashed')
ax.add_artist(a)
ax.set_xlim(0,10)
ax.set_ylim(0,10)
ax.set_zlim(0,10)
#ax.view_init(elev=-150, azim=60)
#ax.set_axis_off()
#plt.draw()
plt.show()