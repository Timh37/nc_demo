#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 18:34:12 2023

@author: timhermans
"""
import os
import xarray as xr
import numpy as np
import xesmf as xe

path = '/Users/timhermans/Documents/Others/python_rvdw'

fingerprints = xr.open_dataset(os.path.join(path,'SeaLevel.nc')) #netcdf openen als xarray dataset (hierbij is de data gelinkt aan de coordinaten in het bestand)
gl = fingerprints.Greenland.values #zo lees je de data van een bepaalde variabele zelf uit zonder coordinaten 

print(len(fingerprints.lon)) #er zijn 360 longitude coordinaten, ze lopen van 0 tot 359



oceaan_data = np.random.random((181,361)) #random oceaan data
oceaan_da = xr.DataArray(data=oceaan_data,dims=['lat','lon'],coords=dict(lat=np.linspace(-90,90,181),lon=np.linspace(-180,180,361))) #met 361 coordinaten heb je er overigens 1 dubbel, immers -180=180

######omzetten van 0-360 naar -180-180 longitude:
  
#als oceaan data een array is kan je de kolommen simpelweg in een andere volgorde zetten, hierbij moeten we wel rekening houden met de dubbele longitude coordinaat:
oceaan_data_ = np.hstack([oceaan_data[:,180::],oceaan_data[:,1:180]])

#als het een xarray dataset is kan je de longitude coordinaat zelf aanpassen
oceaan_da_ = oceaan_da.drop_isel(lon=0) #laten we de eerste longitude coordinaat weggooien, aangezien die dubbelop is met de laatste (zie hierboven)
oceaan_da_.coords['lon'] = np.mod(oceaan_da_.coords['lon'],360) #transformeer de longitude coordinaten
oceaan_da_ = oceaan_da_.reindex({ 'lon' : np.sort(oceaan_da_['lon'])}) #sorteren van 0 tot 359
print(oceaan_da_.coords['lon']) #resultaat

print((oceaan_da_.values == oceaan_data_).all()) #controleren of allebei de manieren hetzelfde antwoord geven

######van -90-90 naar -89.5-89.5 latitude:

#ongewogen middelen kan maar is volgens mij niet correct, omdat de grootte van een gridcell varieert met latitude. Laten we het toch doen:
oceaan_data_ = (oceaan_data_[0:-1,:] + oceaan_data_[1::,:])/2

#netter zou zijn om het met een methode naar keuze te interpoleren (regridden), bijv:
regridder = xe.Regridder(oceaan_da_,fingerprints,method='bilinear',periodic=True)
regridded_oceaan_da = regridder(oceaan_da_)

#je ziet dat dit een warning geeft, waarom? omdat de latitude coordinaten een dubbele coordinaat bevatten, immers -90 = 90
regridder = xe.Regridder(oceaan_da_.drop_sel(lat=90),fingerprints,method='bilinear',periodic=True)
regridded_oceaan_da = regridder(oceaan_da_.drop_sel(lat=90))
#^dit werkt beter


######een paar voorbeeldjes hoe te werken met xarray
fingerprints.sel(lat=81.5)#selecteren van een bepaald punt
fingerprints.isel(lat=5)

fingerprints.Glaciers.plot() #simpel figuur maken