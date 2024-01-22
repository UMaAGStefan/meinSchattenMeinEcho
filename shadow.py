import pytz
from pvlib.location import Location
import numpy as np
import time
import pandas as pd
import geopandas
import os



# Es noch zu ergänzen Prüfen
# - Anpassung auf Fläche und nicht nur Punkt als SR
# - Ergebniss
# - Horizon
# - astronmisch wahrscheinliche Beschattung


def shadowAssessement(gdf_wea, gdf_sr):
    start_time_all = time.time()
    sunDistance = 149597870000
    sunDiameter = 1392680000
    sunAlpha = np.degrees(np.arctan((sunDiameter/sunDistance)))
    siteName = 'Default'
    # # "...\Normen Richtlinien\Schall\shadowRangeCalculation.pdf"
    #gdf_wea.loc[:,'Beschattungsbereich']=((5*sunDistance*gdf_wea.loc[:,'BladeWidthAvg']/1097780000)**2-gdf_wea.loc[:,'Hub height']**2)**(1/2)
    #gdf_wea['Z']=determineStandardParameter.getZValue(gdf_wea)
    #gdf_sr['Z']=determineStandardParameter.getZValue(gdf_sr)
    #gdf_sr['Z']+gdf_sr['Height Above Ground']

    gdf_sr['Schattenstunden/Jahr [h]'] = None
    gdf_sr['Schattenstunden/Jahr [h:m]'] = None
    gdf_sr['Schattentag/Jahr [d]'] = None
    gdf_sr['Max. Schattendauer/Tag [min]'] = None
    SRheight = gdf_sr['Height Above Ground'].mean()
    latitude = gdf_sr.to_crs("EPSG:4326").geometry.y.mean()
    longitude = gdf_sr.to_crs("EPSG:4326").geometry.x.mean()
    altitude = gdf_sr.Z.mean()+SRheight
    site = Location(latitude, longitude, pytz.timezone('UTC'), altitude, siteName)
    sun = site.get_solarposition(pd.date_range("2023-01-01", periods=8760 * 60, freq="1min"))
    # sun['datetime']=sun.index
    sun['datetime Berlin'] = pd.DataFrame(sun.index, index=sun.index)[0].dt.tz_localize('UTC').dt.tz_convert(
        'Europe/Berlin')
    sun = sun.query('apparent_elevation > 3')
    for x in gdf_wea.index:
        sun.loc[:,'shadow'+str(x)]=None
    for srInd in gdf_sr.index:
        start_time = time.time()
        #print(srInd)
        # # # # # # Zusätzliche Genauigkeit für Sonnengang Rezeptor spezifisch
        # latitude = gdf_sr.to_crs("EPSG:4326").geometry.y[srInd]
        # longitude = gdf_sr.to_crs("EPSG:4326").geometry.x[srInd]
        # altitude = gdf_sr.Z[srInd]
        # site = Location(latitude, longitude, pytz.timezone('UTC'), gdf_sr.Z[srInd], siteName)
        # sun = site.get_solarposition(pd.date_range("2023-01-01", periods=8760 * 60, freq="1min"))
        # # sun['datetime']=sun.index
        # sun['datetime Berlin'] = pd.DataFrame(sun.index, index=sun.index)[0].dt.tz_localize('UTC').dt.tz_convert(
        #     'Europe/Berlin')
        sun.loc[:,sun.columns[sun.columns.str.startswith('shadow')]] = 0
        #weaInd = gdf_wea.index[0]
        for weaInd in gdf_wea.index:
            # # # # check der Sichtbarkeit
            # profile = geopandas.GeoDataFrame(geometry=
            #                        geopandas.points_from_xy(np.linspace(gdf_sr.loc[srInd,'geometry'].x,gdf_wea.loc[weaInd,'geometry'].x,1000),
            #                             np.linspace(gdf_sr.loc[srInd,'geometry'].y,gdf_wea.loc[weaInd,'geometry'].y,1000)),
            #                             crs=gdf_wea.crs)
            #
            # profile['Z']=determineStandardParameter.getZValue(profile)
            # profile['Distance']=profile.distance(gdf_sr.loc[srInd,'geometry'])
            # profile['Sichtbarkeit'] = np.linspace(profile['Z'][0],profile['Z'][profile.index[-1]]+
            #                                       gdf_wea.loc[weaInd,'Hub height']+0.5*gdf_wea.loc[weaInd,'Rotor diameter']
            #                                       ,len(profile))

            ## check if turbine is visible
            #profile[profile['Sichtbarkeit']<profile['Z']+2]

            wtAzimuthSr = np.degrees(np.arctan2((gdf_wea.loc[weaInd,'geometry'].x-gdf_sr.loc[srInd,'geometry'].x),
                                  (gdf_wea.loc[weaInd,'geometry'].y-gdf_sr.loc[srInd,'geometry'].y)))%360
            distanceToSr = gdf_wea.loc[weaInd,'geometry'].distance(gdf_sr.loc[srInd,'geometry'])

            # # # Anpassung auf H.D. Freund?
            # H.D. Freund, Die Reichweite des Schattenwurfs von Windkraftanlagen 1999 filetype:pdf
            # # Beschattungsbereich ???????????????
            #sunDiaAtRotor = np.tan(np.deg2rad(sunAlpha))*distanceToSr
            #(bladeWidthAvg/0.2)/np.tan(np.deg2rad(sunAlpha))
            if (distanceToSr < gdf_wea.loc[weaInd,'Beschattungsbereich']) & (distanceToSr<2500):
                # Anpassung nach 20% Bedeckung d ?????????????
                shadowRotorRadius=gdf_wea.loc[weaInd,'Rotor diameter']*0.5*1
                startfilter_time = time.time()

                azimuthRDWidth = np.degrees(np.arctan2(shadowRotorRadius, distanceToSr))
                azimuthRange = np.linspace(wtAzimuthSr-azimuthRDWidth,wtAzimuthSr+azimuthRDWidth,31)
                RDSize =(shadowRotorRadius**2-abs(distanceToSr * np.sin(np.deg2rad(wtAzimuthSr - azimuthRange)))**2)**(1/2)
                azimuthSectionWidth = np.diff(azimuthRange).mean()*0.5
                #azimuth = azimuthRange[0]

                for azimuth, RDSizeSection in zip(azimuthRange,RDSize):
                    elevationAngleIoToWtTipUp = np.degrees(np.arctan((
                                                                gdf_wea.loc[weaInd,'Z']
                                                                - (gdf_sr.loc[srInd,'Z']+gdf_sr.loc[srInd,'Height Above Ground'])
                                                                + RDSizeSection
                                                                + gdf_wea.loc[weaInd,'Hub height'])
                                                                /distanceToSr))

                    elevationAngleIoToWtTipDown = np.degrees(np.arctan((gdf_wea.loc[weaInd,'Z']
                                                                - (gdf_sr.loc[srInd,'Z']+gdf_sr.loc[srInd,'Height Above Ground'])
                                                                - RDSizeSection
                                                                + gdf_wea.loc[weaInd,'Hub height'])
                                                                / distanceToSr))
                    # Wenn mit Fensterausrichtung gearbeitet Wird
                    if ('Shadow Angle' in gdf_sr.columns) and \
                        str(gdf_sr.loc[srInd,'Shadow Angle']).isnumeric() and \
                        gdf_sr.loc[srInd,'Shadow Angle'].between(0,360):
                        #startsrInd=0
                        startSRFace = ((gdf_sr.loc[srInd, 'Shadow Angle'] + 180) % 360 - 90) % 360
                        # end
                        endSRFace = ((gdf_sr.loc[srInd, 'Shadow Angle'] + 180) % 360 + 90) % 360
                        if startSRFace<endSRFace:
                            queryFilterSRFace = '(azimuth > {} & azimuth < {})'.format(startSRFace, endSRFace)
                        else:
                            queryFilterSRFace = '(azimuth > {} | azimuth < {})'.format(startSRFace, endSRFace)
                        if (azimuth-azimuthSectionWidth)%360<(azimuth+azimuthSectionWidth)%360:
                            queryFilterSRazimuth = ' & (azimuth > {} & azimuth < {})'.format((azimuth - azimuthSectionWidth)%360,
                                                                                        (azimuth + azimuthSectionWidth)%360)
                        else:
                            queryFilterSRazimuth = ' & (azimuth > {} | azimuth < {})'.format((azimuth - azimuthSectionWidth)%360,
                                                                                        (azimuth + azimuthSectionWidth)%360)
                        sun.loc[sun.query(queryFilterSRFace +\
                                          queryFilterSRazimuth +\
                                          ' & (apparent_elevation.between({},{}))'.format(elevationAngleIoToWtTipDown,
                                                                                          elevationAngleIoToWtTipUp) +\
                                          ' & (apparent_elevation > 3)').index, 'shadow' + str(weaInd)] = 1
                    # Gewächshaus Modus
                    else:
                        if (azimuth-azimuthSectionWidth)%360<(azimuth+azimuthSectionWidth)%360:
                            queryFilterSRazimuth = '(azimuth > {} & azimuth < {})'.format((azimuth - azimuthSectionWidth)%360,
                                                                                        (azimuth + azimuthSectionWidth)%360)
                        else:
                            queryFilterSRazimuth = '(azimuth > {} | azimuth < {})'.format((azimuth - azimuthSectionWidth)%360,
                                                                                        (azimuth + azimuthSectionWidth)%360)
                        sun.loc[sun.query(queryFilterSRazimuth +\
                                          ' & (apparent_elevation.between({},{}))'.format(elevationAngleIoToWtTipDown,
                                                                                          elevationAngleIoToWtTipUp) +\
                                          ' & (apparent_elevation > 3)').index, 'shadow' + str(weaInd)] = 1
                              #' and azimuth.between({},{})'.format(azimuth-azimuthSectionWidth,azimuth+azimuthSectionWidth))
                    #if azimuth irgendwo um 0 bzw 360 andasdasdas
