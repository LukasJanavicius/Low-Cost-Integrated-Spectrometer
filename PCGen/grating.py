
import geometry_tools.parametric_geo as pg
from geometry_tools import plotting
from matplotlib import pyplot
import itertools as it
from math import pi, sin, cos, sqrt, atan2, radians

from numpy import arange, linspace
"""  Equations from
Mono-Order High-Efficiency Dielectric Concave Diffraction Grating by Pierre Pottier and Muthukumaran Packirisamy
"""


grating_parameters = {
    "n": 1.5,  # substrate index (PMMA or SiO2)
    "n2": 1,  # negative space index (air in this case)
    "blaze_wavelength": 600,  # nm
    "M": -2,     # target mode number
    "alpha": -15,  # degrees
    "beta": -45,   # degrees
    'radius': 10,
    "grating_thickness": 3

}


def get_grating_dims(n, n2, blaze_wavelength, M, alpha, beta, **kwargs):
    alpha_r, beta_r = sin(radians(alpha)), sin(radians(beta))
    a = (M * blaze_wavelength)/(n * (alpha_r + beta_r))
    d = -a*sin((alpha_r+beta_r)/2)
    return d


def create_reference_geometry(radius, alpha, beta):
    RC = pg.RowlandCircle(radius)
    GC = pg.GratingCircle(radius)
    input_point = pg.RowlandPoint(alpha, RC)
    output_point = pg.RowlandPoint(beta, RC)
    return RC, GC, input_point, output_point


def create_ellipsis(d, A, B, grating_circle):
    counter = it.count(0, d)
    first_ellipse = True
    while True:
        offset = next(counter)
        GE = pg.GratingEllipse(A, B, offset=offset)
        intersects_grating = GE.cut_curve(grating_circle)
        #print(offset, intersects_grating)
        if (intersects_grating and first_ellipse):
            first_ellipse = False
        elif not (first_ellipse or intersects_grating):
            break
        if intersects_grating:
            yield GE


def format_plt_window(ax, radius, grating_thickness, tick_count):
    xlim = 2*radius+1  # int(GratingEllipse.max_radius)
    xmin, xmax = -xlim, xlim
    ymin, ymax = -(radius+grating_thickness+1), radius*4+1
    plotting.set_limits(ax, xmin, xmax, ymin, ymax)
    ax.set_xticks(arange(xmin, xmax+1, tick_count))
    ax.set_yticks(arange(ymin, ymax+1, tick_count))


def create_varied_param_plot(axs, param_name, param_start, param_stop, xcount=1, ycount=1, title_lambda=None):
    plot = plotting.plot_geometries
    tick_count, plt_count = 10, xcount*ycount
    local_params = {}
    local_params.update(grating_parameters)
    param_range = linspace(param_start, param_stop, plt_count)
    print(param_range)
    x_plt_range = [x for x in range(0, xcount)]
    y_plt_range = [x for x in range(0, ycount)]
    yx_idxs = it.product(x_plt_range, y_plt_range)
    only_x, only_y = True if ycount == 1 else False, True if ycount == 1 else False
    print(param_name, ',', 'd (nm)')
    for plt_num in range(0, plt_count):
        x_idx, y_idx = next(yx_idxs)

        local_params[param_name] = param_range[plt_num]
        radius, grating_thickness = local_params["radius"], local_params["grating_thickness"]
        d = get_grating_dims(**local_params)
        print(param_range[plt_num], ',', round(d,3))
        RC, GC, input_point, output_point = create_reference_geometry(
            radius, local_params["alpha"], local_params["beta"])
        if only_x:
            ax = axs[x_idx]
        elif only_y:
            ax = axs[y_idx]
        else:
            ax = axs[x_idx, y_idx]
        plot(ax, GC.curve, fill=False, ec=plotting.DARKGRAY, linestyle = '--', label = "Grating Circle")
        plot(ax, RC.curve, fill=False, ec=plotting.DARKGRAY,
             linestyle='-.', label="Rowland Circle")
        plot(ax, input_point.curve, color=plotting.BLUE, zorder=1, label = "Input Point")
        plot(ax, output_point.curve, color=plotting.RED,
             zorder=1, label="Output Center Point")
        grating = [x for x in create_ellipsis(
            d/1e3, input_point, output_point, GC)]
        for ellipse in pg.bound_grating(grating, radius, grating_thickness):
            plot(ax, ellipse.curve, color=plotting.BLACK)
        if title_lambda != None:
            ax.set_title(title_lambda(local_params[param_name]))
        format_plt_window(ax, radius, grating_thickness, tick_count)
    print('\n')

