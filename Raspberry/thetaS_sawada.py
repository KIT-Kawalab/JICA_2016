#!/usr/local/bin/python3
# Download images and movies from the Theta S
# 2015-11-07
import sys, requests, os, time
import json as json_lib
from requests.exceptions import ConnectionError 

bPrintDebug = True
def print_debug(jsonString):
    if bPrintDebug: print json_lib.dumps(jsonString, indent=2)
    
def try_request(url, json = "", type='post'):
    response = ''
    try:
        response = getattr(requests, type)(url, json=json).json()
        if keys_error['error'] in response:
            print 'ERROR!'
            print json_lib.dumps(response[keys_error['error']], indent=2)
            quit()
    except ConnectionError as e:
        print "Error: Could not connect!"
        quit()
    else:
        print_debug(response)

    return response

API_info         = "/osc/info"
API_state        = "/osc/state"
API_checkUpdates = "/osc/checkForUpdates" 
commandsAPI      = "/osc/commands/"
API_commandsExecute = commandsAPI + "execute"
API_commandsStatus  = commandsAPI + "status"

thetaURL = "http://192.168.1.1:80"
URL_info             = thetaURL + API_info             # GET
URL_state            = thetaURL + API_state            # POST
URL_checkForUpdates  = thetaURL + API_checkUpdates     # POST
URL_commandsExecute  = thetaURL + API_commandsExecute  # POST
URL_commandsStatus   = thetaURL + API_commandsStatus   # POST

keys_error = {
    'state':'state',
    'name' :'name' ,
    'error':'error',
}
keys_error_error = {
    'code'   :'code'   ,
    'message':'message',
}
keys_info = {
    'manufacturer'   :'manufacturer'   ,
    'model'          :'model'          ,
    'serialNumber'   :'serialNumber'   ,
    'firmwareVersion':'firmwareVersion',
    'supportUrl'     :'supportUrl'     ,
    'endpoints'      :'endpoints'      ,
    'gps'            :'gps'            ,
    'gyro'           :'gyro'           ,
    'uptime'         :'uptime'         ,
    'api'            :'api'            ,
}
keys_endpoint = {
    'httpPort'       :'httpPort'       ,
    'httpUpdatesPort':'httpUpdatesPort',
}
keys_state = {
    'state'      :'state'       ,
    'fingerprint':'fingerprint' ,
}
keys_state_state = {
    '_recordedTime'  :'_recordedTime'  ,
    'storageChanged' :'storageChanged' ,
    '_batteryState'  :'_batteryState'  ,
    '_captureStatus' :'_captureStatus' ,
    '_latestFileUri' :'_latestFileUri' ,
    '_recordableTime':'_recordableTime',
    'sessionId'      :'sessionId'      ,
    'batteryLevel'   :'batteryLevel'   ,
}
keys_checkforupdates = {
    'fingerprint':'stateFingerprint'
}
keys_commands = {
    'name'      :'name',
    'parameters':'parameters',
}

keys_commands_response = {
    'name'    :'name'    ,
    'state'   :'state'   ,
    'id'      :'id'      ,
    'results' :'results' ,
    'error'   :'error'   ,
    'progress':'progress',
}

list_commands = {
    'startSession'   :'camera.startSession'   ,
    'updateSession'  :'camera.updateSession'  ,
    'closeSession'   :'camera.closeSession'   ,
    '_finishWlan'    :'camera._finishWlan'    ,
    'takePicture'    :'camera.takePicture'    ,
    '_startCapture'  :'camera._startCapture'  ,
    '_stopCapture'   :'camera._stopCapture'   ,
    'listImages'     :'camera.listImages'     ,
    '_listAll'       :'camera._listAll'       ,
    'delete'         :'camera.delete'         ,
    'getImage'       :'camera.getImage'       ,
    '_getVideo'      :'camera._getVideo'      ,
    '_getLivePreview':'camera._getLivePreview',
    'getMetadata'    :'camera.getMetadata'    ,
    'getOptions'     :'camera.getOptions'     ,
    'setOptions'     :'camera.setOptions'     ,
    '_stopSelfTimer' :'camera._stopSelfTimer' ,
}

list_commands_status = {
    'id':'id',
}

## return the JSON of the info of the camera
def getInfo():
    response = try_request(URL_info, type='get')
    return response

## return the JSON of the status of the camera
def getState():
    response = try_request(URL_state)
    return response
    
## return the state and print if it changed
def checkForUpdates(state):
    stateId = state[keys_state['fingerprint']]
    data = {keys_checkforupdates['fingerprint']: stateId}
    response = try_request(URL_checkForUpdates , json=data)
    newStateId = response[keys_checkforupdates['fingerprint']]
    
    if newStateId != stateId:
        print 'State Changed!'
        print_debug(state)
        state = getState()
    
    return state
  
def command_execute(command, data = {}):
    json = {keys_commands_response['name']:list_commands[command],keys_commands['parameters']:data}
    response = try_request(URL_commandsExecute,json=json)
    while response[keys_commands_response['state']] is 'inProgress':
        json = {list_commands_status['id']:response[keys_commands_response['id']]}
        response = try_request(URL_commandsStatus,json=json)
    return response
    
## start a session, returning the sessionId
def startSession():
	response = command_execute('startSession')
	return response['results']['sessionId']

def closeSession(sessionId):
    response = command_execute('closeSession', {'sessionId':sessionId})

def updateSession(sessionId):
	response = command_execute('updateSession', {'sessionId':sessionId})
	return response['results']['sessionId']
    
id = startSession()
print
info = getInfo()
print
state = getState()
print 
state = checkForUpdates(state)
print
updateSession(id)
print
closeSession(id)

    
    