#                    azimuth = 0

                    # Check
                    # Kann die Sonne ins Fenster scheinen?
                    # Übereinstimmung Azimuth zur Anlage
                    # Übereinstimmung Elevation Angle zur Anlage
                    # Ist es Tag
                    # sun.loc[(sun.azimuth<=azimuth+azimuthSectionWidth)&
                    #                       (sun.azimuth>=azimuth-azimuthSectionWidth)&
                    #                         (sun['apparent_elevation']<=elevationAngleIoToWtTipUp)&
                    #                         (sun['apparent_elevation']>=elevationAngleIoToWtTipDown)&
                    #                         (sun['apparent_elevation']>3),'shadow'+str(weaInd)]=1
                    #print('%s %s %s %s' % (azimuth+azimuthSectionWidth,azimuth-azimuthSectionWidth,elevationAngleIoToWtTipUp,elevationAngleIoToWtTipDown))
                    #print('%s ' % (RDSizeSection))

                #print("--- %s seconds to calc Filter --" % (time.time() - startfilter_time))
        shadowTimesAtSr = sun.loc[sun.loc[:,sun.columns[sun.columns.str.startswith('shadow')][0]:].any(axis=1),'datetime Berlin'].to_frame()
        if len(shadowTimesAtSr)>0:
            shadowTimesAtSr['shadow'] = 1
            gdf_sr.loc[srInd,'Schattenstunden/Jahr [h]'] = shadowTimesAtSr.groupby(pd.Grouper(freq='D'))['shadow'].sum().sum()/60
            '{:.0f}:{:.0f}'.format(1.111,1213.12)
            gdf_sr.loc[srInd,'Schattenstunden/Jahr [h:m]'] = \
                '{:.0f}:{:.0f}'.format(np.floor(shadowTimesAtSr.groupby(pd.Grouper(freq='D'))['shadow'].sum().sum()/60),
                                       np.round((shadowTimesAtSr.groupby(pd.Grouper(freq='D'))['shadow'].sum().sum() / 60)%1*60))
            gdf_sr.loc[srInd,'Schattentag/Jahr [d]'] = sum(shadowTimesAtSr.groupby(pd.Grouper(freq='D'))['shadow'].sum() > 0)
            gdf_sr.loc[srInd,'Max. Schattendauer/Tag [min]'] = max(shadowTimesAtSr.groupby(pd.Grouper(freq='D'))['shadow'].sum())
            #print(gdf_sr.loc[srInd, 'Schattenstunden/Jahr [h]'])
        else:
            gdf_sr.loc[srInd, 'Schattenstunden/Jahr [h]'] = 0
            gdf_sr.loc[srInd, 'Schattenstunden/Jahr [h:m]'] = '0:0'
            gdf_sr.loc[srInd, 'Schattentag/Jahr [d]'] = 0
            gdf_sr.loc[srInd, 'Max. Schattendauer/Tag [min]'] = 0
        print("--- %s seconds to calc IO %s---" % (time.time() - start_time, srInd))
        del shadowTimesAtSr

    # res = shadowtime.groupby(pd.Grouper(freq='D'))['shadow'].sum()
    # print(max(res))
    # print(shadowtime.groupby(pd.Grouper(freq='M'))['shadow'].sum())
    # print(shadowtime['shadow'].sum()/60)
        #(sun['apparent_elevation']>elevationAngleIoToWtTipDown[weaInd])]
        #(sun['apparent_elevation']>7.5)]
    # sun['apparent_elevation']

    print(gdf_sr.loc[:,'Max. Schattendauer/Tag [min]'])
    print(gdf_sr.loc[:,'Schattentag/Jahr [d]'])
    print(gdf_sr.loc[:,'Schattenstunden/Jahr [h]'])
    print(gdf_sr.loc[:, 'Schattenstunden/Jahr [h:m]'])
    #gdf_sr.to_excel(r'shadow_out.xlsx')
    print("--- %s seconds to calc all---" % (time.time() - start_time_all))
    # https://help.emd.dk/mediawiki/index.php/Schattenreichweite_Hintergrund

    # Surface net solar radiation from ERA5
    # # https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview
    # # # shadow time berechnen Richtung des Rotorsbestimmen
    # # # azimult und elevation angle des Rotors bestimmen
    # bedeckter Himmel
    # Windrichtung
    return gdf_sr



