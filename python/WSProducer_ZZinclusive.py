"""
WSProducer.py
Workspace producers using coffea.
"""
from coffea.hist import Hist, Bin, export1d
from coffea.processor import ProcessorABC, LazyDataFrame, dict_accumulator
from uproot3 import recreate
import awkward as ak
import numpy as np
import awkward
import yaml

#from tensorflow import keras
#from keras import backend as K
#from keras.layers import Input,InputLayer, Activation, Dense, Dropout, BatchNormalization, Lambda
#from keras.models import Sequential, Model, clone_model
#from keras.optimizers import SGD, Adam, Adadelta, Adagrad

class WSProducer(ProcessorABC):
    """
    A coffea Processor which produces a workspace.
    This applies selections and produces histograms from kinematics.
    """

    histograms = NotImplemented
    selection = NotImplemented

    def __init__(self, isMC, era=2017, sample="DY", do_syst=False, syst_var='', weight_syst=False, haddFileName=None, flag=False):
        self._flag = flag
        self.do_syst = do_syst
        self.era = era
        self.isMC = isMC
        self.sample = sample
        self.syst_var, self.syst_suffix = (syst_var, '_sys_{}'.format(syst_var)) if do_syst and syst_var else ('', '')
        self.weight_syst = weight_syst
        self._accumulator = dict_accumulator({
            name: Hist('Events', Bin(name=name, **axis))
            for name, axis in ((self.naming_schema(hist['name'], region), hist['axis'])
                               for _, hist in list(self.histograms.items())
                               for region in hist['region'])
        })
        self.outfile = haddFileName

    def __repr__(self):
        return "{}(era: {}, isMC: {}, sample: {}, do_syst: {}, syst_var: {}, weight_syst: {}, output: {})".format(self.__class__.__name__, self.era, self.isMC, self.sample, self.do_syst, self.syst_var, self.weight_syst, self.outfile)

    @property
    def accumulator(self):
        return self._accumulator
#    def absolute_BinaryCrossentropy (self,y_true, y_pred, weights): 
#        error = K.abs(K.sum(weights*(K.maximum(y_pred,0) - y_pred*y_true + K.log(1+K.exp(-1*K.abs(y_pred)))),axis=-1))
#        return error

#    def custom_relu(self,X):
#        return K.maximum(K.minimum(X,100-3*X),0)

#    def get_models(self):
#        NINPUT_3J = 27
#        NINPUT_2J = 22
#
#        print('====================')
#        print('loading models...')
#        print('====================')
#
#        nn_input_3J = Input((NINPUT_3J,))
#        y_true_3J = Input((1,),name='y_true_3J')
#        weights_3J = Input((1,), name='weights_3J')
#
#        nn_input_2J = Input((NINPUT_2J,))
#        y_true_2J = Input((1,),name='y_true_2J')
#        weights_2J = Input((1,), name='weights_2J')
#
#        h_3J = BatchNormalization()(nn_input_3J)
#        X_3J = Dense((200), name='hidden_1')(h_3J)
#        h_3J = Lambda(self.custom_relu, name='custom_relu')(X_3J)
#        (out_z_3J)=Dense((1), name='out_z_3J')(h_3J)
#        out_3J = Activation('sigmoid',name='out_3J')(out_z_3J)
#
#        h_2J = BatchNormalization()(nn_input_2J)
#        X_2J = Dense((100), name='hidden_12')(h_2J)
#        h_2J = Lambda(self.custom_relu, name='custom_relu2')(X_2J)
#        (out_z_2J) = Dense((1), name='out_z_2J')(h_2J)
#        out_2J = Activation('sigmoid',name='out_2J')(out_z_2J)
#
#        model_3J = Model(inputs=[nn_input_3J, weights_3J, y_true_3J], outputs=out_3J)
#        model_2J = Model(inputs=[nn_input_2J, weights_2J, y_true_2J], outputs=out_2J)
#
#        model_3J.add_loss(self.absolute_BinaryCrossentropy(y_true_3J, out_z_3J, weights_3J))
#        model_2J.add_loss(self.absolute_BinaryCrossentropy(y_true_2J, out_z_2J, weights_2J))
#
#        optim_3J = Adam(lr = 0.001)
#        optim_2J = Adam(lr = 0.001)
#
#        model_3J.compile(optimizer=optim_3J, loss=None, weighted_metrics=['accuracy'])
#        model_2J.compile(optimizer=optim_2J, loss=None, weighted_metrics=['accuracy'])
#
#        return model_3J, model_2J

    def process(self, df, *args):
        output = self.accumulator.identity()

        weight = self.weighting(df)
        # NN scores (array)
