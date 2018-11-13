from kafe import *
from kafe.function_library import quadratic_3par
from numpy import loadtxt, arange
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.backends.backend_pdf import PdfPages

import csv
from scipy.optimize import curve_fit
import tables as tb
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as ticker
import itertools
from matplotlib.colors import LogNorm
from matplotlib import pyplot as p
from mpl_toolkits.mplot3d import Axes3D    # @UnusedImport
from math import pi, cos, sin
import logging
from scipy.linalg import norm
import os
from matplotlib import gridspec
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - [%(levelname)-8s] (%(threadName)-10s) %(message)s")

class Calibration_Curves():
    def linear(self, x, m, c):
        return m * x + c

    def red_chisquare(self, observed, expected, observed_error, popt):
        return np.sum(((observed - expected) / observed_error)**2 / (len(observed_error) - len(popt) - 1))

    def ln(self, x, a, b, c):
        return a * np.log(x + b) - c

    def exp(self, x, a, b, c):
        return a * np.exp(-b * x) + c

    def Inverse_square(self, x, a, b):
        return a / (x + b)**2
        
    def calibration_curve(self, Directory=False, PdfPages=False, stdev=0.06, tests="without_Al_Filter"):
        ''', 
        To get the calibration curves for each current
        For each Measurement you make you need to replace the numbers 0 in Background, Factor, .....by your measurement
        Background =  array of background estimated for each depth
                Cern Results @(40kv and 50 mA)        Bonn Results @(40kv and 50 mA)
        2 cm     0.439 muA    8.577 Mrad/hr            ------ muA    ----- Mrad/hr
        3 cm     0.694 muA    6.714 Mrad/hr            0.4358 muA    4.194 Mrad/hr
        5 cm     0.936 muA    4.402 Mrad/hr            0.3261 muA    3.281 Mrad/hr
        8 cm     0.257 muA    2.471 Mrad/hr            0.2128 muA    2.077 Mrad/hr
#         '''
        #Background = [0, 0, 0, 6.852006e-09, 0, 6.852006e-09, 0, 6.852006e-09]
        #Factor = [0, 0, 0, 9.62, 0, 9.76, 0, 10.06]
        depth = ["3cm","5cm", "8cm"]
        Voltages = ["30KV", "40KV"]
        colors = ['red','#006381', '#33D1FF', 'green', 'orange', 'maroon']
        styles = ['-', '--']
        for i in range(len(depth)):
            fig = plt.figure()
            #ax = fig.add_subplot(111)
            gs = gridspec.GridSpec(2, 1, height_ratios=[3.5, 0.5])
            #fig, (ax, tabax) = plt.subplots(nrows=2)
            ax = plt.subplot(gs[0])
            ax2 = plt.subplot(gs[1])
            for volt in Voltages:
                x1 = []
                y1 = []
                y2 = []
                bkg_y1 = []
                bkg_y2 = []
                Factor = []
                difference = []
                with open(Directory +"with_Al_Filter/" + depth[i] + "/" + volt + ".csv", 'r')as data:  # Get Data for the first Voltage
                    reader = csv.reader(data)
                    reader.next()
                    for row in reader:
                        x1 = np.append(x1, float(row[0]))
                        y1 = np.append(y1, (float(row[1]) - float(row[2])) * float(row[5]))
                        bkg_y1 = np.append(bkg_y1, float(row[2]))
                        y2 = np.append(y2, (float(row[3]) - float(row[4])) * float(row[5]))
                        bkg_y2 = np.append(bkg_y2, float(row[4]))
                        Factor = np.append(Factor, float(row[5]))
                        difference = np.append(difference,(float(row[3]) - float(row[1])) / float(row[3])*100)
                    logging.info("Start Plotting %s cm" % (depth[i]))
                    sig1 = [stdev * y1[k] for k in range(len(y1))]
                    popt1, pcov = curve_fit(self.linear, x1, y1, sigma=sig1, absolute_sigma=True, maxfev=5000, p0=(1, 1))
                    chisq1 = self.red_chisquare(np.array(y1), self.linear(x1, *popt1), np.array(sig1), popt1)
                    ax.errorbar(x1, y1, yerr=sig1, color=colors[Voltages.index(volt)], fmt='o')
                    ax.plot(x1, self.linear(x1, *popt1), linestyle=styles[0],
                            color=colors[Voltages.index(volt)], label=volt + " " + "with_Al_Filter")
                    
                    sig2 = [stdev * y2[k] for k in range(len(y2))]
                    popt2, pcov = curve_fit(self.linear, x1, y2, sigma=sig2, absolute_sigma=True, maxfev=5000, p0=(1, 1))
                    chisq2 = self.red_chisquare(np.array(y2), self.linear(x1, *popt2), np.array(sig2), popt2)
                    ax.errorbar(x1, y2, yerr=sig2, color=colors[Voltages.index(volt)], fmt='o')
                    ax.plot(x1, self.linear(x1, *popt2), linestyle=styles[1],
                            color=colors[Voltages.index(volt)], label=volt + " " + "without_Al_Filter")
                    sig3 = [stdev * difference[k] for k in range(len(difference))]
                    ax2.errorbar(x1, difference, yerr=sig3, color=colors[Voltages.index(volt)], fmt='o',markersize='1',capsize=2)
                                               
                    #df = pd.DataFrame({"chisq_" + volt: chisq, "(m,c)_" + volt: tuple(popt1)})
                    #df.to_csv(Directory + test + "/" + depth[i] + "/Calibration_parameters_" + depth[i] + volt + ".csv", index=True)

            plt.ticklabel_format(useOffset=False)
            plt.xlim(0, 60)
            ax.set_title('Calibration curve for ' + depth[i], fontsize=12)
            ax.set_ylabel('Dose rate [$Mrad(sio_2)/hr$]')
            ax.set_ylabel('Dose rate drop [%]')
            ax.grid(True)
            ax2.yaxis.set_ticks(np.arange(60, 90, step=10))
            #ax2.set_ylim(0,101,10)
            ax2.grid(True)
            ax.legend()
            ax2.set_xlabel('Tube current (mA)')
            plt.savefig(Directory +"with_Al_Filter/" + depth[i] + '/CalibrationCurve_Bonn_' + depth[i] + ".png", bbox_inches='tight')
            PdfPages.savefig()

    def Dose_Voltage(self, Directory=False, PdfPages=False, Depth="8cm", test="without_Al_Filter"):
        '''
        Effect of tube Voltage on the Dose
        '''

        y1 = []
        x1 = []
        Dataset = []
        kafe_Fit = []
        fig = plt.figure()
        ax = fig.add_subplot(111)
        Current = ["10mA", "20mA", "30mA", "40mA"]
        for i in range(len(Current)):
            x = []
            y = []
            Background = [0.00801e-06]
            Factor = [10.06]
            Current = ["10mA", "20mA", "30mA", "40mA"]
            facecolors = ['#33D1FF','#006381', 'green', 'orange', 'maroon','red']
            with open(Directory + test + "/Dose_Voltage/" + Depth + "/" + Current[i] + ".csv", 'r')as data1:
                reader = csv.reader(data1)
                reader.next()
                for row in reader:
                    x = np.append(x, float(row[0]))
                    y = np.append(y, (float(row[1]) - Background[0]) * Factor[0])
            x1.append(x)
            y1.append(y)
            stdev = 0.06
            sig = [stdev * y1[i][k] for k in range(len(y1[i]))]
            Dataset = np.append(Dataset, build_dataset(x1[i],y1[i],yabserr=sig,title='I=%s'%Current[i], axis_labels=['Voltage (kV)', '$Dose rate [Mrad(sio_2)/hr]$']))
            
            popt, pcov = curve_fit(self.ln, x1[i], y1[i], sigma=sig, absolute_sigma=True, maxfev=5000, p0=(1, 1, 1))
            xfine = np.linspace(0., 60., 100)
            plt.plot(xfine, self.ln(xfine, *popt), facecolors[i])
            chisq = self.red_chisquare(np.array(y1[i]), self.ln(x1[i], *popt), np.array(sig), popt)
            plt.errorbar(x1[i], y1[i], yerr=sig, color=facecolors[i], fmt='o', label='I=%s, $\chi^2$ =%f ' % (Current[i], chisq))
            #df = pd.DataFrame({"chisq": chisq, "(a,b,c)": tuple(popt)})
            #df.to_csv(Directory + test + "/Dose_Voltage/" + Depth + "/Calibration_parameters_" + Current[i] + ".csv", index=True)
        ax.text(0.98, 0.83, "D(V)=a*log(V + b)-c",
                horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.set_title('Effect of tube Voltage at ' + Depth +" "+test, fontsize=12)
        ax.set_ylabel('Dose rate [$Mrad(sio_2)/hr$]')
        ax.set_xlabel('Voltage (kV)')
        ax.grid(True)
        ax.legend()
        plt.ticklabel_format(useOffset=False)
        plt.xlim(5, 60)
        plt.ylim(0.1, 7.5)
        plt.savefig(Directory + test + "/Dose_Voltage/" + Depth + "/" + Depth + Directory[58:-1] + ".png", bbox_inches='tight')
        PdfPages.savefig()
        for Data in Dataset:
            kafe_Fit = np.append(kafe_Fit, Fit(Data, quadratic_3par))
        for fit in kafe_Fit:
            fit.do_fit()
        kafe_plot = Plot(kafe_Fit[2],kafe_Fit[3])
        kafe_plot.plot_all(show_data_for='all',show_band_for=0)
        kafe_plot.save(Directory + test + "/Dose_Voltage/" + Depth + "/" + Depth + Directory[58:-1] +"_kafe_Fit"+".png")
        
        PdfPages.savefig()

    def Depth_Diameter(self, Directory=False, Unknown_diameter=[4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15], PdfPages=False, tests=["without_Al_Filter"]):
        '''
        To get the estimated beam diameter relative to the depth
        '''
        def New_diameter(dx=15,diameter = False,height = False):
            Theta = []
            for i in range(len(diameter)):
                for j in range(len(diameter)):
                    if (i > j):
                        d_diff = diameter[i] - diameter[j]
                        h_diff = height[i] - height[j]
                        Theta = np.append(Theta, d_diff / h_diff)
            hx = (dx - diameter[2]) / np.mean(Theta) + height[2]
            # print "Height for diameter %i cm is %i cm " % (dx, hx)
            return np.round(hx), Theta
        for j in range(len(tests)):
            fig = plt.figure()
            fig.add_subplot(111)
            ax = plt.gca()
            
            Factor = 9.76 # Calibration Factor
            y1 = []
            r1 = []
            diameter = []
            height = []
            with open(Directory + tests[j] + "/Dose_Depth/Dose_Depth.csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    if (float(row[2]) <100): # Some missing data needed to be taken  in the future
                        height = np.append(height, float(row[0]))# Distance from the source
                        diameter = np.append(diameter, float(row[2])*2) #Diameter of the beam
            
            for i in range(len(Unknown_diameter)):
                Unknown_height, Theta = New_diameter(dx=Unknown_diameter[i],diameter =diameter,height =height)
                diameter = np.append(diameter, Unknown_diameter[i])
                height = np.append(height, Unknown_height)
            for i in range(len(diameter)):
                x = np.linspace(-diameter[i] / 2.0, diameter[i] / 2.0, 10)
                y = np.arange(height[i] / 10.0, height[i] + height[i] / 10.0, height[i] / 10.0)
                if i <= 4:  # These values are measured experimentaly
                    linestyle = "solid"
                else:
                    linestyle = "dashed"  # These are Theoritical values
                    
                plt.plot(x, self.linear(y, m=0, c=height[i]), linestyle=linestyle)
    
            ax.text(0.95, 0.90, "$\Theta$ = %.2f ,  E($\Theta$)=%.2f" % (np.mean(Theta), np.std(Theta)),
                    horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            ax.set_title('Diameter covered by beam spot %s'%(tests[j]), fontsize=12)
            ax.invert_yaxis()
            ax.set_xlabel('Diameter [cm]')
            ax.set_ylabel('Depth from the beam window [cm]')
            ax.grid(True)
            fig.savefig(Directory + tests[j] + '/Depth_Diameter_' + tests[j] + '.png', bbox_inches='tight')
            PdfPages.savefig()

    def Dose_Depth(self, Directory=False, PdfPages=False, Voltage="40 kV", current="50 mA", stdev=0.1, test="without_Al_Filter", theta = 0.16):
        '''
        Relation between the depth and  the Dose rate
        '''          
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        colors = ['#33D1FF', 'maroon','#006381', 'green', 'orange','red'] 
        for i in range(len(tests)):
            Factor = 9.76 # Calibration Factor
            height = []
            diameter = []
            y1 = []
            r1 = []
            b1 = []
            Unknown_radius = []
            with open(Directory + tests[i] + "/Dose_Depth/Dose_Depth.csv", 'r')as data:
                reader = csv.reader(data)
                reader.next()
                for row in reader:
                    height = np.append(height, float(row[0]))# Distance from the source
                    y1 = np.append(y1, (float(row[1]))*Factor) # Dose rate
                    r1 = np.append(r1, float(row[2])) #radius of the beam
                    diameter =  np.append(r1, float(row[2])*2) #Diameter of the beam
                    b1 = np.append(b1, float(row[3])) # Background
            y1 = [y1[k]- b1[k] for k in range(len(y1))] # Subtrac Background   
            sig = [stdev * y1[k] for k in range(len(y1))]
            for h in range(len(r1)):
                if diameter[h]<100:
                    Unknown_radius  = np.append(Unknown_radius , ((height[h]-height[1])*theta+ diameter[1])*0.5)
            xfine = np.linspace(0, height[-1], 100)  # define values to plot the function for
            popt1, pcov = curve_fit(self.Inverse_square, height, y1, sigma=sig, absolute_sigma=True, maxfev=5000, p0=(300, 10))
            #b_fixed = 2
            #popt1, pcov = curve_fit(lambda x1, a, b: self.Inverse_square(x1, a, b_fixed), x1, y1) 
            chisq1 = self.red_chisquare(np.array(y1), self.Inverse_square(np.array(height), *popt1), sig, popt1)
            ax.errorbar(height, y1,yerr=sig, color=colors[i], fmt='o', label=tests[i])
            ax.plot(xfine, self.Inverse_square(xfine, *popt1),colors[i],label='Fit: a=%5.2f ,b=%5.2f' % tuple(popt1) + ' & $\chi^2_{red}$ =%5.2f' % (chisq1))
            ax.text(0.9, 0.69, r'$D= \frac{a}{(r+b)^2}$',
                horizontalalignment='right', verticalalignment='top', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)) 
            newlabel = np.arange(0,height[-1],10) # labels of the xticklabels: the position in the new x-axis
            function = lambda t: ((t-height[1])*theta+ diameter[1])*0.5
            newpos  = [function(t) for t in newlabel]   # position of the xticklabels in the old x-axis
            if tests[i] == "without_Al_Filter":
                point_label = [str(r1[0])+' cm', str(r1[1])+' cm', str(r1[2])+' cm', str(r1[3])+' cm','','','']
                for X, Y, Z in zip(height, y1, point_label):
                    plt.annotate('{}'.format(Z), xy=(X, Y), xytext=(27,4), ha='right', textcoords='offset points', fontsize=7)
#                 ax3 = ax.twiny()
#                 ax3.set_xticks(newpos)
#                 #ax2.set_xticklabels(newlabel)
#                 ax3.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
#                 ax3.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
#                 ax3.tick_params(axis='x', colors=colors[i])
#                 #ax.xaxis.label.set_color(colors[i])
#                 ax3.spines['bottom'].set_position(('outward', 36))
#                 ax3.set_ylim(ax.get_ylim()[0], ax.get_ylim()[-1])
#                 print newpos
            if tests[i] == "with_Al_Filter":
                point_label = [str(r1[0])+' cm', str(r1[1])+' cm', '', str(r1[3])+' cm','','',str(r1[6])+' cm']
                for X, Y, Z in zip(height, y1, point_label):
                    plt.annotate('{}'.format(Z), xy=(X, Y), xytext=(27,4), ha='right', textcoords='offset points', fontsize=7)
#                 ax2 = ax.twiny()
#                 ax2.set_xticks(newpos)
#                 print newpos
#                 #ax2.set_xticklabels(newlabel)
#                 ax2.xaxis.set_ticks_position('bottom') # set the position of the second x-axis to bottom
#                 ax2.xaxis.set_label_position('bottom') # set the position of the second x-axis to bottom
#                 ax2.tick_params(axis='x', colors=colors[i])
#                 #ax.xaxis.label.set_color(colors[i])
#                 ax2.spines['bottom'].set_position(('outward', 60))
#                 ax2.set_xlabel('Radius [cm]')
#                 ax2.set_ylim(ax.get_ylim()[0], ax.get_ylim()[-1])
#         
                      
            ax.set_title('Dose rate vs Distance at  (%s and %s)' % (Voltage, current), fontsize=11)
            ax.set_ylabel('Dose rate (D) [$Mrad(sio_2)/hr$]')
            ax.set_xlabel('Distance (r) [cm]')
            ax.set_xlim([0, max(height)+8])
            ax.grid(True)
            ax.legend()
            ax.ticklabel_format(useOffset=False)
            fig.savefig(Directory + tests[i] + "/Dose_Depth/Dose_Depth_"+ tests[i] +".png", bbox_inches='tight')
        plt.tight_layout()
        PdfPages.savefig()

    def Plot_Beam_profile_2d(self, Scan_file=False, Directory=False, Steps=121, width=1, PdfPages=False):
        '''
        Make a 2d scan at specific depth
        '''
        Background = 0.1
        Factor = 10
        with tb.open_file(Scan_file, 'r') as in_file1:
            Map1 = in_file1.root.Mercury_MotorStage[:]
        fig, ax = plt.subplots()
        plt.axhline(y=13, linewidth=2, color='#d62728', linestyle='dashed')
        plt.axvline(x=100, linewidth=2, color='#d62728', linestyle='dashed')
        im = ax.imshow((Map1 * 10e6 - Background) * Factor, aspect='auto', interpolation='gaussian')
        cb = fig.colorbar(im, ax=ax, fraction=0.0594)
        cb.set_label("Dose rate [$Mrad/hr$]")
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y[mm]')
        ax.set_title('Beam profile at 8 cm without collimator support', fontsize=12)
        plt.savefig(Directory + Directory[58:-1] + '2DMap.png')
        PdfPages.savefig()

    def Plot_Beam_profile_3d(self, Scan_file=False, Directory=False, Steps=121, width=1, PdfPages=False):
        '''
        Make a 3d scan at specific depth (The function is under updates)
        '''
        Background = 0.1
        Factor = 10

        def f(x, y):
            with tb.open_file(Scan_file, 'r') as in_file1:
                Map1 = in_file1.root.Mercury_MotorStage[:]
            return (Map1[x, y] * 10e6 - Background) * Factor
        y = np.linspace(0, Steps - 1, Steps - 1, dtype=int)
        x = np.linspace(0, width - 1, width - 1, dtype=int)
        X, Y = np.meshgrid(x, y)
        Z = f(X, Y)
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        plot = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
        scale_x = 10
        scale_y = 10
        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale_x))
        ax.xaxis.set_major_formatter(ticks_x)
        ticks_y = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale_y))
        ax.yaxis.set_major_formatter(ticks_y)
        plt.axhline(y=13, linewidth=2, color='#d62728', linestyle='dashed')
        plt.axvline(x=100, linewidth=2, color='#d62728', linestyle='dashed')
        cb = fig.colorbar(plot, ax=ax, fraction=0.046)
        cb.set_label("Dose rate [$Mrad/hr$]")
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y[mm]')
        ax.set_title('Beam profile at 8 cm without collimator support', fontsize=12)
        plt.savefig(Directory + Directory[58:-1] + '3DMap.png')
        PdfPages.savefig()

    def power_2d(self, Directory=False, PdfPages=False, size_I=50, size_V=60, V_limit=50, I_limit=50):
        '''
        Calculate the power in each point of I and V
        '''

        Power = np.zeros(shape=(size_I, size_V), dtype=float)
        power_max = np.zeros(shape=(size_I, size_V), dtype=float)
        p_max = V_limit * I_limit
        V = np.arange(0, size_V, 1)
        for i in range(size_I):
            for v in range(len(V)):
                Power[i, v] = i * v
                if (i * v == p_max):
                    power_max[i, v] = i * v
        fig, ax = plt.subplots()
        im = ax.imshow(Power, aspect='auto', origin='lower', interpolation='gaussian', cmap=plt.get_cmap('tab20c'))
        cb = fig.colorbar(im, ax=ax, fraction=0.0594)
        cb.set_label("Power [W]")
        ax.set_xlabel('Voltage [kV]')
        ax.set_ylabel('Current [mA]')
        ax.set_xlim([0, len(V)])
        ax.set_ylim([0, size_I])
        ax.set_title('Power of x-ray tube ', fontsize=12)
        ax.grid()
        ax2 = ax.twinx()
        x, y = np.where(power_max)
        ax2.axis('off')
        ax2.set_ylim([0, size_I])
        plt.axhline(y=I_limit, linewidth=2, color='#d62728', linestyle='solid')
        plt.axvline(x=V_limit, linewidth=2, color='#d62728', linestyle='solid')
        plt.tight_layout()
        plt.savefig(Directory + 'Power.png')
        PdfPages.savefig()

    def close(self):
        PdfPages.close()


if __name__ == '__main__':
    global PdfPages
    Directory = "Calibration_Curves/Bonn/"
    Scan_file = Directory + "Mercury_MotorStage.h5"
    tests = ["without_Al_Filter", "with_Al_Filter"]
    scan = Calibration_Curves()
#     scan.Plot_Beam_profile_2d(Scan_file=Scan_file, Steps=200, width=20)
#     scan.Plot_Beam_profile_3d(Scan_file=Scan_file, Steps=200, width=20)
    PdfPages = PdfPages('output_data/CalibrationCurve_Bonn' + '.pdf')
    scan.calibration_curve(stdev=0.05, PdfPages=PdfPages, Directory=Directory, tests=["with_Al_Filter"])
    scan.Depth_Diameter(Directory=Directory, PdfPages=PdfPages, tests=["without_Al_Filter"])
    scan.Dose_Depth(test=tests, Directory=Directory, PdfPages=PdfPages)
    scan.power_2d(PdfPages=PdfPages, Directory=Directory, V_limit=50, I_limit=50)
    scan.Dose_Voltage(PdfPages=PdfPages, Directory=Directory, test="without_Al_Filter")
    scan.close()
