from plot_tools import *

def make_ZpX_OS(selection, hist_name, proc_options) :
    tree = proc_options['tree']
    proc_postfix = proc_options['proc_postfix']
    directory = proc_options ['directory']
    mc = proc_options['BKG_ZZ_correction']

    #print '%s/%s_2P2F_%s'%(selection, selection, hist_name)
    p_2P2F_SR = get_plot('%s%s_BKG_AllData_%s.root'%(directory, tree, proc_postfix), '%s/%s_2P2Fw_%s'%(selection, selection, hist_name))
    #return {}
    p_3P1F_SR = get_plot('%s%s_BKG_AllData_%s.root'%(directory, tree, proc_postfix), '%s/%s_3P1Fw_%s'%(selection, selection, hist_name))
    p_ZZ_3P1F_SR = get_plot('%s%s_BKG_%s_%s.root'%(directory, tree, mc, proc_postfix), '%s/%s_3P1Fw_%s'%(selection, selection, hist_name))
    
    p_3P1F_final = p_3P1F_SR.Clone()
    #print '3P1F before ZZ removal: ', p_3P1F_final.Integral()
    p_3P1F_final.Add(p_ZZ_3P1F_SR, -1.)
    #print '3P1F after ZZ removal: ', p_3P1F_final.Integral()
    p_3P1F_final.Add(p_2P2F_SR, -2.)
    #print 'Final 3P1F : ', p_3P1F_final.Integral()

    p_BKG_total = p_2P2F_SR.Clone()
    
    #print 'Final 3P1F after negative bin removal: ', p_3P1F_final.Integral()
    #print 'FInal 2P2F above 300 GeV: ',p_2P2F_SR.Integral(, ) 
    p_BKG_total.Add(p_3P1F_final, 1.)
    
    return {'p_2P2F_SR' : p_2P2F_SR ,
            'p_3P1F_SR' : p_3P1F_SR,
            'p_3P1F_final' : p_3P1F_final,
            'p_ZZ_3P1F_SR': p_ZZ_3P1F_SR,
            'p_BKG_total' : p_BKG_total,
           }

def make_ZpX_ZZMass(parametrization, binning = [100, 70, 1000]) :
    res = ROOT.TH1F('ZpX', '', binning[0], binning[1], binning[2])
    
    for param in parametrization :
        curr = ROOT.TH1F('ZpX_curr', '', binning[0], binning[1], binning[2])
        c_norm = param['norm']
        tf = ROOT.TF1("ZpX_curr", "landau(0)*(1 + exp( pol1(3))) + [5]*(TMath::Landau(x, [6], [7]))", 70, 1000)
        tf.SetParameters(4.404e-05,151.2,36.6,7.06,-0.00497,0.01446,157.3,26.00)
        plot_ratio = tf.Integral(binning[1], binning[2]) / tf.Integral(70, 1000)
        print 'plot_ratio ', plot_ratio
        curr.FillRandom('ZpX_curr', 100000)
        curr.Scale(c_norm * plot_ratio / curr.Integral())
        
        res.Add(curr)
        
    return res