#        nn_score_2J,nn_score_3J = self.get_nn_scores(df)
#        case_2J=df['ngood_jets'] == 2
#        case_3J=df['ngood_jets'] >=3
#        nn_score=[-1]*len(case_2J)
#        for i in range(len(case_2J)):
#            if case_2J[i]:
#                nn_score[i]=nn_score_2J[i][0]
#            elif case_3J[i]:
#                nn_score[i]=nn_score_3J[i][0]
#        df['nnscore']=nn_score

        for h, hist in list(self.histograms.items()):
            for region in hist['region']:
                name = self.naming_schema(hist['name'], region)
                selec = self.passbut(df, hist['target'], region)
                output[name].fill(**{
                    'weight': weight[selec],
                    name: awkward.flatten(df[hist['target']][selec],axis=0)
                })

        return output

    def postprocess(self, accumulator):
        return accumulator

    def passbut(self, event, excut, cat):
        excut =str(excut)
        cat =str(cat)
        """Backwards-compatible passbut."""
        return eval('&'.join('(' + cut.format(sys=('' if self.weight_syst else self.syst_suffix)) + ')'
                             for cut in self.selection[cat] if excut not in cut))

    
class MonoZ(WSProducer):
    histograms = {
        'h_bal': {
            'target': 'sca_balance',
            'name': 'balance',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'sca_balance', 'n_or_arr': 100, 'lo': 0, 'hi': 2}
        },
        'h_phi': {
            'target': 'delta_phi_ZMet',
            'name': 'phizmet',
            'region': ['signal','catSignal-0jet','catSignal-1jet','catNRB','catTOP','catDY','cat3L','catWW','catEM','cat4Jet'],
            'axis': {'label': 'delta_phi_ZMet','n_or_arr': 16,'lo': -3.2, 'hi': 3.2}
        },
        'h_njet': {
            'target': 'ngood_jets',
            'name': 'njet',
            'region': ['catDY','signal'],
            'axis': {'label': 'ngood_jets', 'n_or_arr': 6, 'lo': 0, 'hi': 6}
        },

        'h_dijet_abs_dEta': {
            'target': 'dijet_abs_dEta',
            'name': 'dijet_abs_dEta',
            'region': ['signal','catSignal-0jet','catSignal-1jet','catNRB','catTOP','catDY','cat3L','catWW','catEM','cat4Jet'],
            'axis': {'label':  'dijet_abs_dEta' , 'n_or_arr':20, 'lo':0, 'hi':10}
        }, 
        
