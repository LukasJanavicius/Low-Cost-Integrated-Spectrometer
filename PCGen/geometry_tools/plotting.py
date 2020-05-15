from shapely.geometry import Point, LineString, MultiLineString
from shapely.geometry.polygon import Polygon
from descartes import PolygonPatch

BLUE = '#6699cc'
GRAY = '#999999'
DARKGRAY = '#333333'
YELLOW = '#ffcc33'
GREEN = '#339933'
RED = '#ff3333'
BLACK = '#000000'


def set_limits(ax, x0, xN, y0, yN):
    ax.set_xlim(x0, xN)
    ax.set_xticks(range(int(round(x0)), int(round(xN))+1))
    ax.set_ylim(y0, yN)
    ax.set_yticks(range(int(round(y0)), int(round(yN))+1))
    ax.set_aspect("equal")


def plot_coords(ax, ob, **kwargs):
    x, y = ob.xy
    ax.plot(x, y, 'o', **kwargs)


def plot_line(ax, ob, **kwargs):
    x, y = ob.xy
    ax.plot(x, y, **kwargs)


def plot_lines(ax, ob, **kwargs):
    for line in ob:
        # print(line)
        plot_line(ax, line, **kwargs)


def plot_poly(ax, ob, **kwargs):
    patch = PolygonPatch(ob, **kwargs)
    ax.add_patch(patch)

plot_dispatch = {
    Point: plot_coords,
    LineString: plot_line,
    MultiLineString: plot_lines,
    Polygon: plot_poly
}

def plot_geometries(ax, ob, **kwargs):
    if type(ob) in plot_dispatch:
        #print(plot_dispatch[type(ob)])
        plot_dispatch[type(ob)](ax, ob, **kwargs)
    else:
        print("failed to plot {}".format(type(ob)))
