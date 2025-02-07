import pandas as pd
import numpy as np
from itertools import product
import time
def calcVBZB(df_wea,df_io,ind):
    """
    Berechnung der Schallpegel der WEA an dem IO
    Berechnung erfolgt nach Interimsverfahren oder bei Schallquellen kleiner 60m nach dem Alternativen Verfahren
    (Hinweise zum Schallimmissionsschutz bei Windkraftanlagen (WKA) Stand 30.06.2016)
    """
    df_calcs = pd.DataFrame(columns=['ZB', 'VB', 'L WEA', 'D', 'A', 'Adiv', 'Aatm', 'Agr', 'Abar', 'Cmet','Dc'])
    df_calcs['D']=(((df_wea.loc[:,'Ost ']-df_io.loc[ind,'Ost '])**2+
                         (df_wea.loc[:,'Nord ']-df_io.loc[ind,'Nord '])**2+
                         (df_io.loc[ind,'Z']-df_wea.loc[:,'Z']+df_wea.loc[:,'Hub height'])**2)**(1/2)).astype('float')
    df_calcs['Adiv'] = 20*np.log10(df_calcs['D']/1)+11
    df_calcs['Aatm'] =df_wea['LatDW']-\
                (10*np.log10(10**((df_wea[63].astype(float)-(0.1*df_calcs['D']/1000))/10)+10**((df_wea[125].astype(float)-(0.4*df_calcs['D']/1000))/10)+
                           10**((df_wea[250].astype(float)-(1*df_calcs['D']/1000))/10)+10**((df_wea[500].astype(float)-(1.9*df_calcs['D']/1000))/10)+
                           10**((df_wea[1000].astype(float)-(3.7*df_calcs['D']/1000))/10)+10**((df_wea[2000].astype(float)-(9.7*df_calcs['D']/1000))/10)+
                           10**((df_wea[4000].astype(float)-(32.8*df_calcs['D']/1000))/10)+10**((df_wea[8000].astype(float)-(117*df_calcs['D']/1000))/10)))
    df_calcs['Agr'] = -3.0
    df_calcs['Dc'] = 0.0
    df_calcs['Abar'] = 0
    df_calcs['Cmet'] = 0
    # Alternatives Verfahren für alle WEA mit NH kleiner 60m  annahme mittlerer Schallweg über Grund 30m ohne Orographie
    for wea_ind in df_wea[df_wea['Hub height']<=60].index:
        df_calcs.loc[wea_ind,'Aatm'] = df_wea.loc[wea_ind,'LatDW'] - \
                                       10*np.log10(10**((df_wea.loc[wea_ind,'LatDW']-
                                                         (1.9*df_calcs.loc[wea_ind,'D']/1000))/10))
        df_calcs.loc[wea_ind, 'Agr'] = np.max([0,(4.8-
                                                  (2*(df_wea.loc[wea_ind,'Hub height']+5)/2/df_calcs.loc[wea_ind,'D'])*
                                                  (17+300/df_calcs.loc[wea_ind,'D']))])
        df_calcs.loc[wea_ind, 'Dc'] = 10*np.log10(1+
                                                  (df_calcs.loc[wea_ind,'D']**2+(5-df_wea.loc[wea_ind,'Hub height'])**2)/
                                        max(df_calcs.loc[wea_ind,'D']**2+(5+df_wea.loc[wea_ind,'Hub height'])**2, 1e-10))

    df_calcs['A'] = (df_calcs.loc[:,'Adiv':'Cmet']).sum(axis=1)
    df_calcs['L WEA'] = df_wea['LatDW']-df_calcs['A']+df_calcs['Dc']+df_wea['deltaL']
    df_calcs['Object type']=df_wea['Object type']
    WeaVB = -100
    GewVB = -100
    ZB = -100
    if len(df_calcs.loc[df_calcs['Object type']=='Existierende WEA','L WEA'])>0:
        WeaVB = 10*np.log10((10**(df_calcs.loc[df_calcs['Object type']=='Existierende WEA','L WEA']/10)).sum(axis=0))
    if len(df_calcs.loc[df_calcs['Object type']=='Gewerbliche Vorbelastung','L WEA'])>0:
        GewVB = 10*np.log10((10**(df_calcs.loc[df_calcs['Object type']=='Gewerbliche Vorbelastung','L WEA']/10)).sum(axis=0))
    if len(df_calcs.loc[df_calcs['Object type']=='Neue WEA','L WEA'])>0:
        ZB = 10*np.log10((10**(df_calcs.loc[df_calcs['Object type']=='Neue WEA','L WEA']/10)).sum(axis=0))
    return WeaVB, GewVB,\
           ZB,\
            df_calcs# VB,ZB


