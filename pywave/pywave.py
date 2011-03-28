#!/users/micas/bmachiel/python/epd-6.1-1-rh5-x86/bin/python

import wxversion
wxversion.ensureMinimal('2.8')

import os
import re
import wx
import wx.xrc as xrc
import numpy as np

from circuit import Circuit, Subcircuit, Signal
from datasource import DataSource, DataFile
from plot import PlotView, Trace

import pywave_xrc
from pywave_xrc import xrcMainFrame, get_resources
from xh_searchctrl import SearchCtrlXmlHandler

import plugins


pywave_path = os.path.dirname(os.path.abspath(__file__))


def __init_resources():
    pywave_xrc.__res = xrc.EmptyXmlResource()
    pywave_xrc.__res.Load(os.path.join(pywave_path, 'pywave.xrc'))


pywave_xrc.__init_resources = __init_resources


class MyMainFrame(xrcMainFrame):
    def __init__(self, parent):
        # add the wxSearchCtrl XML handler
        get_resources().AddHandler(SearchCtrlXmlHandler())
        # Initialize the frame
        super(MyMainFrame, self).__init__(parent)

        images_path = os.path.join(pywave_path, 'images')

        self.image_list = wx.ImageList(16, 16)
        circuit_image = wx.Image(os.path.join(images_path, 'circuit.png'))
        subcircuit_image = wx.Image(os.path.join(images_path, 'subcircuit.png'))
        self.image_list.Add(circuit_image.ConvertToBitmap())
        self.image_list.Add(subcircuit_image.ConvertToBitmap())
        self.fileTreeCtrl.AssignImageList(self.image_list)

        self.filterSearchCtrl.ShowCancelButton(1)

        self.open_files = []
        self.data_source_counter = 1
        self.views = []
        self.statusBar = xrc.XRCCTRL(self, "statusBar")

        self.OpenNewPlotView()
        
