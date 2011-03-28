import wx
import numpy as np

# Chaco imports
from enthought.enable.wx_backend.api import Window
#from enthought.enable.wx.image import Window
from enthought.chaco.api import ArrayPlotData, Plot, OverlayPlotContainer
from enthought.chaco.api import PlotLabel, Legend
from enthought.chaco.api import add_default_grids, add_default_axes
from enthought.chaco.api import create_line_plot, create_scatter_plot
from enthought.chaco.tools.api import PanTool, ZoomTool, LegendTool
from enthought.chaco.tools.api import TraitsTool, DragZoom

from circuit import SignalClient


class Trace(SignalClient):
    """Class representing a single trace in a PlotView"""
    def __init__(self, signal, plot, color, sweep_point):
        SignalClient.__init__(self)
        self.signal = signal
        self.signal.add_client(self)
        self.sweep_point = sweep_point
        self._plot = plot
        self._group = None  # trace is part of a group? (sweeps)

        sweep_set = sweep_point._sweep_set
        if len(sweep_set._points) > 1:
            suffix = " ["
            for i, name in enumerate(sweep_set._names):
                suffix += "%s=%g" % (name, sweep_point[i]) + ", "
            suffix = suffix[:-2] + "]"
        else:
            suffix = ""

        prefix = "[%d] " % signal.get_circuit().get_data_source().number
        self.label = prefix + signal.full_name + suffix
        self.index_label = signal.get_independent_signal().full_name + suffix

        self.color = color
        self.line_style = 'solid'
        self.line_width = 1
        self.marker = 'circle'
        self.marker_size = 10
        self.marker_color = color

    def update_signal(self, signal):
        print "update_signal:", signal

    def set_label(self, label):
        self.label = label

    def get_indices(self):
        return self.signal.get_independent_signal().get_values(self.sweep_point)
        
    def get_values(self):
        return self.signal.get_values(self.sweep_point)
    
    def destroy(self):
        self.signal.remove_client(self)


class TraceGroup(list):
    """Class representing a set of Traces (sweeped, for example)"""
    def __init__(self, *args, **kwargs):
        self.traces = []
        
    def rainbow(self):
        # colour traces in this group as rainbow
        pass


class PlotView(wx.Panel):
    def __init__(self, parent, id=-1, **kwargs):
        wx.Panel.__init__(self, parent, id=id, **kwargs)
        self.statusBar = self.GetTopLevelParent().statusBar

        self.container = OverlayPlotContainer(padding = 50, fill_padding = True,
            bgcolor = "lightgray", use_backbuffer=True)
        self.legend = Legend(component=self.container, padding=10, align="ur")
        #self.legend.tools.append(LegendTool(self.legend, drag_button="right"))
        self.container.overlays.append(self.legend)

        self.plot_window = Window(self, component=self.container)

        self.container.tools.append(TraitsTool(self.container))

        self.firstplot = True
        self._palette = ['red', 'blue', 'green', 'purple', 'yellow']
        self._current_palette_index = 0

        self._traces = []

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def _next_color(self):
        if self._current_palette_index == len(self._palette):
            self._current_palette_index = 0
        self._current_palette_index += 1
        return self._palette[self._current_palette_index - 1]

    def add_plot(self, signal, sweep_point=None):
##        waveform = signal.get_waveform()
##        x = waveform.get_x()[-1][0].tolist()
##        y = np.real(waveform.get_y()[0].tolist())

        if sweep_point is None:
            sweep_point = signal.get_circuit()._sweep_set._points[0]

        trace = Trace(signal, self, self._next_color(), sweep_point)

        x_name = trace.index_label
        y_name = trace.label

        x = trace.get_indices()
        y = trace.get_values()
        if type(y[0]) == complex:
            y = [value.real for value in y]
        #print x_name, len(x)
        #print y_name, len(y)
        #print x
        #print y

        if self.firstplot:
            self.plotdata = ArrayPlotData()
            self.plotdata.set_data(x_name, x)
            self.plotdata.set_data(y_name, y)

            plot = Plot(self.plotdata)
            plot.padding = 1

            plot.bgcolor = "white"
            plot.border_visible = True
            add_default_grids(plot)
            add_default_axes(plot)

            plot.tools.append(PanTool(plot))

            # The ZoomTool tool is stateful and allows drawing a zoom
            # box to select a zoom region.
            zoom = CustomZoomTool(plot)
            plot.overlays.append(zoom)

            # The DragZoom tool just zooms in and out as the user drags
            # the mouse vertically.
            dragzoom = DragZoom(plot, drag_button="right")
            plot.tools.append(dragzoom)

            #~ # Add a legend in the upper right corner, and make it relocatable
            #~ self.legend = Legend(component=plot, padding=10, align="ur")
            #~ self.legend.tools.append(LegendTool(self.legend, drag_button="right"))
            #~ plot.overlays.append(self.legend)

            #~ self.legend.plots = {}

            self.firstplot = False

            self.container.add(plot)

            self.plot = plot

        else:
            self.plotdata.set_data(x_name, x)
            self.plotdata.set_data(y_name, y)

        #self.plot.plot(self.plotdata.list_data())
        pl = self.plot.plot( (x_name, y_name), name=trace.label, type="line",
            color=trace.color, line_style=trace.line_style,
            line_width=trace.line_width, marker=trace.marker,
            marker_size=trace.marker_size, marker_color=trace.marker_color)

        self.legend.plots[trace.label] = pl

        self.Refresh()


    #~ def ChangeCursor(self, event):
        #~ self.canvas.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))

    #~ def UpdateStatusBar(self, event):
        #~ if event.inaxes:
            #~ x, y = event.xdata, event.ydata
            #~ self.statusBar.SetStatusText(( "x= " + str(x) +
                                           #~ "  y=" + str(y) ),
                                           #~ 0)

class CustomZoomTool(ZoomTool):
    def __init__(self, component=None):
        ZoomTool.__init__(self, component, tool_mode="range", always_on=True,
            drag_button='right')

    def normal_right_down(self, event):
        self._original_x = event.x
        self._original_y = event.y
        return ZoomTool.normal_right_down(self, event)

    def selecting_mouse_move(self, event):
        if abs(event.x - self._original_x) > abs(event.y - self._original_y):
            self.axis = 'index'
        else:
            self.axis = 'value'
        return ZoomTool.selecting_mouse_move(self, event)
