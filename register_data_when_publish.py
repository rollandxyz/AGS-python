import arcpy
import os



"""
This example shows how you can programmatically register a data folder with ArcGIS Server.
Registering folders and databases is possible through the ArcGIS REST API,
but it's typically easier to use the arcpy functions.

In this example, the folder (held by the variable named wrkspc) must contain both the MXD and the source data.
Before running this script, you should ensure that the ArcGIS Server account has permissions to the folder.
The script calls arcpy.ListDataStoreItems to check if any folders registered with ArcGIS Server have the same path as the folder.
If no matches are found, the script registers the folder using arcpy.AddDataStoreItem.

The remainder of the script uses arcpy functions to analyze the map and publish the service.
"""

arcpy.env.overwriteOutput = True

# Path to ArcGIS Server connection file
connPath = "C:/data/connections/myserver.ags"

# Folder containing data and MXD
wrkspc = "C:/data/Tulsa/"
mapName = "Parcels.mxd"

# Service metadata
service = "TulsaParcels"
summary = "Shows cadastral data in Tulsa"
tags = "Tulsa, cadastre, parcels"

# make sure the folder is registered with the server, if not, add it to the datastore
if wrkspc not in [i[2] for i in arcpy.ListDataStoreItems(connPath, 'FOLDER')]:
     # both the client and server paths are the same
     dsStatus = arcpy.AddDataStoreItem(connPath, "FOLDER", "Workspace for " + service, wrkspc, wrkspc)
     print "Data store : " + str(dsStatus)

# Provide other service details
mapDoc = arcpy.mapping.MapDocument(os.path.join(wrkspc, mapName))
sddraft = os.path.join(wrkspc, service + '.sddraft')
sd = os.path.join(wrkspc, service + '.sd')

# Create service definition draft
arcpy.mapping.CreateMapSDDraft(mapDoc, sddraft, service, 'ARCGIS_SERVER', connPath, True, None, summary, tags)

# Analyze the service definition draft
analysis = arcpy.mapping.AnalyzeForSD(sddraft)

# Print errors, warnings, and messages returned from the analysis
print "The following information was returned during analysis of the MXD:"
for key in ('messages', 'warnings', 'errors'):
  print '----' + key.upper() + '---'
  vars = analysis[key]
  for ((message, code), layerlist) in vars.iteritems():
    print '    ', message, ' (CODE %i)' % code
    print '       applies to:',
    for layer in layerlist:
        print layer.name,
    print

# Stage and upload the service if the sddraft analysis did not contain errors
if analysis['errors'] == {}:
    # Execute StageService. This creates the service definition.
    arcpy.StageService_server(sddraft, sd)

    # Execute UploadServiceDefinition. This uploads the service definition and publishes the service.
    arcpy.UploadServiceDefinition_server(sd, connPath)
    print "Service successfully published"
else: 
    print "Service could not be published because errors were found during analysis."

print arcpy.GetMessages()