if __name__ == "__main__":
    # Vary M
    """ nrows, ncols = 2, 2
    fig, axs = pyplot.subplots(nrows, ncols, sharex='all', sharey='all')
    title_lambda = lambda x: "Mode Number M={}".format(int(x))
    create_varied_param_plot(
        axs, "M", -4, -1, xcount=nrows, ycount=ncols, title_lambda=title_lambda)
    
    handles, labels = axs[0, 0].get_legend_handles_labels()

    fig.legend(handles, labels, loc="lower right")
    fig.suptitle(r"Grating Configurations with Varying $M$", fontsize=16)
    fig.tight_layout()
    pyplot.show()

    #vary alpha
    nrows, ncols = 2, 3
    fig, axs = pyplot.subplots(nrows, ncols, sharex='all', sharey='all')
    def title_lambda(x): return "{}={}$^\circ$".format(r'$\alpha$', x)
    create_varied_param_plot(
        axs, "alpha", -5, -40, xcount=nrows, ycount=ncols, title_lambda=title_lambda)
    
    handles, labels = axs[0, 0].get_legend_handles_labels()

    fig.legend(handles, labels, loc = "lower right")
    fig.suptitle(r"Grating Configurations with Varying $\alpha$", fontsize=16)
    fig.tight_layout()
    pyplot.show()"""
    

    nrows, ncols = 2, 2
    fig, axs = pyplot.subplots(nrows, ncols, sharex='all', sharey='all')
    def title_lambda(x): return "{}={}".format(r'$R_{RC}$', x)
    create_varied_param_plot(
        axs, "radius", 2.5, 10, xcount=nrows, ycount=ncols, title_lambda=title_lambda)
    
    handles, labels = axs[0, 0].get_legend_handles_labels()

    fig.legend(handles, labels, loc="lower right")
    fig.suptitle(r"Grating Configurations with Varying $R_{RC}$", fontsize=16)
    fig.tight_layout()
    pyplot.show()
    

    """

    create_varied_param_plot(
        axs, "alpha", -40, -10, xcount=nrows, ycount=ncols)

    plot = plotting.plot_geometries
    radius = 10
    grating_thickness = 5
    tick_count = 10

    d = get_grating_dims(**grating_parameters)
    RC, GC, input_point, output_point = create_reference_geometry(
        radius, grating_parameters["alpha"], grating_parameters["beta"])

    fig = pyplot.figure()
    ax = fig.add_subplot(111)
    plot(ax, RC.curve, fill=False, ec=plotting.GRAY)
    plot(ax, GC.curve, fill=False, ec=plotting.DARKGRAY)
    plot(ax, input_point.curve, color=plotting.BLUE, zorder=1)
    plot(ax, output_point.curve, color=plotting.RED, zorder=1)
    grating = [x for x in create_ellipsis(
        d/1e3, input_point, output_point, GC)]
    # print(grating)
    for ellipse in pg.bound_grating(grating, radius, grating_thickness):
        plot(ax, ellipse.curve, color=plotting.BLACK)

    format_plt_window(ax, radius, grating_thickness, tick_count)
    pyplot.show()
    """
    # print(d)