def calcAndEvaluateNoise(df_wea,df_io,outfile=None,IrrelevanzZusatzbelstung=6,EinwirkbereichEinzelbeitrag=12,
                         zulaessigeUeberschreitungBeiVB=1):
    """
    Bewertung des Berechneten Pegel am den IOs
    :param EinwirkbereichEinzelbeitrag: Definition des Abstand zwische IRW und Pegel am IO der noch als
        Beitrag berücksichtig wird.
    :param zulaessigeUeberschreitungBeiVB: Definition der zulässigen Überschreitung wenn ein Vorbelastung vorhanden ist
    :return:
    """
    # Falls kein Oktavband angegeben wird das LAI Oktavband verwendet
    if len(df_wea[abs(df_wea['LatDW'] - 10 * np.log10((10 ** (df_wea.loc[:, 63:8000] / 10)).sum(axis=1)))>1])>0:
        for ind_wea in df_wea[abs(df_wea['LatDW'] - 10 * np.log10((10 ** (df_wea.loc[:, 63:8000] / 10)).sum(axis=1)))>1].index:
            if (df_wea.loc[ind_wea,'Object type']=='Neue WEA') or\
                (df_wea.loc[ind_wea, 'Object type'] == 'Existierende WEA'):
                df_wea.loc[ind_wea, 63:8000] = df_wea.loc[ind_wea, 'LatDW']+[-20.3,-11.9,-7.7,-5.5,-6.0,-8.0,-12.0,-20.0]
            else:
                df_wea.loc[ind_wea, 500] = df_wea.loc[ind_wea, 'LatDW']
    df_wea.loc[df_wea['deltaL']!=df_wea['deltaL'],'deltaL']=0
    # Alle IOs werden einzelns betrachet
    for ind_io in df_io.index:
        df_io.loc[ind_io, 'WeaVB'],df_io.loc[ind_io, 'GewVB'], df_io.loc[ind_io, 'ZB'], df_calcs = calcVBZB(df_wea, df_io, ind_io)
        df_io.loc[ind_io, 'VB'] = 10 * np.log10((10 ** (df_io.loc[ind_io, ['WeaVB', 'GewVB']] / 10)).sum().astype(float))
        df_io.loc[ind_io, 'GB'] = 10 * np.log10((10 ** (df_io.loc[ind_io, ['VB', 'ZB']] / 10)).sum().astype(float))
        # Bewertung
        if df_io.loc[ind_io, 'ZB'] <= df_io.loc[ind_io, 'IRW']-IrrelevanzZusatzbelstung:
            df_io.loc[ind_io, 'Bewertung'] = 'Einwirkbereich Zusatzbelastung  ' + str(IrrelevanzZusatzbelstung) + 'dB unter IRW'
        elif round(df_io.loc[ind_io, 'GB']) <= df_io.loc[ind_io, 'IRW']:
            df_io.loc[ind_io, 'Bewertung'] = 'GB kleiner IRW'
        elif round(df_io.loc[ind_io, 'GB'] - zulaessigeUeberschreitungBeiVB) <= df_io.loc[ind_io, 'IRW'] and round(df_io.loc[ind_io, 'VB'] + EinwirkbereichEinzelbeitrag) >= df_io.loc[ind_io, 'IRW']:
            df_io.loc[ind_io, 'Bewertung'] = 'GB '+str(zulaessigeUeberschreitungBeiVB)+'dB über IRW'
        elif all(df_calcs.loc[df_calcs['Object type'] == 'Neue WEA', 'L WEA'] <= df_io.loc[ind_io, 'IRW']-EinwirkbereichEinzelbeitrag):
            df_io.loc[ind_io, 'Bewertung'] = f'Einzelbeitrag {EinwirkbereichEinzelbeitrag}dB unter IRW'
        else:
            df_io.loc[ind_io, 'Bewertung'] = 'Nicht ok'
    # Ergebnis
    df_wea.name = 'Windkraftanlagen'
    df_io.name = 'Bewertung Schall Immissionsorte'
    if outfile!=None:
        with pd.ExcelWriter(outfile, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            for df in [df_wea, df_io]:
                sheet = writer.sheets['Noise'] if 'Noise' in writer.sheets else None
                if sheet is None:
                    # Das Tabellenblatt existiert noch nicht, erstellen Sie es
                    df.to_excel(writer, sheet_name='Noise', index=None,startrow=1)
                    sheet = writer.sheets['Noise']
                else:
                    # Das Tabellenblatt existiert bereits, fügen Sie die Daten darunter hinzu
                    sheet.append([])
                    sheet.append([df.name])  # Fügen Sie die Überschrift in eine neue Zeile ein
                    df.to_excel(writer, sheet_name='Noise', index=None,
                                 startrow=sheet.max_row)
    return df_io

def schallKonzeptFortePiano(df_wea,df_io, fileName,IrrelevanzZusatzbelstung=6,EinwirkbereichEinzelbeitrag=12,
                         zulaessigeUeberschreitungBeiVB=1):
    """
    Die Lauteste Anlage wird reduziert bis die Bewertung in Ordnung ist.
    """
    print('Starte Schallkonzept FortePiano')
    start_time_FP = time.time()
    df_inp = pd.read_excel(fileName, sheet_name='WEASchallDaten', header=None, index_col=0)
    # Füllen mit Oktavband Daten mit maximal möglichen Schallmode
    for ind in df_wea[df_wea['NachtBetrieb'].isnull()].index:
        start_index = df_inp.index.get_loc(df_wea.loc[ind, 'Object description'])
        df_wea.loc[ind, 'NachtBetrieb'] = df_inp.iloc[start_index + 1, :10].name
        df_wea.loc[ind, 63:'deltaL'] = df_inp.iloc[start_index + 1, :10].values
        df_wea.loc[ind, 'NB kW'] = df_inp.iloc[start_index + 1, -1]
    df_io = calcAndEvaluateNoise(df_wea, df_io,outfile=None,
                                 IrrelevanzZusatzbelstung=IrrelevanzZusatzbelstung,
                                 EinwirkbereichEinzelbeitrag=EinwirkbereichEinzelbeitrag,
                                zulaessigeUeberschreitungBeiVB=zulaessigeUeberschreitungBeiVB)
    df_io['Abstand ZB IRW'] = df_io['ZB'] - df_io['IRW']
    # # Solange die Bewertung nicht ok ist wird eine Anlage reduziert, außer die Anlage ich bereits auf dem letzten Mode
    while any(df_io['Bewertung'] == 'Nicht ok'):
        ind_io = df_io[df_io['Bewertung'] == 'Nicht ok']['Abstand ZB IRW'].nlargest(1).index.values[0]
        WeaVB, GewVB, ZB, df_calcs = calcVBZB(df_wea, df_io, ind_io)

        wea_ind = df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].nlargest(1).index.values[0]
        start_index = df_inp.index.get_loc(df_wea.loc[wea_ind, 'Object description'])
        aus_index = start_index + np.where(pd.isna(df_inp.index[start_index:]))[0][0]
        df_modes = df_inp.iloc[start_index:aus_index]
        mode_index = df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb'])
        if mode_index < aus_index - 1:
            print(f'WEA{wea_ind} {df_modes.iloc[mode_index + 1].name}')
            # Lauteste Anlage ein Mode leiser
            df_wea.loc[wea_ind, 'NachtBetrieb'] = df_modes.iloc[mode_index + 1].name
            df_wea.loc[wea_ind, 63:'deltaL'] = df_modes.iloc[mode_index + 1, :10].values
            df_wea.loc[wea_ind, 'NB kW'] = df_modes.iloc[mode_index + 1, -1]
        # Falls lauteste Anlage bereits im kleinsten Mode
        elif mode_index == aus_index - 1 and (len(df_wea['Object type'] == 'Neue WEA') > 2) and \
                df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].nlargest(2).diff().values[1] < 3:
            # zweit Lauteste WEA
            wea_ind = df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].nlargest(2).index.values[1]
            start_index = df_inp.index.get_loc(df_wea.loc[wea_ind, 'Object description'])
            aus_index = start_index + np.where(pd.isna(df_inp.index[start_index:]))[0][0]
            mode_index = df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb'])
            df_wea.loc[wea_ind, 'NachtBetrieb'] = df_modes.iloc[mode_index + 1].name
            df_wea.loc[wea_ind, 63:'deltaL'] = df_modes.iloc[mode_index + 1, :10].values
            df_wea.loc[wea_ind, 'NB kW'] = df_modes.iloc[mode_index + 1, -1]
            if mode_index < aus_index - 1:
                # zweite lauteste Anlage einen Mode leiser
                df_wea.loc[wea_ind, 'NachtBetrieb'] = df_modes.iloc[mode_index + 1].name
                df_wea.loc[wea_ind, 63:'deltaL'] = df_modes.iloc[mode_index + 1, :10].values
                df_wea.loc[wea_ind, 'NB kW'] = df_modes.iloc[mode_index + 1, -1]
            # Falls auch zweit lauteste im kleinsten Mode
            elif (mode_index == aus_index - 1) and (len(df_wea['Object type'] == 'Neue WEA') > 3) and \
                    df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].nlargest(3).diff().values[2] < 3:
                # dritte Anlage ein Mode leister
                wea_ind = df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].nlargest(3).index.values[1]
                start_index = df_inp.index.get_loc(df_wea.loc[wea_ind, 'Object description'])
                aus_index = start_index + np.where(pd.isna(df_inp.index[start_index:]))[0][0]
                mode_index = df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb'])
                df_wea.loc[wea_ind, 'NachtBetrieb'] = df_modes.iloc[mode_index + 1].name
                df_wea.loc[wea_ind, 63:'deltaL'] = df_modes.iloc[mode_index + 1, :10].values
                df_wea.loc[wea_ind, 'NB kW'] = df_modes.iloc[mode_index + 1, -1]

                if mode_index < aus_index - 1:
                    # dritt lauteste Anlage einen Mode leiser
                    df_wea.loc[wea_ind, 'NachtBetrieb'] = df_modes.iloc[mode_index + 1].name
                    df_wea.loc[wea_ind, 63:'deltaL'] = df_modes.iloc[mode_index + 1, :10].values
                    df_wea.loc[wea_ind, 'NB kW'] = df_modes.iloc[mode_index + 1, -1]
                else:
                    wea_ind = df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].idxmax()
                    df_wea.loc[wea_ind, 'NachtBetrieb'] = 'Aus'
                    df_wea.loc[wea_ind, 63:'deltaL'] = 0
                    df_wea.loc[wea_ind, 'NB kW'] = 0
            else:
                wea_ind = df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].idxmax()
                df_wea.loc[wea_ind, 'NachtBetrieb'] = 'Aus'
                df_wea.loc[wea_ind, 63:'deltaL'] = 0
                df_wea.loc[wea_ind, 'NB kW'] = 0
        else:
            wea_ind = df_calcs[df_calcs['Object type'] == 'Neue WEA']['L WEA'].idxmax()
            df_wea.loc[wea_ind, 'NachtBetrieb'] = 'Aus'
            df_wea.loc[wea_ind, 63:'deltaL'] = 0
            df_wea.loc[wea_ind, 'NB kW'] = 0
        df_io = calcAndEvaluateNoise(df_wea, df_io, outfile=None,
                                 IrrelevanzZusatzbelstung=IrrelevanzZusatzbelstung,
                                 EinwirkbereichEinzelbeitrag=EinwirkbereichEinzelbeitrag,
                                zulaessigeUeberschreitungBeiVB=zulaessigeUeberschreitungBeiVB)
        df_io['Abstand ZB IRW'] = df_io['ZB'] - df_io['IRW']
    print("--- %s seconds for Noise FortePiano ---" % (time.time() - start_time_FP))
    print(df_wea.loc[:, 'NachtBetrieb'])
    print(df_io.loc[:, 'Bewertung'])
    return df_io, df_wea

