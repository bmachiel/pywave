import wx
import wx.xrc as xrc


class SearchCtrlXmlHandler(xrc.XmlResourceHandler):
    def __init__(self):
        xrc.XmlResourceHandler.__init__(self)
        # Standard styles
        self.AddWindowStyles()
        # Custom styles
        
    def CanHandle(self, node):
        return self.IsOfClass(node, 'wxSearchCtrl')
        
    # Process XML parameters and create the object
    def DoCreateResource(self):
        assert self.GetInstance() is None
        w = wx.SearchCtrl(self.GetParentAsWindow(),
                          self.GetID(),
                          self.GetText('value'),
                          self.GetPosition(),
                          self.GetSize(),
                          self.GetStyle())
        self.SetupWindow(w)
        return w