#        'h_dijet_Mjj': {
#            'target': 'dijet_Mjj',
#            'name': 'dijet_Mjj',
#            'region': ['signal','catNRB','catTOP','catDY','cat3L','catWW','catEM'],
#            'axis': {'label': 'dijet_Mjj', 'n_or_arr':15, 'lo':0, 'hi':1500}
#       }, 
        'h_measMET': {
            'target': 'met_pt',
            'name': 'measMET',
            'region': ['signal','catSignal-0jet','catSignal-1jet','catNRB','catTOP','catDY','cat3L','catWW','catEM','cat4Jet'],
            'axis': {'label': 'met_pt','n_or_arr': [50, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 1000]}
        },
        'h_emuMET': {
            'target': 'emulatedMET',
            'name': 'measMET',
            'region': ['cat3L','signal','catSignal-0jet','catSignal-1jet',
                       'catWW',
                       'catEM','cat4Jet'],
            'axis': {'label': 'emulated_met_pt','n_or_arr': [50, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 1000]}
        },
        'h_mT': {
            'target': 'MT',
            'name': 'measMT',
            'region': ['signal','catSignal-0jet','catSignal-1jet','cat3L','catNRB','catTOP','catDY','catEM','catWW','cat4Jet'],
            'axis': {'label': 'MET','n_or_arr': [0, 100, 200, 250, 300, 350, 400, 500, 600, 700, 800, 1000, 1200, 2000]}
        },
        'h_emu_mT': {
            'target': 'MT',
            'name': 'emuMT',
            'region': ['signal','catSignal-0jet','catSignal-1jet',
                       'catNRB','catTOP','catDY',
                       'cat3L',
                       'catWW',
                       'catEM','cat4Jet'],
            'axis': {'label': 'emulated_MT','n_or_arr': [0, 100, 200, 250, 300, 350, 400, 500, 600, 700, 800, 1000, 1200, 2000]}
        },
        'h_Z_pt': {
            'target': 'Z_pt',
            'name': 'Z_pt',
            'region': ['catNRB','catTOP','catDY',
                       'signal','catSignal-0jet','catSignal-1jet',
                       'catEM',
                       'cat3L','catWW','cat4Jet'],
            'axis': {'label': 'Z_pt','n_or_arr': 20, 'lo':0, 'hi':1000}
        },
        'h_Z_mass': {
            'target': 'Z_mass',
            'name': 'Z_mass',
            'region': ['catNRB','catTOP','catDY',
                       'signal','catSignal-0jet','catSignal-1jet',
                       'catEM',
                       'cat3L','catWW','cat4Jet'],
            'axis': {'label': 'Z_mass','n_or_arr': 80, 'lo':50, 'hi':130}
        },
