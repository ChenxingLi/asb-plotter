import numpy as np

def list_ceil(value, ticks):
    return next(filter(lambda x: x>value, ticks), None)

def decompose(real):
    dec = int(np.floor(np.log10(np.abs(real))))
    fra = real / 10**dec
    return fra, dec

def ceilY(y):
    ytick = y/8 * 1.1
    fra, dec = decompose(ytick)
    ytick = 10**dec * list_ceil(fra,[1,2,2.5,5,10])
    
    ymax = np.ceil(y*1.1/ytick)*ytick
    return ymax,ytick

remove_none = np.vectorize(lambda x: 0 if x is None or x == np.nan else x)

class LinePlot:
    def __init__(self):
        self.data = []
        self.maxY = 0
    
    def add(self,X,Y,**kwargs):
        self.data.append((X,Y,kwargs))
        self.maxY = max(self.maxY,max(Y))
        
    def draw(self,ax):
        for (X,Y,kwargs) in self.data:
            ax.plot(X,Y,**kwargs)
        ymax, ytick = ceilY(self.maxY)
        ax.set_ylim((0,ymax))
        ax.set_yticks(np.arange(0,ymax+ytick,ytick))
        
class BarPlot:
    def __init__(self):
        self.cols = None
        self.data = []
        self.label = []
        self.maxY = 0
        
    def add(self,label,*args):
        if self.cols is None:
            self.cols = len(args)
        else:
            assert self.cols == len(args)
        self.data.append(np.array(args))
        self.label.append(label)
        self.maxY = max(self.maxY,max(remove_none(args)))
        
    def draw(self,ax,labels=None,space=0.3):
        if labels is None:
            if self.cols == 1:
                labels=[""]
            else:
                raise Exception("Label lost")
        assert len(labels) == self.cols
        width = 1 - space
        self.space = space
        w = width/self.cols
        length = len(self.data)
        base = [(2*x+1)*w/2-width/2 for x in range(self.cols)]
        for idx, v in enumerate(np.array(self.data).T):
            v = remove_none(v)
            ax.bar(np.arange(length)+base[idx], v, width = w,label=labelize(labels[idx]))
            
        ax.set_xticks(np.arange(length))
        ax.set_xticklabels(self.label)
        ax.set_xlim((-0.5,length-0.5))
        
        ymax, ytick = ceilY(self.maxY)
        ax.set_ylim((0,ymax))
        ax.set_yticks(np.arange(0,ymax+ytick,ytick))
        
    def number(self,ax,align = None, format=None,**kwargs):
        if format is None:
            format = str
        
        if align is None:
            align = "c" * self.cols
            
        ymin,ymax = ax.get_ylim()
        height = ymax-ymin
        
        width = 1 - self.space
        w = width/self.cols
        length = len(self.data)
        base = [(2*x+1)*w/2-width/2 for x in range(self.cols)]
        for i, cluster in enumerate(self.data):
            for j,v in enumerate(cluster):
                if v is None:
                    continue
                pos = align[j]
                x = base[j] + i
                y = v + height * 0.05 * kwargs.get("hspace",1)
                text = format(v)
                if pos == "c":
                    ha = "center"
                elif pos == "l":
                    x -= w/2 - kwargs.get("padding",0)
                    ha = "left"
                elif pos == "r":
                    x += w/2 - kwargs.get("padding",0)
                    ha = "right"
                ax.text(x,y,text,ha=ha,va="baseline")
        