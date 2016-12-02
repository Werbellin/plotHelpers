from random import random
import ROOT as rt
rt.TH1.AddDirectory(rt.kFALSE)
import math

rt.gStyle.SetOptTitle(0)

def norm_hist(hist, norm = 1.) :
    integral = hist.Integral()
    if integral > 0. : hist.Scale(norm / integral)
    return hist

def scale_hist(hist, scale) :
    hist.Scale(scale)
    return hist

def get_copy(filename, histname) :

    afile = rt.TFile.Open(filename)

    #afile.ls()
    orgHist = afile.Get(histname)
    if orgHist == None :
        print 'Did not find histogram ', histname
        afile.ls()
    else :
        tmp = orgHist.Clone(orgHist.GetName() + '_copy' + str(random()) )
        #tmp.SetDirectory(False)
        afile.Close()
    return tmp

def get_plot(file_name, plot_name, options = None, reference_counts_name = None) :
    if options == None :
        options = {}
    print 'file_name ', file_name
    print 'plot_name', plot_name
    #return None
    out_plot = get_copy(file_name, plot_name)
    
    if 'Counters_hist' in options :
        counters = get_copy(file_name, 'Counters')
        sumOfWeights = counters.GetBinContent(40)
        factor = 1.
        if 'xsection' in options :
            xsection = options['xsection']
        return scale_hist(out_plot, xsection * sumOfWeights)

    if 'normalize' in options :
        return norm_hist(out_plot)

    if 'x_section' in options and 'reference_counts_name' is options :
        ref_counts_plot = get_copy(file_name, options['reference_counts_name'])
        return scale_hist(out_plot, options['x_section'] / ref_counts_plot.GetEntries())

    if 'x_section' in options :
        return norm_hist(out_plot, options['x_section'])

    if 'scale' in options :
        return scale_hist(out_plot, options['scale'])

    return out_plot


def sum_plots(plot_list = [], file_name = '', options = None) :
    if options == None :
        options = {}
        
    first_plot_item = plot_list[0]

    plots = []

    #if normalize :
    first_plot = get_plot(first_plot_item[0], first_plot_item[1])
    n_bins = first_plot.GetNbinsX()
    low_x = first_plot.GetXaxis().GetBinLowEdge(1)
    high_x = first_plot.GetXaxis().GetBinLowEdge(n_bins) + first_plot.GetXaxis().GetBinWidth(n_bins)

    out_plot = first_plot.Clone('sum_plots_' + str(random()))
    out_plot.Reset()

    for i_plot in range(0, len(plot_list)) :
        plot_item = plot_list[i_plot]
        plot = get_copy(plot_item[0], plot_item[1])

        if 'reference_counts_name' in options :
            ref_counts_plot = get_copy(plot_item[0], options['reference_counts_name'])
            get_plot(plot_item[0], plot_item[1])
            scale_hist(plot, x_section[i_plot] / ref_counts_plot.GetEntries())
        else :
            get_plot(plot_item[0], plot_item[1])

        plots.append(plot)

    for plot in plots:
        out_plot.Add(plot)

    if 'normalize' in options : norm_hist(out_plot)
    return out_plot