#        'h_nnscore' : {
#            'target': 'nnscore',
#            'name': 'nnscore',
#            'region': ['signal','catNRB','catTOP','catDY','cat3L','catWW','catEM'],
#            'axis': {'label': 'nnscore','n_or_arr':60, 'lo':-1, 'hi':1}
#        },

    }

    selection = {
            "signal" : [
                "(event.lep_category{sys} == 1) | (event.lep_category{sys} == 3)",
                "event.Z_pt{sys}        >  45" ,
                "abs(event.Z_mass{sys} - 91.1876) < 15",
                "event.ngood_jets{sys}  <= 1" ,
                "event.ngood_bjets{sys} ==  0" ,
#                "event.nhad_taus{sys}   ==  0" ,
                "event.met_pt{sys}      >  70" ,
                "(event.met_pt{sys}/event.Z_pt{sys})>0.4",
                "(event.met_pt{sys}/event.Z_pt{sys})<1.8",
                "abs(event.delta_phi_ZMet{sys} ) > 0.5",
            ],
            "cat4Jet" : [
                "(event.lep_category{sys} == 1) | (event.lep_category{sys} == 3)",
                "event.Z_pt{sys}        >  45" ,
                "abs(event.Z_mass{sys} - 91.1876) < 15",
                "event.ngood_jets{sys}  >= 4" ,
                "event.ngood_bjets{sys} ==  0" ,
#                "event.nhad_taus{sys}   ==  0" ,
                "event.met_pt{sys}      >  70" ,
                "(event.met_pt{sys}/event.Z_pt{sys})>0.4",
                "(event.met_pt{sys}/event.Z_pt{sys})<1.8",
                "abs(event.delta_phi_ZMet{sys} ) > 0.5",
            ],
            "catSignal-0jet": [
                "event.ngood_jets{sys} == 0",
                "self.passbut(event, excut, 'signal')",
            ],
            "catSignal-1jet": [
                "event.ngood_jets{sys} == 1",
                "self.passbut(event, excut, 'signal')",
            ],
            "catDY" : [
                "(event.lep_category{sys} == 1) | (event.lep_category{sys} == 3)",
                "event.Z_pt{sys}        >  60" ,
                "abs(event.Z_mass{sys} - 91.1876) < 15",
                "event.ngood_jets{sys}   <= 1" ,
                "event.ngood_bjets{sys} ==  0" ,
                "event.nhad_taus{sys}   ==  0" ,
                "event.met_pt{sys}      >  50" ,
                "event.met_pt{sys}      <  100" ,
                "abs(event.delta_phi_ZMet{sys} ) < 0.5",
                "abs(1 - event.sca_balance{sys}) < 0.4",
                "abs(event.delta_phi_j_met{sys}) > 0.5",
                "event.delta_R_ll{sys}           < 1.8"
            ],
            "cat3L": [
                "(event.lep_category{sys} == 4) | (event.lep_category{sys} == 5)",
                "event.Z_pt{sys}        >  30" ,
                "abs(event.Z_mass{sys} - 91.1876) < 15",
                "event.ngood_jets{sys}  <=  1" ,
                "event.ngood_bjets{sys} ==  0" ,
                "event.met_pt{sys}      >  70" ,
#                "event.mass_alllep{sys} > 100" ,
                "abs(1 -event.emulatedMET{sys}/event.Z_pt{sys}) < 0.4"
#                "abs(event.emulatedMET_phi{sys} - event.Z_phi{sys}) > 2.6"
            ],
#            "cat4L": [
#                "(event.lep_category{sys} == 6) | (event.lep_category{sys} == 7)",
#                "event.Z_pt{sys}        >  60" ,
#                "abs(event.Z_mass{sys} - 91.1876) < 35",
#                "event.ngood_jets{sys}  >=  2" ,
#		        "abs(event.emulatedMET_phi{sys} - event.Z_phi{sys}) > 2.6",
#            ],
            "catNRB": [
                "event.lep_category{sys} == 2",
                "event.Z_pt{sys}        >  45" ,
                "abs(event.Z_mass{sys} - 91.1876) < 15",
                "event.ngood_jets{sys}   <= 1" ,
                "event.ngood_bjets{sys} ==  0" ,
                "event.met_pt{sys}      >  70"
            ],
            "catTOP": [
                "event.lep_category{sys} == 2",
                "event.Z_pt{sys}        >  30" ,
                "((event.Z_mass > 40) & (event.Z_mass < 70)) | ((event.Z_mass > 110) & (event.Z_mass < 200))",
#                "abs(event.Z_mass{sys} - 91.1876) < 15",
                "event.ngood_jets{sys}  >   2" ,
                "event.ngood_bjets{sys} >=  1" ,
                "event.met_pt{sys}      >  70"
            ],
            "catWW": [
                "event.lep_category{sys} ==2",
                "event.Z_pt{sys} > 45", 
                "((event.Z_mass > 40) & (event.Z_mass < 70)) | ((event.Z_mass > 110) & (event.Z_mass < 200))",
                "event.ngood_jets{sys}  <= 1",
                "event.ngood_bjets{sys} == 0",
                "event.met_pt{sys}       >70",
                "abs(event.delta_phi_ZMet{sys} ) > 0.5",
                "(event.met_pt{sys}/event.Z_pt{sys})>0.4",
                "(event.met_pt{sys}/event.Z_pt{sys})<1.8"
            ],
            "catEM": [
                "event.lep_category{sys} == 2",
                "self.passbut(event, excut, 'catNRB')"
            ],

        }