def shadowFlicker(gdf_wea,gdf_sr,outfile):
    # # Windturbine Data
    #WTGDataPath = r'WTGDATAIMPORT??????'
    # # # # # # SHADOW # # # # # # #
    gdf_wea.loc[:, 'BladeWidthAvg'] = 1 / 2 * (gdf_wea.loc[:, 'BladeWidthMax'] + gdf_wea.loc[:, 'BladeWidthat90%R'])
    sunDistance = 149597870000
    sunDiameter = 1392680000
    sunAlpha = np.degrees(np.arctan((sunDiameter/sunDistance)))
    siteName = 'Default'
    # # "...\Normen Richtlinien\Schall\c6-UK_WindPRO3.6-Environment.pdf"
    gdf_wea.loc[:,'Beschattungsbereich']=((5*sunDistance*gdf_wea.loc[:,'BladeWidthAvg']/1097780000)**2-gdf_wea.loc[:,'Hub height']**2)**(1/2)

    gdf_sr.loc[:,:'geometry']
    gdf_srGB = shadowAssessement(gdf_wea[(gdf_wea['Object type'] == 'Neue WEA') | (gdf_wea['Object type'] == 'Existierende WEA')], gdf_sr.loc[:,:'geometry'])
    if gdf_wea[gdf_wea['Object type'] == 'Existierende WEA'].empty:
        gdf_srVB = pd.DataFrame()
    else:
       gdf_srVB = shadowAssessement(gdf_wea[gdf_wea['Object type'] == 'Existierende WEA'], gdf_sr.loc[:,:'geometry'])

    gdf_srZB = shadowAssessement(gdf_wea[gdf_wea['Object type'] == 'Neue WEA'], gdf_sr.loc[:,:'geometry'])
    # ExcelWriter
    gdf_wea.name = 'Windkraftanlage'
    gdf_srVB.name = 'Vorbelastung'
    gdf_srZB.name = 'Zusatzbelastung'
    gdf_srGB.name = 'Gesamtbelastung'
    with pd.ExcelWriter(outfile, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        for gdf in [gdf_wea, gdf_srVB, gdf_srZB, gdf_srGB]:
            sheet = writer.sheets['Shadow'] if 'Shadow' in writer.sheets else None

            if sheet is None:
                # Das Tabellenblatt existiert noch nicht, erstellen Sie es

                gdf.to_excel(writer, sheet_name='Shadow', index=None,startrow=1)
                sheet = writer.sheets['Shadow']
            else:
                # Das Tabellenblatt existiert bereits, fügen Sie die Daten darunter hinzu
                sheet.append([])
                sheet.append([gdf.name])  # Fügen Sie die Überschrift in eine neue Zeile ein
                gdf.to_excel(writer, sheet_name='Shadow', index=None,
                             startrow=sheet.max_row)

    print('Done')
    print(gdf_wea['Beschattungsbereich'])
    print(gdf_srVB)
    print(gdf_srZB)
    print(gdf_srGB)
    return gdf_srVB, gdf_srZB, gdf_srGB

