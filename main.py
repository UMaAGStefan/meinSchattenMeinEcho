# This is a sample Python script.
import pandas as pd
import geopandas
import time
import shadow
import noise

def main():
    fileName = r"C:\Users\sb.umaag\OneDrive - Umwelt Management AG UMaAG\Dokumente\GitHub\meinSchattenMeinEcho\example\yyyymmdd_EINGANG_meinSchattenMeinEcho_Projekt.xlsx"
    crsInp = 'EPSG:25832'
    #df_wea = pd.read_excel(fileName,sheet_name='WEA',usecols=['User label', 'Object type', 'Ost ', 'Nord ', 'Z', 'Object description','Hub height', 'NachtBetrieb'])
    df_wea = pd.read_excel(fileName,sheet_name='WEA')
    df_wea = df_wea[df_wea['Object type'] != 0]
    df_wea.loc[df_wea['Object type']=='New','Object type']= 'Neue WEA'
    gdf_wea = geopandas.GeoDataFrame(df_wea.drop(columns=['Ost ', 'Nord ']),
                                    geometry=geopandas.points_from_xy(df_wea['Ost '],df_wea['Nord ']),
                                     crs=crsInp)
    df_io = pd.read_excel(fileName,sheet_name='Schall',usecols=['IRW', 'Description', 'Ost ', 'Nord ', 'Z', 'User label'])
    df_sr = pd.read_excel(fileName,sheet_name='Schatten')
    gdf_sr = geopandas.GeoDataFrame(df_sr.drop(columns=['Ost ', 'Nord ']),
                                    geometry=geopandas.points_from_xy(df_sr['Ost '], df_sr['Nord ']),
                                    crs=crsInp)
    outfile = fileName.replace('.xlsx','_Outfile.xlsx')
    gdf_wea.to_excel(outfile,index=None,sheet_name='WEA Eingangsdaten')

    # # # # # # SHADOW # # # # # # #
    ## gdf_srVB, gdf_srZB, gdf_srGB = shadow.shadowFlicker(gdf_wea,gdf_sr,outfile)
    # # # # # # NOISE # # # # # # #
    # Einfaches Schallkonzept - die lauteste WEA wir reduziert
    df_io, df_wea = noise.schallKonzeptFortePiano(df_wea,df_io,fileName)
    # Alle Varianten von +/-1Mode werden getestet. Das mit der höchsten gesamt kW Leistung wird ausgewählt
    # df_wea = noise.ExtraRundeSchallModes(df_wea,df_io,fileName)
    # Berechnung der Schallwerte mit Bewertung an den jeweiligen IOs mit einem Schallkonzept
    df_io = noise.calcAndEvaluateNoise(df_wea,df_io,outfile)

if __name__ == "__main__":
    main()