#        data_source, item = self.open_file('tests/lcmodel.ac0')
#        if item is not None:
#            self.fileChoice.SetSelection(item)
#            self._populate_tree(data_source.get_circuit())

    def OnChoice_fileChoice(self, evt):
        self._save_tree_state()
        data_source = evt.GetClientData()
        self._populate_tree(data_source.get_circuit())

    def _populate_tree(self, circuit):
        # remove old entries
        self.fileTreeCtrl.DeleteAllItems()
        self.signalListBox.Clear()
        # fill up with new entries
        self.fileTreeCtrl.AddRoot(circuit.name, image=0, data=wx.TreeItemData(circuit))
        root_item = self.fileTreeCtrl.GetRootItem()
        circuit.tree_item_id = root_item
        self._add_subcircuits(root_item, circuit)
        self._restore_tree_state()
        # update sweep list
        sweep_set = circuit._sweep_set
        if sweep_set is None:
            circuit.get_signals()[0].get_values()
            sweep_set = circuit._sweep_set
        self.sweepListCtrl.ClearAll()
        for i, name in enumerate(sweep_set._names):
            self.sweepListCtrl.InsertColumn(i, name)
        if len(sweep_set._points) > 1:
            for i, sweep_point in enumerate(sweep_set._points):
                row = ["%4g" % item for item in sweep_point]
                self.sweepListCtrl.Append(row)
            self.sweepListCtrl.Select(0)

    def _add_subcircuits(self, parent_item, circuit):
        for subckt in circuit.get_subcircuits():
            subckt_item = self.fileTreeCtrl.AppendItem(parent_item, subckt.name,
                    image=1,
                    data=wx.TreeItemData(subckt))
            subckt.tree_item_id = subckt_item
            self._add_subcircuits(subckt_item, subckt)

    def _restore_tree_state(self):
        root_item = self.fileTreeCtrl.GetRootItem()
        self._restore_item_state(root_item)
        circuit = self.fileTreeCtrl.GetItemPyData(root_item)
        if circuit.selected is None:
            circuit.selected = self.fileTreeCtrl.GetItemPyData(root_item)
        self.fileTreeCtrl.SelectItem(self.fileTreeCtrl.GetSelection(), False)
            # toggle selection to trigger refresh of signal list box
        self.fileTreeCtrl.SelectItem(circuit.selected.tree_item_id, True)

    def _restore_item_state(self, item):
        # recurse
        if self.fileTreeCtrl.ItemHasChildren(item):
            child, cookie = self.fileTreeCtrl.GetFirstChild(item)
            while True:
                self._restore_item_state(child)
                if child == self.fileTreeCtrl.GetLastChild(item):
                    break
                child, cookie = self.fileTreeCtrl.GetNextChild(item, cookie)
        # restore state
        circuit = self.fileTreeCtrl.GetItemPyData(item)
        if circuit.is_open():
            self.fileTreeCtrl.Expand(item)
        else:
            self.fileTreeCtrl.Collapse(item)

    def _save_tree_state(self):
        if not self.fileTreeCtrl.IsEmpty():
            root_item = self.fileTreeCtrl.GetRootItem()
            self._save_item_state(root_item)
            circuit = self.fileTreeCtrl.GetItemPyData(root_item)
            selected_item = self.fileTreeCtrl.GetSelection()
            circuit.selected = self.fileTreeCtrl.GetItemPyData(selected_item)

    def _save_item_state(self, item):
        # recurse
        if self.fileTreeCtrl.ItemHasChildren(item):
            child, cookie = self.fileTreeCtrl.GetFirstChild(item)
            while True:
                self._save_item_state(child)
                if child == self.fileTreeCtrl.GetLastChild(item):
                    break
                child, cookie = self.fileTreeCtrl.GetNextChild(item, cookie)
        # save state
        circuit = self.fileTreeCtrl.GetItemPyData(item)
        circuit._opened = self.fileTreeCtrl.IsExpanded(item)
        circuit.tree_item_id = None

    def OnTree_sel_changed_fileTreeCtrl(self, evt):
        selection = self.fileTreeCtrl.GetSelection()
        if selection:
            subcircuit = self.fileTreeCtrl.GetItemData(selection).GetData()
            # restore filter string
            self.filterSearchCtrl.SetValue(subcircuit._filter_regex)
            # update signal list
            self._update_signal_list(subcircuit, subcircuit._filter_regex)

    def _update_signal_list(self, circuit, regex):
        signals = circuit.get_signals()
        try:
            re_signals = re.compile(regex)
        except:
            return
        self.signalListBox.Clear()
        for signal in signals:
            if re_signals.match(signal.name):
                item = self.signalListBox.Append(signal.name, signal)

    def open_file(self, file_path):
        if file_path in self.open_files:
            raise FileAlreadyOpen()
        data_source = open_data_file(file_path)
        data_source.number = self.data_source_counter
        self.data_source_counter += 1
        self.open_files.append(file_path)
        item = self.fileChoice.Append("{1} [{0}] ".format(data_source.number,
                                                         data_source.name),
                                      data_source)
        return data_source, item

    def OnListbox_dclick_signalListBox(self, evt):
        signal = evt.GetClientData()
        plot_view = self.viewNotebook.GetCurrentPage()
        selected_sweep = self.sweepListCtrl.GetFirstSelected()
        if selected_sweep == -1:
            sweep_point = None
        else:
            sweep_point = signal.get_circuit()._sweep_set._points[selected_sweep]
        plot_view.add_plot(signal, sweep_point)

    def OpenNewPlotView(self):
        plotView = PlotView(self.viewNotebook)
        self.viewNotebook.AddPage(plotView, "plot view")
        self.viewNotebook.ChangeSelection(self.viewNotebook.GetPageCount() - 1)

    def OnText_filterSearchCtrl(self, evt):
        subcircuit = self.fileTreeCtrl.GetItemPyData(self.fileTreeCtrl.GetSelection())
        subcircuit._filter_regex = self.filterSearchCtrl.GetValue()
        self._update_signal_list(subcircuit, subcircuit._filter_regex)

    def OnSearchctrl_cancel_btn_filterSearchCtrl(self, evt):
        self.filterSearchCtrl.Clear()
        self.OnText_filterSearchCtrl(None)

    # File menu
    def OnMenu_fileOpenMenuItem(self, evt):
        # retrieve path where currently selected data file is located
        path = None
        selection = self.fileChoice.GetSelection()
        if selection != wx.NOT_FOUND:
            data_source = self.fileChoice.GetClientData(selection)
            if issubclass(type(data_source), DataFile):
                path = os.path.dirname(data_source.file_path)

        # create file open dialog
        filedialog = wx.FileDialog(self,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
            wildcard="All files (*.*)|*|HSPICE files (*.tr*, *.ac*, *.sw0, *.ft*)|*.ac*|Touchstone files (*.s*p)|*.s*p")
        if path:
            filedialog.SetDirectory(path)
        filedialog.ShowModal()
        filenames = filedialog.GetFilenames()
        item = None
        if filenames:
            filepaths = filedialog.GetPaths()
            for i, filename in enumerate(filenames):
                try:
                    data_source, item = self.open_file(filepaths[i])
                except FileAlreadyOpen:
                    d = wx.MessageDialog(self, "File is already open", "Alert", wx.OK)
                    d.ShowModal()
                    d.Destroy()
            self._save_tree_state()
            if item is not None:
                self.fileChoice.SetSelection(item)
                self._populate_tree(data_source.get_circuit())

    def OnMenu_fileReloadMenuItem(self, evt):
        selection = self.fileChoice.GetSelection()
        data_source = self.fileChoice.GetClientData(selection)
        if data_source.changed():
            data_source.reload()
            self._populate_tree(data_source.get_circuit())
        

    def OnMenu_fileCloseMenuItem(self, evt):
        selection = self.fileChoice.GetSelection()
        if selection == wx.NOT_FOUND:
            return
        data_source = self.fileChoice.GetClientData(selection)
        self.open_files.remove(data_source.file_path)
        # TODO: remove all plots from the plot views
        self.fileChoice.Delete(selection)

        if self.fileChoice.GetCount() > 0:
            new_selection = (selection - 1) % self.fileChoice.GetCount()
            print new_selection
            self.fileChoice.SetSelection(new_selection)
            data_source = self.fileChoice.GetClientData(new_selection)
            self._populate_tree(data_source.get_circuit())
        else:
            self.fileTreeCtrl.DeleteAllItems()
            self.signalListBox.Clear()
            self.data_source_counter = 1

    def OnMenu_exitMenuItem(self, evt):
        wx.Exit()

    # View menu
    def OnMenu_viewNewMenuItem(self, evt):
        self.OpenNewPlotView()

    def OnMenu_viewCloseMenuItem(self, evt):
        currentPlotViewIndex = self.viewNotebook.GetSelection()
        self.viewNotebook.RemovePage(currentPlotViewIndex)

        if self.viewNotebook.GetPageCount() == 0:
            self.OpenNewPlotView()

    def OnMenu_viewRenameMenuItem(self, evt):
        currentPlotViewIndex = self.viewNotebook.GetSelection()
        currentName = self.viewNotebook.GetPageText(currentPlotViewIndex)
        d = wx.TextEntryDialog(self, "Enter new name", "Rename plot view", currentName, wx.OK | wx.CANCEL)
        d.ShowModal()
        d.Destroy()
        self.viewNotebook.SetPageText(currentPlotViewIndex, d.GetValue())

    # Help menu
    def OnMenu_aboutMenuItem(self, evt):
        aboutInfo = wx.AboutDialogInfo()
        aboutInfo.SetName("pyWave")
        aboutInfo.SetDescription("a waveform viewer")
        aboutInfo.AddDeveloper("Brecht Machiels")
        aboutInfo.SetVersion("alpha")
        wx.AboutBox(aboutInfo)

    # Toolbar buttons map to menu items
    def OnTool_fileOpenTool(self, evt):
        self.OnMenu_fileOpenMenuItem(evt)

    def OnTool_fileReloadTool(self, evt):
        self.OnMenu_fileReloadMenuItem(evt)

    def OnTool_fileCloseTool(self, evt):
        self.OnMenu_fileCloseMenuItem(evt)

    def OnTool_viewNewTool(self, evt):
        self.OnMenu_viewNewMenuItem(evt)

    def OnTool_viewCloseTool(self, evt):
        self.OnMenu_viewCloseMenuItem(evt)


def open_data_file(file_path):
    print DataFile.__subclasses__()
    for subclass in DataFile.__subclasses__():
        if subclass.test(file_path):
            return subclass(file_path)


class FileAlreadyOpen(Exception):
    pass


class MyApp(wx.App):
    def OnInit(self):
        # Display the frame
        self.frame = MyMainFrame(None)
        self.frame.Center()
        self.frame.Show(1)
        return True

def main():
    import sys
    from optparse import OptionParser

    usage = "usage: %prog [options] <file>"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--debug",
                      action="store_true", dest="verbose", default=False,
                      help="print debug output")

    (options, args) = parser.parse_args()

    app = MyApp()
    app.MainLoop()