def to_precision(x,p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """
    x = float(x)

    if x == 0.:
        return "0." + "0"*(p-1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)

    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1

    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1


    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)

    return "".join(out)

def get_y_title(histo, draw_options) :
    xAxis = histo.GetXaxis()
    
    unit_dict = {'': ['phi', '\phi', 'eta', '\eta', 'BDT'], 'GeV' : ['pT', 'pT', 'p_T', 'p_{T}', 'p_{t}', 'mass', 'm', 'm_{ZZ}', 'm_{4l}']  }

    if 'y_unit' not in draw_options :
        unit = None
        xTitle = xAxis.GetTitle()
        #print 'low: ', xTitle.find("[")+1, '  high ', xTitle.find("]")
        low = xTitle.find("[")
        if low > -1 :
            unit = xTitle[low + 1 : xTitle.find("]")]
        #print 'unit given ', unit ,  '  ', xTitle
        if unit == '' :
            unit = None
    else :
        unit = draw_options['y_unit']
    if unit is None :
        for k,v in unit_dict.iteritems() :
            for qty in v :
                if xTitle.find(qty) > -1 :
                    #print 'found ', qty, '   in ', xTitle
                    #print 'unit=', k
                    unit = k
                    continue
            if unit is not None :
                continue

    bin_width = xAxis.GetBinWidth(1)

    if isinstance(histo, rt.TGraphAsymmErrors) :
        x0 = rt.Double()
        x1 = rt.Double()
        t = rt.Double()
        histo.GetPoint(0, x0, t)
        histo.GetPoint(1, x1, t)
        bin_width = x1 - x0
        
    if 'y_title' in draw_options :
        y_title = draw_options['y_title']
    else:
        y_title = None
        
    if y_title is None :
        y_title = histo.GetYaxis().GetTitle()

    bin_width_string = to_precision(bin_width, 2)

    if bin_width_string != '0' and  'no_y_bin' not in draw_options :
        y_title = y_title + ' / ' + bin_width_string
    #if unit is not None and  'no_y_bin' not in draw_options :
    #    y_title += ' ' + unit

        return y_title  

def save_plot(simple_plots = None, stacked_plots = None, draw_options = {}) :

    if simple_plots is None : simple_plots = []
    if stacked_plots is None : stacked_plots = []
    #  do_stacked_plots = False
    #  stacked_plots = []
    #else : do_stacked_plots = True

    _draw_options = draw_options.copy()

    if 'canvas' not in draw_options :
        canvas = rt.TCanvas( str(random()), 'Test', 200, 10, 700, 700 )
    else :
        canvas = draw_options['canvas']
    
    #canvas = rt.TCanvas( 'c1', 'Test', 200, 10, 700, 700 )
    canvas.cd()
    #canvas.SetGridy()

    #print _draw_options
    canvas.SetLeftMargin(0.15)
    #canvas. SetLeftMargin(.5)
    histList = []
    if 'y_log' in _draw_options : canvas.SetLogy()

    if 'legend_position' not in _draw_options : _draw_options['legend_position'] = (.60,.70,.89,.89)

    if 'no_legend' not in _draw_options :
        legend = rt.TLegend(_draw_options['legend_position'][0], _draw_options['legend_position'][1], _draw_options['legend_position'][2], _draw_options['legend_position'][3])
        legend.SetBorderSize(0); # //no border for legend
        legend.SetFillColor(0);
        
    if len(stacked_plots) :
        first_plot = stacked_plots[0]['p']
    if len(simple_plots) :
        first_plot = simple_plots[0]['p']

    if not isinstance(first_plot, rt.TH1) :
        print 'is MultiGraph'
        theStack = rt.TMultiGraph()
    else :
        theStack = rt.THStack('tmp', 'tmp')
    if len(simple_plots) == 0 : theStack = None     

    if not isinstance(first_plot, rt.TH1) :
        theStackStack = rt.TMultiGraph()
    else :
        theStackStack = rt.THStack('tmp2', 'tmp')
    if len(stacked_plots) == 0 : theStackStack = None
        
    #print '_draw_options', _draw_options
    if 'draw_option' not in _draw_options :
        _draw_options['draw_option'] = 'NOSTACK'
    if 'stack_draw_option' not in _draw_options :
        _draw_options['stack_draw_option'] = 'HIST'

    for i in range(0, len(simple_plots)) :
        plot_bundle = simple_plots[i]
        h = plot_bundle['p']
        if 'rebin' in _draw_options :
            h.Rebin(_draw_options['rebin'])
        h.Draw()
        plot_draw_options = plot_bundle['draw_options']
        if 'color' in plot_draw_options :
            h.SetLineColor(plot_draw_options['color'])
            h.SetFillColor(plot_draw_options['color'])
            h.SetMarkerColor(plot_draw_options['color'])
        h.SetLineWidth(2)
        if 'MarkerStyle' in plot_draw_options :
            h.SetMarkerStyle(plot_draw_options['MarkerStyle'])
        if 'no_legend' not in _draw_options :
            legend_title = plot_draw_options['legend_title']
            if not 'legend_supress_counts' in  _draw_options :
                legend_title += ' ({:.0f}'.format(h.Integral()) + ' events)'
            legend.AddEntry(h, legend_title, "LP")
        theStack.Add(h)
        
    for i in range(0, len(stacked_plots)) :
        plot_bundle = stacked_plots[i]
        h = plot_bundle['p']
        h.Draw()
        if 'rebin' in _draw_options :
            h.Rebin(_draw_options['rebin'])
        plot_draw_options = plot_bundle['draw_options']
        if 'color' in plot_draw_options :
            h.SetLineColor(plot_draw_options['color'])
            h.SetFillColor(plot_draw_options['color'])
            h.SetMarkerColor(plot_draw_options['color'])
        if 'fill_color' in plot_draw_options :
            h.SetFillColor(plot_draw_options['fill_color'])
        if 'line_color' in plot_draw_options :
            h.SetLineColor(plot_draw_options['line_color'])

        h.SetLineWidth(2)
        if 'MarkerStyle' in plot_draw_options :
            h.SetMarkerStyle(plot_draw_options['MarkerStyle'])

        if 'no_legend' not in _draw_options :
            legend_title = plot_draw_options['legend_title']
            if not 'legend_supress_counts' in  _draw_options :
                legend_title += ' ({:.2f}'.format(h.Integral()) + ' events)'
            legend.AddEntry(h, legend_title, "FP")           
        theStackStack.Add(h)
        
    if 'x_title' not in _draw_options :
        _draw_options['x_title'] = first_plot.GetXaxis().GetTitle()
        
    if ('y_title' not in _draw_options) or (not 'no_y_bin' in _draw_options) :
        _draw_options['y_title'] = get_y_title(first_plot, _draw_options) #yTitle = y_title, unit = _draw_options['y_unit'])

    if 'per_bin_norm' in _draw_options :
        plots = []
        for i in range(0, len(simple_plots)) :
            plots.append(simple_plots[i]['p'])
        norm_per_bin(plots)

    if 'cumulative' in _draw_options :
        for i in range(0, len(simple_plots)) :
            simple_plots[i]['p'] = simple_plots[i]['p'].GetCumulative(_draw_options['cumulative'])
        
    if theStack is not None :
        theStack.Draw("NOSTACK")
        theStack.GetXaxis().SetTitle(_draw_options['x_title'])
        theStack.GetYaxis().SetTitle(_draw_options['y_title'])
        theStack.GetYaxis().SetTitleOffset(1.7)

    if theStackStack is not None :
        theStackStack.Draw("STACK")
        if len(stacked_plots) > 0 :
            theStackStack.GetXaxis().SetTitle(_draw_options['x_title'])
            theStackStack.GetYaxis().SetTitle(_draw_options['y_title'])
            theStackStack.GetYaxis().SetTitleOffset(1.7)  
        
    if 'y_min' in _draw_options :
        if theStack is not None : theStack.SetMinimum(_draw_options['y_min'])
        if theStackStack is not None : theStackStack.SetMinimum(_draw_options['y_min'])

    if 'y_max' in _draw_options :
        if theStack is not None : theStack.SetMaximum(_draw_options['y_max'])
        if theStackStack is not None : theStackStack.SetMaximum(_draw_options['y_max'])
    else :
        if theStack is not None : theStack.Draw("NOSTACK")
        canvas.Update();
        stack_y_max = rt.gPad.GetUymax();
        
        if theStackStack is not None : theStackStack.Draw("")
        canvas.Update();
        stackstack_y_max = rt.gPad.GetUymax();

        y_max = max(stack_y_max, stackstack_y_max)
        # print 'y_max ', y_max
        if theStackStack is not None : theStackStack.SetMaximum(y_max)
        if theStack is not None : theStack.SetMaximum(y_max)

    if 'range' in draw_options :
        if theStackStack is not None : theStackStack.GetXaxis().SetRangeUser(draw_options['range'][0], draw_options['range'][1])
        if theStack is not None : theStack.GetXaxis().SetRangeUser(draw_options['range'][0], draw_options['range'][1])

    if theStackStack is not None :
        theStackStack.Draw(_draw_options['stack_draw_option'])
    
    if theStack is not None :
        same_string = 'SAME'
        if theStackStack is None : same_string = ''
        
        #print 'theStack.Draw ',_draw_options['draw_option']
        theStack.Draw(_draw_options['draw_option'] + 'NOSTACK' + same_string)
    else :
        theStack.Draw(_draw_options['draw_option'])

    if 'no_legend' not in _draw_options :
        legend.Draw("SAME")
        
    if 'paves' in _draw_options :
        for pave in _draw_options['paves'] :
            #print 'Preparing pave', pave['text']
            aPave = rt.TPaveText(pave['pos'][0],pave['pos'][1], pave['pos'][2], pave['pos'][3], "blNDC")
            aPave.SetFillStyle(0)
            aPave.SetBorderSize(0)
            aPave.Draw()
            aPave.AddText(pave['text'])
            aPave.Draw()
    canvas.Update()

    save_name = 'blubb'
    if 'save_name' in _draw_options :
        save_name = _draw_options['_draw_options']
        save_folder = save_name[:save_name.rfind('/')]
        save_file_name = save_name[save_name.rfind('/'):]

        subfolderName = outputFolderName + '//' + 'new_save/' + save_folder

        if not os.path.exists(subfolderName):
            os.makedirs(subfolderName)

        for fileFormat in savedFileFormats :
            canvas.Print(subfolderName + '//' + save_file_name + fileFormat)

    #theStack.Draw("NOSTACK"), _draw_options
    if 'do_not_draw_canvas' not in _draw_options :
        canvas.Draw()
    return theStack, legend  