#    def get_nn_scores(self, event):
#        feature_2j = ['lep_category','ngood_bjets','lead_jet_pt','trail_jet_pt','leading_lep_pt','trailing_lep_pt','lead_jet_eta','trail_jet_eta','leading_lep_eta','trailing_lep_eta','lead_jet_phi','trail_jet_phi','leading_lep_phi','trailing_lep_phi','met_pt','met_phi','delta_phi_j_met','delta_phi_ZMet','Z_mass','dijet_Mjj','dijet_abs_dEta']
#        feature_3j = ['lep_category','ngood_jets','ngood_bjets','lead_jet_pt','trail_jet_pt','third_jet_pt','leading_lep_pt','trailing_lep_pt','lead_jet_eta','trail_jet_eta','third_jet_eta','leading_lep_eta','trailing_lep_eta','lead_jet_phi','trail_jet_phi','third_jet_phi','leading_lep_phi','trailing_lep_phi','met_pt','met_phi','delta_phi_j_met','delta_phi_ZMet','Z_mass','dijet_Mjj','dijet_abs_dEta']
#        # hard coded
#        year = self.era
#
#        model_3J, model_2J = self.get_models()
#
#        model_2J.load_weights('exactly2Jets.h5')
#        model_3J.load_weights('atLeast3Jets.h5')
#
#        df_2J = event[feature_2j]
#        df_2J = ak.to_pandas(df_2J)
#        df_2J['dilep_abs_dEta'] = abs(df_2J['leading_lep_eta']- df_2J['trailing_lep_eta'])
#        df_2J['year'] = year
#        df_2J = df_2J[['lep_category','ngood_bjets','lead_jet_pt','trail_jet_pt','leading_lep_pt','trailing_lep_pt','lead_jet_eta','trail_jet_eta','leading_lep_eta','trailing_lep_eta','lead_jet_phi','trail_jet_phi','leading_lep_phi','trailing_lep_phi','met_pt','met_phi','delta_phi_j_met','delta_phi_ZMet','Z_mass','dijet_Mjj','dijet_abs_dEta','year']]
#        df_2J['filler_weight'] = -1
#        df_2J['filler_target'] = -1
#
#        input_2J = df_2J.to_numpy()
#
#        nn_input_1_2J = input_2J[:,0:22]
#        nn_input_2_2J = input_2J[:,22]
#        nn_input_3_2J = input_2J[:,23]
#
#        nn_score_2J = model_2J.predict([nn_input_1_2J,nn_input_2_2J,nn_input_3_2J])
#
#        df_3J = event[feature_3j]
#        df_3J = ak.to_pandas(df_3J)
#        df_3J['year'] = year
#        df_3J['dilep_abs_dEta'] = abs(df_3J['leading_lep_eta']- df_3J['trailing_lep_eta'])
#        df_3J = df_3J[['lep_category','ngood_jets','ngood_bjets','lead_jet_pt','trail_jet_pt','third_jet_pt','leading_lep_pt','trailing_lep_pt','lead_jet_eta','trail_jet_eta','third_jet_eta','leading_lep_eta','trailing_lep_eta','lead_jet_phi','trail_jet_phi','third_jet_phi','leading_lep_phi','trailing_lep_phi','met_pt','met_phi','delta_phi_j_met','delta_phi_ZMet','Z_mass','dijet_Mjj','dijet_abs_dEta','dilep_abs_dEta','year']]
#        df_3J['filler_weight'] = -1
#        df_3J['filler_target'] = -1
#
#        input_3J = df_3J.to_numpy()
#
#        nn_input_1_3J = input_3J[:,0:27]
#        nn_input_2_3J = input_3J[:,27]
#        nn_input_3_3J = input_3J[:,28]
#
#        nn_score_3J = model_3J.predict([nn_input_1_3J,nn_input_2_3J,nn_input_3_3J])
#        return nn_score_2J, nn_score_3J


    def weighting(self, event):
        weight = 1.0
#        with open("./xsections_{}.yaml".format(self.era), 'r') as stream:
#            xsections = yaml.safe_load(stream)
#        oldweight= event.xsecscale[0]
#        if self.isMC:
#            weightfixfactor=xsections[self.sample]['xsec']/oldweight
#            weight = event.xsecscale*weightfixfactor
#            print(weight)
#        else:
        try:
            weight = event.xsecscale
