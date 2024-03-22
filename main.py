# This is a sample Python script.
import pandas as pd
import geopandas
import time
import shadow
import noise

def main():
    # EINGABE der Eingangsdatei
    fileName = r"example\240322_EINGANG_meinSchattenMeinEcho_Example.xlsx"
    # EINGABE des Verwendeten Koordinatensystems
    crsInp = 'EPSG:25832'
    #df_wea = pd.read_excel(fileName,sheet_name='WEA',usecols=['User label', 'Object type', 'Ost ', 'Nord ', 'Z', 'Object description','Hub height', 'NachtBetrieb'])
    df_wea = pd.read_excel(fileName,sheet_name='WEA')
    # Anpassung der ausgelesenen Eingangsdaten auf die Spaltennamen die später verwendet werden
    df_wea = df_wea[df_wea['Object type'] != 0]
    df_wea.loc[df_wea['Object type']=='New','Object type']= 'Neue WEA'
    df_wea.loc[df_wea['Object type']=='Exist','Object type']= 'Existierende WEA'
    gdf_wea = geopandas.GeoDataFrame(df_wea.drop(columns=['Ost ', 'Nord ']),
                                    geometry=geopandas.points_from_xy(df_wea['Ost '],df_wea['Nord ']),
                                     crs=crsInp)
    outfile = fileName.replace('.xlsx','_Outfile.xlsx')
    gdf_wea.to_excel(outfile,index=None,sheet_name='WEA Eingangsdaten')

    # # # # # # SHADOW # # # # # # #
    df_sr = pd.read_excel(fileName, sheet_name='Schatten')
    gdf_sr = geopandas.GeoDataFrame(df_sr.drop(columns=['Ost ', 'Nord ']),
                                    geometry=geopandas.points_from_xy(df_sr['Ost '], df_sr['Nord ']),
                                    crs=crsInp)
    gdf_srVB, gdf_srZB, gdf_srGB = shadow.shadowFlicker(gdf_wea,gdf_sr,outfile)
    # # # # # # NOISE # # # # # # #
    # Einlesen der Schall IOs
    df_io = pd.read_excel(fileName, sheet_name='Schall',
                          usecols=['IRW', 'Description', 'Ost ', 'Nord ', 'Z', 'User label'])
    # Einfaches Schallkonzept - die Lauteste WEA wird reduziert
    df_io, df_wea = noise.schallKonzeptFortePiano(df_wea,df_io,fileName)
    # Alle Varianten von +/-1Mode werden getestet. Die Variante mit der höchsten gesamt kW Leistung wird ausgewählt
    df_wea = noise.ExtraRundeSchallModes(df_wea,df_io,fileName,outfile)
    # Berechnung der Schallwerte mit Bewertung an den jeweiligen IOs mit einem Schallkonzept
    df_io = noise.calcAndEvaluateNoise(df_wea,df_io,outfile)

if __name__ == "__main__":
    main()