def ExtraRundeSchallModes(df_wea,df_io,fileName,outfile,IrrelevanzZusatzbelstung=6,EinwirkbereichEinzelbeitrag=12,
                         zulaessigeUeberschreitungBeiVB=1):
    print('ExtraRundeSchallVariation')
    start_time = time.time()
    # # ExtraRundeSchallModes
    # Alle Möglichen Varianten mit +/-1 Mode werden bestimmt
    df_inp = pd.read_excel(fileName, sheet_name='WEASchallDaten', header=None, index_col=0)
    df_wea_allModes = pd.DataFrame(columns=df_wea.columns[:18], index=pd.MultiIndex.from_tuples([], names=(u'WEA', u'Mode')))
    for wea_ind in df_wea.loc[df_wea['Object type'] == 'Neue WEA'].index:
        start_index = df_inp.index.get_loc(df_wea.loc[wea_ind, 'Object description'])
        aus_index = start_index + np.where(pd.isna(df_inp.index[start_index:]))[0][0]
        df_modes = df_inp.iloc[start_index+1:aus_index]
        if df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb'])==0:
            mode_index_start = 0
            mode_index_end = 2
        elif df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb'])==len(df_modes):
            mode_index_start = len(df_modes)-2
            mode_index_end = len(df_modes)
        elif df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb']) < len(df_modes)  and \
            df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb']) > 0:
            mode_index_start = df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb'])-1
            mode_index_end = df_modes.index.get_loc(df_wea.loc[wea_ind, 'NachtBetrieb'])+2
        for mode, ind_mode in zip(df_modes.iloc[mode_index_start: mode_index_end].values,
                                  df_modes.iloc[mode_index_start: mode_index_end].index):
            df_wea_allModes.loc[(df_wea.loc[wea_ind, 'User label'],ind_mode),:'Hub height']=df_wea.loc[wea_ind,:'Hub height']
            df_wea_allModes.loc[(df_wea.loc[wea_ind, 'User label'],ind_mode),'NachtBetrieb'] = ind_mode
            df_wea_allModes.loc[(df_wea.loc[wea_ind, 'User label'],ind_mode),63:'deltaL'] = mode[:10].astype(float)
            df_wea_allModes.loc[(df_wea.loc[wea_ind, 'User label'], ind_mode), 'kW'] = mode.astype(float)[10]
    data1 = pd.DataFrame(df_wea_allModes.values,
                         index=df_wea_allModes.index.map('_'.join),
                         columns=df_wea_allModes.columns)

    df_io_allModes = pd.DataFrame(index=data1.index,columns=df_io['User label'])
    # Für alle möglichen Einzelbeiträge werden die Pegel ermittelt, sowie die Vorbelastung
    for ind_io in df_io.index:
        if df_wea.loc[df_wea['Object type'] != 'Neue WEA'].empty:
            df_io.loc[ind_io, 'WeaVB']=-100
            df_io.loc[ind_io, 'GewVB']=-100
        else:
            df_io.loc[ind_io,'WeaVB'],\
            df_io.loc[ind_io, 'GewVB'] = \
                calcVBZB(df_wea.loc[df_wea['Object type'] != 'Neue WEA'], df_io,ind_io)[:2]
        df_io_allModes.iloc[:, ind_io] = calcVBZB(data1, df_io, ind_io)[3]['L WEA']

    df_io.loc[:,'VB'] = 10 * np.log10((10 ** (df_io.loc[:,['WeaVB', 'GewVB']] / 10)).sum(axis=1).astype(float))
    # Anpassung IRW nach Bewertung wenn +1 dB Möglich bei ausreichender Vorbelastung
    df_io.loc[:, 'IRW Calc'] = df_io.loc[:,'IRW']
    if not df_io[round(df_io.loc[:,'VB'])>=df_io.loc[:,'IRW']-EinwirkbereichEinzelbeitrag].empty:
        df_io.loc[round(df_io.loc[:,'VB'])>=df_io.loc[:,'IRW']-EinwirkbereichEinzelbeitrag,'IRW Calc']=\
            df_io.loc[round(df_io.loc[:,'VB'])>=df_io.loc[:,'IRW']-EinwirkbereichEinzelbeitrag,'IRW']+zulaessigeUeberschreitungBeiVB
    df_io = df_io.set_index('User label')
    # possible combinations modes**wea

    df_io_allModes_calcs = 10**(df_io_allModes/10)
    df_io_vb_calcs = 10**(df_io.loc[:,'VB']/10).values

    bestCombinations = pd.DataFrame(index=range(0,len(df_wea[df_wea['Object type'] == 'Neue WEA'])),columns=range(0,6))
    bestCombinations.loc['kW',:]=10
    df_wea.loc[df_wea['Object type']=='Neue WEA','User label'].to_list()
    prefixes = df_wea.loc[df_wea['Object type'] == 'Neue WEA', 'User label'].to_list()
    possibleCombinations = len(list(product(*[df_io_allModes[df_io_allModes.index.str.startswith(prefix)].index for prefix in prefixes])))
    print(f"Es werden {possibleCombinations} Kombinationen betrachtet")
    max_iterations = possibleCombinations
    # if possibleCombinations>max_iterations:
    #     print('Iterationen reduzieren????????')
    #     print(f"Länge des Produkts: {possibleCombinations}")
    #     max_iterations = 100000
    # Mögliche Kombinationen finden
    for i, combination in enumerate(product(*[df_io_allModes[df_io_allModes.index.str.startswith(prefix)].index for prefix in prefixes])):
        combi_ZB = 10*np.log10((df_io_allModes_calcs.loc[list(combination)]).sum(axis=0).astype(float))
        combi_GB = 10*np.log10(df_io_vb_calcs+(10**(combi_ZB/10.0)).astype(float))
        df_io.loc[:, 'Bewertung'] = 0
        # # # Irgendwie muss hier nochmal angepasst werden
        # for io_ind in df_io.index:
        #     if round(combi_GB.loc[io_ind])<=df_io.loc[io_ind,'IRW Calc']:
        #         df_io.loc[io_ind,'Bewertung'] = 1
        #     elif round(combi_ZB.loc[io_ind])<=(df_io.loc[io_ind,'IRW']-IrrelevanzZusatzbelstung):
        #         df_io.loc[io_ind, 'Bewertung'] = 1
        #     elif all(df_io_allModes.loc[list(combination),io_ind]-(df_io.loc[io_ind,'IRW']-EinwirkbereichEinzelbeitrag)>=0):
        #         df_io.loc[io_ind, 'Bewertung'] = 1
        # Prüfung Gesamtbelastung kleiner IRW, bei signifikanter Vorbelastung 1dB über IRW
        df_io.loc[df_io['IRW Calc']-round(combi_GB)>=0,'Bewertung']=1
        # df_io.loc[round(combi_GB)<=df_io['IRW Calc'].values,'Bewertung']=1
        # Prüfung Irrelevanz Zusatzbelastung
        df_io.loc[df_io['IRW']-IrrelevanzZusatzbelstung-round(combi_ZB)>=0,'Bewertung']=1
        # df_io.loc[round(combi_ZB)<=(df_io['IRW'].values-IrrelevanzZusatzbelstung),'Bewertung']=1
        # Prüfung Einwirkbereich Einzelbeitrag
        df_io.loc[(df_io_allModes.loc[list(combination)]-(df_io['IRW'].values-EinwirkbereichEinzelbeitrag)>=0).all(axis='rows'),'Bewertung']=1
        # df_io.loc[(df_io_allModes.loc[list(combination)]-df_io['IRW'].values+EinwirkbereichEinzelbeitrag>=0).all(axis='rows'),'Bewertung']=1
        if all(df_io['Bewertung']!=0):
            if data1.loc[list(combination),'kW'].sum()>bestCombinations.loc['kW'].min():
                bestCombinations.iloc[:len(bestCombinations)-1,bestCombinations.loc['kW'].idxmin()] = combination
                bestCombinations.iloc[len(bestCombinations)-1,bestCombinations.loc['kW'].idxmin()] = data1.loc[list(combination),'kW'].sum()
        # Überprüfe, ob die maximale Anzahl von Iterationen erreicht ist
        if i + 1 == max_iterations:
            print('done')
        if i%1000==0 and i>0:
            print("Fortschritt: {:.1f}% ".format(i/possibleCombinations*100)+
                  "verbleibende Dauer: {:.1f}s".format((time.time() - start_time)/(i/possibleCombinations)-(time.time() - start_time)))

    print("--- %s seconds for ExtraRundeSchallVariation---" % (time.time() - start_time))
    print(bestCombinations)
    bestCombinations['WEA Label']=df_wea['User label']
    bestCombinations['WEA Label']['kW'] = 'kW'
    bestCombinations = bestCombinations.set_index('WEA Label')

    if outfile!=None:
        with pd.ExcelWriter(outfile, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                sheet = writer.sheets['Noise'] if 'Noise' in writer.sheets else None
                if sheet is None:
                    # Das Tabellenblatt existiert noch nicht, erstellen Sie es
                    bestCombinations.to_excel(writer, sheet_name='Noise', index=True,startrow=1)
                    sheet = writer.sheets['Noise']
                    sheet['A1'] = 'Mögliche Schallkonzepte'
                else:
                    # Das Tabellenblatt existiert bereits, fügen Sie die Daten darunter hinzu
                    sheet.append([])
                    sheet.append(['Mögliche Schallkonzepte'])  # Fügen Sie die Überschrift in eine neue Zeile ein
                    bestCombinations.to_excel(writer, sheet_name='Noise', index=True,
                                 startrow=sheet.max_row)
    #combination=list(prefixes+df_wea['NachtBetrieb'])
    df_wea['NB kW'].sum()
    df_wea.loc[df_wea['Object type'] == 'Neue WEA','NachtBetrieb':'deltaL'] = \
        data1.loc[list(bestCombinations.loc[:,bestCombinations.loc['kW'].idxmax()])[:-1],'NachtBetrieb':'deltaL'].values
    df_wea.loc[df_wea['Object type'] == 'Neue WEA','NB kW'] = data1.loc[list(bestCombinations.loc[:,bestCombinations.loc['kW'].idxmax()])[:-1],'kW'].values.astype(float)
    return df_wea