import arcpy
import os
"""
This example Python script runs a model and publishes the result to ArcGIS Server as a geoprocessing service.

The script first makes some feature layers and runs the Extract Data Task model from the Server Tools toolbox.
If the feature layer location isn't registered with ArcGIS Server, the script calls arcpy.AddDataStoreItem to register the database or folder.
Next, the script invokes arcpy.CreateGPSDDraft to create a service definition (SD) draft file from the model result.

If no errors are found after analyzing the SD draft, the script moves ahead with publishing the service.
"""

connPath = "c:/gis/conections/myServer.ags"
sddraft = "c:/gis/gp/drafts/ExtractionDraft.sddraft"
sd = "c:/gis/gp/sd/AnalysisDraft.sd"
serviceName = "DataExtractor"
arcpy.env.workspace = "c:/gis/citydata"

# create layers which will be available as input
arcpy.MakeFeatureLayer_management('Wiarton.gdb/places/Cityhall', 'CityHall')
arcpy.MakeFeatureLayer_management('Wiarton.gdb/places/Airport', 'Airport')
arcpy.MakeFeatureLayer_management('Wiarton.gdb/places/FireStations', 'FireStations')

# run the extract data task and assign it to the 'result' variable
# only the cityhall layer was used as input, but the airport and firestation layers will be used in the service creation
aoi = "c:/gis/citydata/extract.shp"
result = arcpy.ExtractDataTask_server("CityHall", aoi, "File Geodatabase - GDB - .gdb", "ESRI GRID - GRID", os.path.join(arcpy.env.scratchFolder, "output.zip"))

# make sure the folder is registered with the server, if not, add it to the datastore
if arcpy.env.workspace not in [i[2] for i in arcpy.ListDataStoreItems(connPath, 'FOLDER')]:
     # both the client and server paths are the same
     dsStatus = arcpy.AddDataStoreItem(connPath, "FOLDER", "CityData", arcpy.env.workspace, arcpy.env.workspace)
     print "Data store : " + str(dsStatus)


# create service definition draft
arcpy.CreateGPSDDraft(
    result, sddraft, serviceName, server_type="ARCGIS_SERVER",
    connection_file_path=connPath, copy_data_to_server=False, 
    folder_name=None, summary="Extraction Service", tags="extract data, clip")
   

# analyze the service definition draft
analyzeMessages = arcpy.mapping.AnalyzeForSD(sddraft)

# stage and upload the service if the sddraft analysis did not contain errors
if analyzeMessages['errors'] == {}:
    # Execute StageService
    arcpy.StageService_server(sddraft, sd)
    # Execute UploadServiceDefinition
    upStatus = arcpy.UploadServiceDefinition_server(sd, connPath)
    print "Completed upload"
else: 
    # if the sddraft analysis contained errors, display them
    print analysis['errors']
