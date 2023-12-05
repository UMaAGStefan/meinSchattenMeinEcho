import pandas as pd
import numpy as np


def calcVBZB(df_wea,df_io,ind):
    df_calcs = pd.DataFrame(columns=['ZB', 'VB', 'L WEA', 'D', 'A', 'Adiv', 'Aatm', 'Agr', 'Abar', 'Cmet','Dc'])
    df_calcs['D']=(((df_wea.loc[:,'Ost ']-df_io.loc[ind,'Ost '])**2+
                         (df_wea.loc[:,'Nord ']-df_io.loc[ind,'Nord '])**2+
                         (df_io.loc[ind,'Z']-df_wea.loc[:,'Z']+df_wea.loc[:,'Hub height'])**2)**(1/2)).astype('float')
    df_calcs['Adiv'] = 20*np.log10(df_calcs['D']/1)+11
    df_calcs['Aatm'] =df_wea['LatDW']-\
                (10*np.log10(10**((df_wea[63]-(0.1*df_calcs['D']/1000))/10)+10**((df_wea[125]-(0.4*df_calcs['D']/1000))/10)+
                           10**((df_wea[250]-(1*df_calcs['D']/1000))/10)+10**((df_wea[500]-(1.9*df_calcs['D']/1000))/10)+
                           10**((df_wea[1000]-(3.7*df_calcs['D']/1000))/10)+10**((df_wea[2000]-(9.7*df_calcs['D']/1000))/10)+
                           10**((df_wea[4000]-(32.8*df_calcs['D']/1000))/10)+10**((df_wea[8000]-(117*df_calcs['D']/1000))/10)))
    df_calcs['Agr'] = -3.0
    df_calcs['Dc'] = 0.0
    df_calcs['Abar'] = 0
    df_calcs['Cmet'] = 0
    for wea_ind in df_wea[df_wea['Hub height']<=50].index:
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
    WeaVB = 0
    GewVB = 0
    if len(df_calcs.loc[df_calcs['Object type']=='Existierende WEA','L WEA'])>0:
        WeaVB = 10*np.log10((10**(df_calcs.loc[df_calcs['Object type']=='Existierende WEA','L WEA']/10)).sum(axis=0))
    if len(df_calcs.loc[df_calcs['Object type']=='Gewerbliche Vorbelastung','L WEA'])>0:
        GewVB = 10*np.log10((10**(df_calcs.loc[df_calcs['Object type']=='Gewerbliche Vorbelastung','L WEA']/10)).sum(axis=0))

    return WeaVB, GewVB,\
           10*np.log10((10**(df_calcs.loc[df_calcs['Object type']=='Neue WEA','L WEA']/10)).sum(axis=0)),\
            df_calcs# VB,ZB

def calcAndEvaluateNoise(df_wea,df_io,outfile):
    # Falls kein Oktavband angegeben wird das LAI Oktavband verwendet
    if len(df_wea[df_wea['LatDW'] != 10 * np.log10((10 ** (df_wea.loc[:, 63:8000] / 10)).sum(axis=1))])>0:
        for ind_wea in df_wea[df_wea['LatDW'] != 10 * np.log10((10 ** (df_wea.loc[:, 63:8000] / 10)).sum(axis=1))].index:
            if (df_wea.loc[ind_wea,'Object type']=='Neue WEA') or\
                (df_wea.loc[ind_wea, 'Object type'] == 'Existierende WEA'):
                df_wea.loc[ind_wea, 63:8000] = df_wea.loc[ind_wea, 'LatDW']+[-20.3,-11.9,-7.7,-5.5,-6.0,-8.0,-12.0,-20.0]
            else:
                df_wea.loc[ind_wea, 500] = df_wea.loc[ind_wea, 'LatDW']
    df_wea.loc[df_wea['deltaL']!=df_wea['deltaL'],'deltaL']=0
    for ind_io in df_io.index:
        df_io.loc[ind_io, 'WeaVB'],df_io.loc[ind_io, 'GewVB'], df_io.loc[ind_io, 'ZB'], df_calcs = calcVBZB(df_wea, df_io, ind_io)
        df_io['VB'] = 10 * np.log10((10 ** (df_io[['WeaVB', 'GewVB']] / 10)).sum(axis=1))
        df_io['GB'] = 10 * np.log10((10 ** (df_io[['VB', 'ZB']] / 10)).sum(axis=1))
        # df_io.loc[df_io['Abstand IRW']>0,'Bewertung'] = 'Not'
        if df_io.loc[ind_io, 'ZB'] + 10 < df_io.loc[ind_io, 'IRW']:
            df_io.loc[ind_io, 'Bewertung'] = 'Einwirkbereich'
        elif df_io.loc[ind_io, 'GB'] - 0.45 < df_io.loc[ind_io, 'IRW']:
            df_io.loc[ind_io, 'Bewertung'] = 'GB kleiner IRW'
        elif df_io.loc[ind_io, 'GB'] - 1.45 < df_io.loc[ind_io, 'IRW'] and df_io.loc[ind_io, 'VB'] + 10 > df_io.loc[
            ind_io, 'IRW']:
            df_io.loc[ind_io, 'Bewertung'] = 'GB 1dB über IRW'
        elif all(df_calcs.loc[df_calcs['Object type'] == 'Neue WEA', 'L WEA'] + 10 < df_io.loc[ind_io, 'IRW']):
            df_io.loc[ind_io, 'Bewertung'] = 'Einzelbeitrag 10dB unter IRW'
        else:
            df_io.loc[ind_io, 'Bewertung'] = 'Nicht ok'
    df_wea.name = 'Windkraftanlagen'
    df_io.name = 'Bewertung Schall Immissionsorte'
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