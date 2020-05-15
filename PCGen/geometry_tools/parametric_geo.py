from shapely.geometry import Point, LineString, MultiLineString
from shapely.geometry.polygon import Polygon
from matplotlib import pyplot
from descartes import PolygonPatch

from geometry_tools.shapely_figures import SIZE, GREEN, GRAY, set_limits
from math import pi, sin, cos, sqrt, atan2
from numpy import arange


def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, 'o', color='#999999', zorder=1)


def plot_line(ax, ob, **kwargs):
    x, y = ob.xy
    ax.plot(x, y, **kwargs)


def plot_lines(ax, ob, **kwargs):
    for line in ob:
        # print(line)
        plot_line(ax, line, **kwargs)


def pole_angle_to_polar(angle):
    angle = pi/180*angle
    return pi/2+2*angle


def get_bounds(radius, max_offset):
    x_bound = 2*radius
    y_max, y_min = 2*radius, -(max_offset+radius)
    bounding_box = Polygon(
        [(-x_bound, y_min), (x_bound, y_min), (x_bound, y_max), (-x_bound, y_max)])
    center = (0, radius)
    bounding_circle = Point(*center).buffer(2*radius+max_offset)
    outer_bound = Point(*center).buffer(GratingEllipse.max_radius)
    interior = bounding_box.intersection(bounding_circle)
    bounding_curve = outer_bound.difference(interior)
    return bounding_curve


def bound_grating(grating_list, radius, grating_max):
    bounding_curve = get_bounds(radius, grating_max)
    for ellipse in grating_list:
        if ellipse.mask(bounding_curve):
            yield ellipse



class ParametricGeometry:

    def __init__(self, origin=None):
        self.origin = origin
        if self.origin == None:
            self.origin = Point((0.0, 0.0))
        self.u = 0
        self.v = 0
        self.curve = None

    def get_patch(self, **kwargs):
        return PolygonPatch(self.curve, **kwargs)

    def cut_curve(self, curve_obj):
        """cut_curve Removes Positive image of curve_obj from the geometry

        :param curve_obj: [description]
        :type curve_obj: ParametricGeometry
        :return: True if the curve is successfully cut, false otherwise.
        :rtype: Boolean
        """
        curve = curve_obj.curve
        if self.curve.intersects(curve.boundary):
            self.curve = self.curve.difference(curve)
            return True
        return False

    def mask(self, curve):
        if curve.contains(self.curve):
            return False
        if self.curve.intersects(curve.boundary):
            self.curve = self.curve.difference(curve)
            return True
        return True


class RowlandCircle(ParametricGeometry):

    def __init__(self, radius, origin=None):
        super().__init__(origin=origin)
        self.radius = radius
        self.v = radius
        self.curve = Point(self.u, self.v).buffer(radius)


class GratingCircle(RowlandCircle):

    def __init__(self, radius, origin=None):
        super().__init__(radius, origin=None)
        self.radius = radius*2
        self.v = self.v*2
        self.curve = Point(self.u, self.v).buffer(self.radius)


class RowlandPoint(ParametricGeometry):

    def __init__(self, angle, circle):
        super().__init__(origin=circle.origin)
        polar_angle = pole_angle_to_polar(angle)
        radius = circle.radius
        self.u = circle.u + radius*cos(polar_angle)
        self.v = circle.v + radius*sin(polar_angle)
        self.curve = Point(self.u, self.v)

    def midpoint(self, point_1):
        u0, u1 = self.u, point_1.u
        v0, v1 = self.v, point_1.v
        return ((u1+u0)/2, (v1+v0)/2)


class GratingEllipse(ParametricGeometry):
    max_radius = 0

    def __init__(self, focus_0, focus_1, offset=0, origin=None):
        super().__init__(origin)
        A, B = (focus_0.u, focus_0.v), (focus_1.u, focus_1.v)
        # x axis angle, needed for ellipse orientation
        theta = atan2(B[1]-A[1], B[0]-A[0])  
        center = focus_0.midpoint(focus_1)
        self.u, self.v = center[0], center[1]


        foci_spacing = sqrt((B[1]-A[1])**2 + (B[0]-A[0])**2)
        major_axis = foci_spacing+2*offset
        minor_axis = sqrt(major_axis**2-foci_spacing**2)
        from shapely import affinity

        # create a circle of radius 1
        curve = Point(self.u, self.v).buffer(1)
        # create the ellipse by scaling the circle along x and y:
        curve = affinity.scale(curve, major_axis, minor_axis)

        # Let rotate the ellipse (clockwise, x axis pointing right):
        self.curve = affinity.rotate(curve, theta, use_radians=True).boundary

        # resolve maximum mask size to remove extra curves
        minx, miny, maxx, maxy = self.curve.bounds
        max_dimension = sqrt(maxx**2+maxy**2)
        if max_dimension > GratingEllipse.max_radius:
            GratingEllipse.max_radius = max_dimension



if __name__ == "__main__":

    alpha, beta = -15, -45  # degree
    radius = 20
    d1, d2 = 0.6, 0.6
    grating_lower_bound = radius/20
    RC = RowlandCircle(radius)
    GC = GratingCircle(radius)
    input_point = RowlandPoint(alpha, RC)
    output_point = RowlandPoint(beta, RC)
    offsets = arange(1, radius*2, step=d2)
    grating = []
    center = (0, radius)
    #bounding_circle = Point(*center).buffer(2*radius+grating_lower_bound)

    for offset in offsets:
        GE = GratingEllipse(input_point, output_point, offset=offset)
        if not GE.cut_curve(GC):
            break
        # if bounding_circle.touches(GE.curve):
        grating.append(GE)

    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    patch = GC.get_patch(fc='#FFFFFF')
    ax.add_patch(patch)
    patch = RC.get_patch(fc='#FFFFFF')
    ax.add_patch(patch)

    BB = get_bounds(radius, grating_lower_bound)
    # plot_line(ax, BB, color='#000000')

    # patch = PolygonPatch(bounding_circle, ec='#000000', fill=False)
    # ax.add_patch(patch)

    for ellipse in bound_grating(grating, radius, grating_lower_bound):
        # print(type(ellipse.curve))
        try:
            plot_lines(ax, ellipse.curve, color='#000000')
        except:
            plot_line(ax, ellipse.curve, color='#000000')
        # patch = ellipse.get_patch(ec='#000000', fill=False)
        # ax.add_patch(patch)

    tick_count = 10
    plot_coords(ax, output_point.curve)
    plot_coords(ax, input_point.curve)
    xlim = 2*radius+1  # int(GratingEllipse.max_radius)
    xmin, xmax = -xlim, xlim
    ymin, ymax = -(radius+1), radius*4+1
    set_limits(ax, xmin, xmax, ymin, ymax)
    ax.set_xticks(arange(xmin, xmax+1, tick_count))
    ax.set_yticks(arange(ymin, ymax+1, tick_count))

    pyplot.show()
