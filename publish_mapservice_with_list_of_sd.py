import json
import urllib,httplib
import sys
import getpass
import arcpy
import os
import codecs

"""
#SD|folderName|serviceName|clusterName
SD=\\mylabserver\Yellowstone.sd|folderName=Parks|serviceName=Yellowstone
SD=\\mylabserver\Rainier.sd|serviceName=Rainier
SD=C:\data\BufferGP.sd|serviceName=BufferGeoprocessing
SD=C:\data\Arches.sd|folderName=Parks|serviceName=Arches|clusterName=mapCluster



The script first checks if the service exists in the specified folder.
If the service exists, it is deleted and then republished.
Thus, the text file can contain a long list of services to
deploy or just one service to update.
"""
def main(argv=None):
    
    # Ask for admin user name and password
    
    username = raw_input("Enter user name: ")
    password = getpass.getpass("Enter password: ")
    
    # Ask for server name and the port
    serverName = raw_input("Enter server name: ")
    serverPort = raw_input("Enter server port: ")
    
    # Get a token and connect
    token = getToken(username, password, serverName, serverPort)
    
    if token == "":
        sys.exit(1)

    # Create a connection file to the server            
    serverURL="http://"+serverName+":"+str(serverPort)+"/arcgis/admin"
    try:
        arcpy.mapping.CreateGISServerConnectionFile("PUBLISH_GIS_SERVICES",os.curdir,serverName+".ags",serverURL,"ARCGIS_SERVER",username=username,password=password)
    except Exception, e:
            print e.message   
    
    agsConnection = os.path.join(os.curdir, serverName+".ags")
    
    if not os.path.isfile(agsConnection):
        print("Unable to connect to ArcGIS Server -- exiting")
        sys.exit(1)
    
    # Input file that contains the services information
    servicesFile = raw_input("Path to pipe-delimited text file containing services: ")
    
    num = 0 
    services = {}
    
    for serviceRow in readlinesFromInputFile(servicesFile):
        
        serviceEntry = {}
            
        for index in range(len(serviceRow)):
            
            serviceProp = serviceRow[index].split("=")
            
            if serviceProp[0] == "SD":
                serviceEntry["in_sd_file"] = serviceProp[1]
            if serviceProp[0] == "serviceName":
                serviceEntry["in_service_name"] = serviceProp[1]
            if serviceProp[0] == "folderName":
                serviceEntry["in_folder"] = serviceProp[1]
                if isFolderPresent(serviceProp[1],serverName, serverPort,token):
                    serviceEntry["in_folder_type"]="EXISTING"
                else:        
                    serviceEntry["in_folder_type"]="NEW"
            if serviceProp[0] == "clusterName":
                serviceEntry["in_cluster"] = serviceProp[1]
            if serviceProp[0] == "startupType":
                serviceEntry["in_startupType"] = serviceProp[1]
         
            # Add the services information to a dictionary
            services["service" + str(num)] = serviceEntry

        num +=1
        
    # Call helper functions to publish services
    addServices(services,serverName,serverPort,token,agsConnection)

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
    
def addServices(serviceDict, serverName, serverPort, token, agsConnection):
    
    for serviceToAdd in serviceDict:
        
        # Check to see that SD is present and that it is reachable.
        if not os.path.isfile(serviceDict[serviceToAdd]['in_sd_file']):
            print("Unable to access '" + serviceDict[serviceToAdd]['in_sd_file']+"'. Skipping to publish.")
       
        else:    
            #Delete the service first (if it exists) and then re-publish it
            if serviceDict[serviceToAdd].has_key("in_service_name"):
                if serviceDict[serviceToAdd].has_key("in_folder"):
                    deleteServiceIfPresent(serverName,serverPort,token,serviceDict[serviceToAdd]["in_service_name"],serviceDict[serviceToAdd]["in_folder"])
                else:
                    deleteServiceIfPresent(serverName,serverPort,token,serviceDict[serviceToAdd]["in_service_name"])
                        
            serviceDict[serviceToAdd]["in_server"] =  agsConnection
            
            print "Publishing the service: " + serviceDict[serviceToAdd]['in_sd_file']
            
            try:
                arcpy.UploadServiceDefinition_server(**serviceDict[serviceToAdd])
                print "Successfully published the service: " + serviceDict[serviceToAdd]['in_sd_file']
                
            except Exception, e:
                print "Publishing of " + serviceDict[serviceToAdd]['in_sd_file'] + " failed."
                print e.message
 
# A function that will post HTTP POST request to the server
def postToServer(serverName, serverPort, url, params):
    
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # URL encode the resource URL
    url = urllib.quote(url.encode('utf-8'))
    
    # Build the connection to add the roles to the server
    httpConn.request("POST", url, params, headers)

    response = httpConn.getresponse()
    data = response.read()
    httpConn.close()

    return (response, data)
    
# A function that checks that the JSON response received from the server does not contain an error   
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        return False
    else:
        return True

def getToken(username, password, serverName, serverPort):

    tokenURL = "/arcgis/admin/generateToken"
    params = urllib.urlencode({'username': username, 'password': password,'client': 'requestip', 'f': 'json'})
    
    response, data = postToServer(serverName, serverPort, tokenURL, params)
        
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Error while fetching tokens from admin URL. Please check if the server is running and ensure that the username/password provided are correct"
        print str(data)
        return
    else: 
        # Extract the token from it
        token = json.loads(data)   
        return token['token']            
    
def isFolderPresent(folderName,serverName, serverPort,token):
    
    params = urllib.urlencode({'token':token,'f': 'json'})    
    folderURL = "/arcgis/admin/services"
    
    response, data = postToServer(serverName, serverPort, folderURL, params)
        
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Error while fetching folders from the server."
        print str(data)
        return
    
    servicesJSON = json.loads(data)
    
    folders = servicesJSON['folders']
    for folder in folders:
        if folder == folderName :
            return True
    return False      
    
def deleteServiceIfPresent(serverName,serverPort, token, serviceName, folderName='root'):
    
    # If the folder itself is not present, we do not need to check for the service's presence in this folder.
    if folderName != 'root' and not isFolderPresent(folderName,serverName, serverPort,token): 
            return
            
    params = urllib.urlencode({'token':token,'f': 'json'})
        
    if  folderName == 'root' :
        URL = "/arcgis/admin/services/"
    else:
        URL = "/arcgis/admin/services/"+folderName
    
    response, data = postToServer(serverName, serverPort, URL, params)
        
    if (response.status != 200 or not assertJsonSuccess(data)):
        print "Error while fetching the service information from the server."
        print str(data)
        return
        
    #extract the services from the JSON response
    servicesJSON = json.loads(data)
    
    services = servicesJSON['services']
    for service in services:
        if service['serviceName'] == serviceName : 
            
            ##delete the service
            params = urllib.urlencode({'token':token,'f': 'json'})

            if  folderName == 'root' :
                URL = "/arcgis/admin/services/"+serviceName+"."+service['type']+"/delete"
            else:
                URL = "/arcgis/admin/services/"+ folderName + "/" + serviceName+"."+service['type']+"/delete"
            
            print "Found the service '" + serviceName + "."+ service['type'] + " at '" + folderName + "' folder in the server, the service will be deleted and be re-published."
           
            response, data = postToServer(serverName, serverPort, URL, params)
            
            if (response.status != 200 or not assertJsonSuccess(data)):
                
                print "Failed to delete the service: '" + serviceName + "." + service['type']
                print str(data)
                return
            else:
                print "Deleted the service '" + serviceName + "."+service['type']+ " successfully."
    
# Script start 
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
