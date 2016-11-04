
"""
A service definition (.sd) encapsulates a service into a single transferable file, 
optionally including source GIS data. 
The Upload Service Definition tool uploads a service definition to 
the server and publishes it. It can be invoked from the arcpy site 
package included with ArcGIS for Desktop.

The following Python example loops through a given folder, 
finds the service definitions contained therein (excluding subfolders), 
and publishes them to ArcGIS Server. All that's required is a data location, 
the path to an ArcGIS Server connection file, and the name 
of the destination folder on ArcGIS Server. 
The service definitions could be of any service type.
"""
# Publishes all service definitions in an operating system directory
#  (excluding subfolders)
import arcpy, os

# Define path to SDs
wrkspc = "C:/data"
sdDir = wrkspc + "/SDs"

# Provide path to connection file
# To create this file, right-click a folder in the Catalog window and
#  click New > ArcGIS Server Connection
con = wrkspc + "/connections/arcgis on myserver_6080 (publisher).ags"

# Destination folder name on ArcGIS Server
serverFolder = "TestPublish"

# Loop through all items in folder
sdList = os.listdir(sdDir)

for sd in sdList:
    
    # Construct path to item
    extension = os.path.splitext(sd)[1] #Get file extension
    sdPath = os.path.join(sdDir, sd)

    # Check if item is an SD file and, if so, try to publish
    if os.path.isfile(sdPath) and extension == ".sd":    
        try:     
            arcpy.UploadServiceDefinition_server(sdPath, con, "", "", "EXISTING", serverFolder)
            print "Published " + sd + " with no errors reported."
            
        except:
            print "Could not complete publishing operation for " + sd + "."

        print arcpy.GetMessages()