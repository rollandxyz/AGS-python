"""
Request an administrative token from ArcGIS Server.
Whenever you log in to Manager or the Administrator Directory, you need to
provide the user name and password of an account that has administrative or
publisher privileges to ArcGIS Server. The same concept applies when you write scripts.
You are required to programmatically submit a name and password to the server.
The server returns a token, which is a special string of characters that proves to the server
you have been authenticated to perform certain types of actions. You must include this token
in any web service requests you make to the server.

The token does not last forever; it is designed to time out so it cannot be stolen
and used indefinitely by a malicious user. You have to request a new token each time you run
your script (but not each time you make a request).

------------------------------------------------------------------------------------------------

To use the REST API, you create an HTTP request for the operation you want to perform and include
the required parameters for that operation; for example, the following HTTP request joins a new machine to your site:

http://gisserver.domain.com:6080/arcgis/admin/machines/registermachineName=GISSERVER1.DOMAIN.COMadminURL=http://GISSERVER1.DOMAIN.COM:6080/arcgis/admin


The ArcGIS Server Administrator Directory is a web application that can help you write administrative scripts for ArcGIS Server.
The Administrator Directory is typically available at http://gisserver.domain.com:6080/arcgis/admin.


Note the parameters you are required to enter and examine the URL in your browser's address bar as you make the request to the server.
Web developer tools such as Fiddler or Firebug can be useful to see the full body of the request and response.
This information is extremely valuable when you're attempting to construct your own administrative HTTP requests through Python or another scripting language.

Although you can use the Administrator Directory interactively to actually perform administrative tasks,
this web application is best used as a learning tool to help you get familiar with the REST API.
The intended web application for ArcGIS for Server administration is ArcGIS Server Manager.

"""
def getToken(username, password, serverName, serverPort):
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"
    
    # URL-encode the token parameters:-
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Error while fetch tokens from admin URL. Please check the URL and try again."
        return
    else:
        data = response.read()
        httpConn.close()
           
        # Extract the token from it
        token = json.loads(data)        
        return token['token']