#            print(weight)
        except:
            return "ERROR: weight branch doesn't exist"

        if self.isMC:
            try:
                if "ADD" in self.syst_suffix:
                    weight = weight*event.ADDWeight #for ADD samples only (EFT weights)
            except:
                pass
            # weight *= event.genWeight
            if "puWeight" in self.syst_suffix:
                if "Up" in self.syst_suffix:
                    weight = weight*event.puWeightUp
                else:
                    weight = weight*event.puWeightDown
            else:
            	weight = weight*event.puWeight
            # Electroweak
            try:
                if "EWK" in self.syst_suffix:
                    if "Up" in self.syst_suffix:
                        weight = weight*event.kEWUp
                    else:
                        weight = weight*event.kEWDown
                else:
                    weight = weight*event.kEW
            except:
                pass
            # NNLO crrection
            try:
                weight = weight*event.kNNLO
            except:
                pass
            # PDF uncertainty
            if "PDF" in self.syst_suffix:
                try:
                    if "Up" in self.syst_suffix:
                        weight = weight*event.pdfw_Up
                    else:
                        weight = weight*event.pdfw_Down
                except:
                    pass
            # QCD Scale weights
            if "QCDScale0" in self.syst_suffix:
                try:
                    if "Up" in self.syst_suffix:
                        weight = weight*event.QCDScale0wUp
                    else:
                        weight = weight*event.QCDScale0wDown
                except:
                    pass
            if "QCDScale1" in self.syst_suffix:
                try:
                    if "Up" in self.syst_suffix:
                        weight = weight*event.QCDScale1wUp
                    else:
                        weight = weight*event.QCDScale1wDown
                except:
                    pass
            if "QCDScale2" in self.syst_suffix:
                try:
                    if "Up" in self.syst_suffix:
                        weight = weight*event.QCDScale2wUp
                    else:
                        weight = weight*event.QCDScale2wDown
                except:
                    pass                
            #Muon SF    
            if "MuonSF" in self.syst_suffix:
                if "Up" in self.syst_suffix:
                    weight = weight*event.w_muon_SFUp
                else:
                    weight = weight*event.w_muon_SFDown
            else:
                weight = weight*event.w_muon_SF
            # Electron SF
            if "ElecronSF" in self.syst_suffix:
                if "Up" in self.syst_suffix:
                    weight = weight*event.w_electron_SFUp
                else:
                    weight = weight*event.w_electron_SFDown
            else:
                weight = weight*event.w_electron_SF
	    #Prefire Weight
            try:
                if "PrefireWeight" in self.syst_suffix:
                    if "Up" in self.syst_suffix:
                        weight = weight*event.PrefireWeight_Up
                    else:
                        weight = weight*event.PrefireWeight_Down
                else:
                    weight = weight*event.PrefireWeight
            except:
                pass
            #nvtx Weight (replaced by PhiXY corrections)
            #if "nvtxWeight" in self.syst_suffix:
            #    if "Up" in self.syst_suffix:
            #        weight *= event.nvtxWeightUp
            #    else:
            #        weight *= event.nvtxWeightDown
            #else:
            #    weight *= event.nvtxWeight

            #TriggerSFWeight
            if "TriggerSFWeight" in self.syst_suffix:
                if "Up" in self.syst_suffix:
                    weight = weight*event.TriggerSFWeightUp
                else:
                    weight = weight*event.TriggerSFWeightDown
            else:
                weight = weight*event.TriggerSFWeight
            #BTagEventWeight
#            if "btagEventWeight" in self.syst_suffix:
#                if "Up" in self.syst_suffix:
#                    weight = weight*event.btagEventWeightUp
#                else:
#                    weight = weight*event.btagEventWeightDown
#            else:
#                weight = weight*event.btagEventWeight

        return weight

    def naming_schema(self, name, region):
        return "{}_{}_{}{}".format(name,self.sample,region,self.syst_suffix)
