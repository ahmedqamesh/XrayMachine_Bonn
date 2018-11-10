import sys,os
import matplotlib
import ROOT
from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1F, TFile, TH1D
from ROOT import gROOT, gBenchmark
#import root_numpy as r2n
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import colors, cm
from matplotlib import pyplot as plt
#import matplotlib.pyplot as plt
import datetime as dt
import time
from pytz import timezone

matplotlib.rc('text', usetex = True)
params = {'text.latex.preamble': [r'\usepackage{siunitx}']}   
plt.rcParams.update(params)
class Simulation():
    def makeExtent(self, xTicks,yTicks):
       dX=(xTicks[1]-xTicks[0])/2
       dY=(yTicks[1]-yTicks[0])/2
       return (yTicks[0] -dY , yTicks[-1] + dY, xTicks[0] - dX, xTicks[-1]+ dX)
    def get_numpy_hist_from_root(self, fname, histname):
    
        rootfile = ROOT.TFile(fname)
        hist = rootfile.Get(histname)
        return hist2array(hist)
    # To call it 
    # Directory = "/home/silab62/git/XrayMachine_Bonn/Calibration_Curves/Bonn/Simulation/"
    # root_files = [Directory+"Geant4/Geant4_empenelope_DiffEnergys/gammaSpectrum_10keV.root"]
    # Hist = get_numpy_hist_from_root(root_files[0],"h3")
    # print Hist 

    def readHistogram(self,filename,histname,overflow=True):
        rootFile=TFile("file:%s"%filename)
        assert rootFile.IsOpen(),"could not open file %s"%filename
        try:
            rootHist=rootFile.Get(histname)
            #assert rootHist.Class().GetName() in __rootHistogramList__,"%s is not a histogram type"%rootHist.Class().GetName()
        except:
            raise
        rootHist=histname
        dims=int(rootHist.Class().GetName()[2])
        s = e = 1
        if overflow:
            s = 0
            e = 2
    
        if dims==1:
            data= [rootHist.GetBinContent(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersX=[rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data),np.asarray(binCentersX)
        if dims==2:
    
            data = [[rootHist.GetBinContent(j,i) for i in range(s, rootHist.GetNbinsY() + e)] for j in range(s, rootHist.GetNbinsX() + e) ]
            binCentersX = [rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersY = [rootHist.GetYaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsY() + e)]
    
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data),np.asarray(binCentersX),np.asarray(binCentersY)
        if dims==3:
            data = [[[rootHist.GetBinContent(k,j,i) for i in range(s, rootHist.GetNbinsZ() + e)] for j in range(s, rootHist.GetNbinsY() + e) ] for k in range(s, rootHist.GetNbinsX() + e) ]
            binCentersX = [rootHist.GetXaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsX() + e)]
            binCentersY = [rootHist.GetYaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsY() + e)]
            binCentersZ = [rootHist.GetZaxis().GetBinCenter(i) for i in range(s, rootHist.GetNbinsZ() + e)]
            rootFile.Close()
            del rootHist
            del rootFile
            return np.asarray(data),np.asarray(binCentersX),np.asarray(binCentersY),np.asarray(binCentersZ)
    
    __rootHistogramList__=["TH%d%s"%(__i__,__type__) for __i__ in range(1,4) for __type__ in ['C','S','I','F','D']]
    
    def getListOfHistograms(self,filename):
        rootFile = TFile("file:%s" % filename)
        assert rootFile.IsOpen(), "could not open file %s" % filename
        l=list(rootFile.GetListOfKeys())
        return [obj.GetName() for obj in l if obj.GetClassName() in __rootHistogramList__]
    def energy(self, Directory=False, PdfPages=False, Energy= False,hist_id=False):
        fig = plt.figure()
        #FigureCanvas(fig)
        ax = fig.add_subplot(111)
            
        for i in range(len(Energy)):
            Energy_file = Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_"+Energy[i]+".root"
            f = ROOT.TFile(Energy_file)
            t=f.Get(hist_id)
            #t.Draw("t")
            data,x=self.readHistogram(Energy_file,t, False)
            entries = np.nonzero(data)
            ax.errorbar(x, data, fmt='-',markersize = 2, label =Energy[i] )
            #line_fit_legend_entry = 'line fit: ax + b\na=$%.2f\pm%.2f$\nb=$%.2f\pm%.2f$' % (fit_fn[1], np.absolute(pcov[0][0]) ** 0.5, fit_fn[0], np.absolute(pcov[1][1]) ** 0.5)
            ax.set_title('Energy of neutral secondaries at creation')
            ax.set_xlabel('Energy [keV]')
            ax.set_ylabel('Counts')
            ax.legend()
            ax.grid(True)
            ax.set_yscale("log")
        plt.savefig(Directory+"/Geant4_empenelope_DiffEnergys/gammaSpectrum_.png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()
        
    def filters(self, Directory=False, PdfPages=False,Filters=False,title ="Tungsten Anode Spectrum After Different Filters",
                hist_id=False,filter_thickness=False):
        fig = plt.figure()
        #FigureCanvas(fig)
        ax = fig.add_subplot(111)
            
        for i in range(len(Filters)):
            file = Directory+"/Geant4_Filters/Tungsten_Spectrum_"+Filters[i]+".root"
            f = ROOT.TFile(file)
            if Filters[i] == "Test":
                t=f.Get("27")
            else:
                t=f.Get(hist_id)
            #t.Draw("t")
            data,x=self.readHistogram(file,t, False)
            entries = np.nonzero(data)
            ax.errorbar(x[1:], data[1:], fmt='-',markersize = 2, label =filter_thickness[i]+" "+Filters[i] )
        
            ax.set_title(title)
            ax.set_xlabel('Energy [keV]')
            ax.set_ylabel('Counts')
            ax.legend()
            ax.grid(True)
            ax.set_yscale("log")
        plt.savefig(Directory+"/Geant4_Filters/Tungsten_Spectrum_DiffFilters.png", dpi=300)
        plt.tight_layout()
        PdfPages.savefig()
                
    def close(self):
        PdfPages.close()
        
        
if __name__ == '__main__':
    global PdfPages
    Directory = "Simulation/Geant4/"
    Energy = ["10keV","20keV","30keV","40keV","50keV","60keV"]
    Filters = ["Anode_spectrum","Al"]#,"Fe","Mn","Ni","Va"]
    filter_thickness = ["","15$\mu m $"]#,"15$\mu m $","15$\mu m $","15$\mu m $","15$\mu m $"]
    scan = Simulation()
    PdfPages = PdfPages('output_data/SimulationCurve_Bonn' + '.pdf')
    #scan.energy(Directory=Directory, PdfPages=PdfPages, Energy=Energy,hist_id="h3")
    scan.filters(Directory=Directory, PdfPages=PdfPages,Filters=Filters,hist_id="32",filter_thickness=filter_thickness) 
    scan.close()