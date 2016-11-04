import sys,os
import getpass
import arcpy
import codecs


"""
"""

def main(argv=None):
    
    # Ask for admin user name and password
    
    username = raw_input("Enter user name: ")
    password = getpass.getpass("Enter password: ")
    
    # Ask for server name & port
    serverName = raw_input("Enter server name: ")
    serverPort = raw_input("Enter server port: ")
 
    # Create a connection file to the server and save it in the same location as that of the script
    serverURL="http://"+serverName+":"+str(serverPort)+"/arcgis/admin"
    try:
        arcpy.mapping.CreateGISServerConnectionFile("PUBLISH_GIS_SERVICES",os.curdir,serverName+".ags",serverURL,"ARCGIS_SERVER",username=username,password=password)
    except Exception, e:
            print e.message    
    
    agsConnection = os.path.join(os.curdir, serverName+".ags")
    
    if not os.path.isfile(agsConnection):
        print("Unable to connect to ArcGIS Server. Exiting.")
        sys.exit(1)

    # Input File that contains the data store information
    dataStoresFile = raw_input("Path to pipe-delimited text file containing datastore information: ")
    
    num = 0 
    datastores = {}
    
    for datastoreRow in readlinesFromInputFile(dataStoresFile):
            
        datastoreEntry = {}
        
        for index in range(len(datastoreRow)):
            
            datastoreProp = datastoreRow[index].split("=")
            
            if datastoreProp[0] == "dsName":
                datastoreEntry["connection_name"] = datastoreProp[1]
            if datastoreProp[0] == "dsType":
                datastoreEntry["datastore_type"] = datastoreProp[1]
            if datastoreProp[0] == "serverPath":
                datastoreEntry["server_path"] = datastoreProp[1]
            if datastoreProp[0] == "clientPath":
                datastoreEntry["client_path"] = datastoreProp[1]
            if datastoreProp[0] == "hostname":
                datastoreEntry["hostname"] = datastoreProp[1]
         
            # Add the datastore information to a dictionary
            datastores["datastore" + str(num)] = datastoreEntry
        
        num +=1

    # Call helper functions to register datastores
    addDataStores(datastores,agsConnection)

# A function that reads lines from the input file
def readlinesFromInputFile(filename, delim='|'):
    file = codecs.open(filename,'r','utf-8-sig')
    for line in file.readlines():
        # Remove the trailing whitespaces and the newline characters
        line = line.rstrip()
        
        if line.startswith('#') or len(line) == 0:
            pass # Skip the lines that contain # at the beginning or any empty lines
        else:
            # Split the current line into list
            yield line.split(delim)
    file.close()
    
def addDataStores(datastoresDict,agsConnection):
    
    for datastoreToAdd in datastoresDict:
        # Build the dictionary with the role name and description               
        datastoresDict[datastoreToAdd]["connection_file"] =  agsConnection
        
        print "Adding the datastore: " + datastoresDict[datastoreToAdd]['connection_name']
        
        try:
            arcpy.AddDataStoreItem(**datastoresDict[datastoreToAdd])
            print "Successfully added the datastore: " + datastoresDict[datastoreToAdd]['connection_name'] 
        except Exception, e:
            print "Adding of the datastore: " + datastoresDict[datastoreToAdd]['connection_name'] + " failed."
            print e.message

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
