# This is a sample Python script.
import pandas as pd
import geopandas
import time
import shadow
import noise
start_time_all = time.time()
fileName = r"C:\Users\sb.umaag\OneDrive - Umwelt Management AG UMaAG\Dokumente\WindPRO Data\Projects\BWE Ringversuch\2023 Schall und Schattenringversuch\BWE_RV-Schall+Schatten_Eingangsdaten_angepasst_UMasEcho.xlsx"
crsInp = 'EPSG:25832'
#df_wea = pd.read_excel(fileName,sheet_name='WEA',usecols=['User label', 'Object type', 'Ost ', 'Nord ', 'Z', 'Object description','Hub height', 'NachtBetrieb'])
df_wea = pd.read_excel(fileName,sheet_name='WEA')
gdf_wea = geopandas.GeoDataFrame(df_wea.drop(columns=['Ost ', 'Nord ']),
                                geometry=geopandas.points_from_xy(df_wea['Ost '],df_wea['Nord ']),
                                 crs=crsInp)

df_io = pd.read_excel(fileName,sheet_name='Schall',usecols=['IRW', 'Description', 'Ost ', 'Nord ', 'Z', 'User label'])
df_sr = pd.read_excel(fileName,sheet_name='Schatten')
gdf_sr = geopandas.GeoDataFrame(df_sr.drop(columns=['Ost ', 'Nord ']),
                                geometry=geopandas.points_from_xy(df_sr['Ost '], df_sr['Nord ']),
                                crs=crsInp)
outfile = fileName.replace('.xlsx','Outfile.xlsx')
gdf_wea.to_excel(outfile,index=None,sheet_name='WEA Eingangsdaten')

# # # # # # SHADOW # # # # # # #
gdf_srVB, gdf_srZB, gdf_srGB = shadow.shadowFlicker(gdf_wea,gdf_sr,outfile)
# # # # # # NOISE # # # # # # #
df_io = noise.calcAndEvaluateNoise(df_wea,df_io,outfile)

print('done')


