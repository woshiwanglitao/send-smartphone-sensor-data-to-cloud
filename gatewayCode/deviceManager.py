# refer to https://msdn.microsoft.com/en-us/library/azure/mt548489.aspx)

import base64
import hmac
import hashlib
import time
import requests
import urllib

class DeviceManager:
    
    API_VERSION = '2016-02-03'
    TOKEN_VALID_SECS = 365 * 24 * 60 * 60
    TOKEN_FORMAT = 'SharedAccessSignature sr=%s&sig=%s&se=%s&skn=%s'
    
    def __init__(self, connectionString=None):
        if connectionString != None:
            iotHost, keyName, keyValue = [sub[sub.index('=') + 1:] for sub in connectionString.split(";")]
            self.iotHost = iotHost
            self.keyName = keyName
            self.keyValue = keyValue
    
    def _buildExpiryOn(self):
        return '%d' % (time.time() + self.TOKEN_VALID_SECS)
    
    def _buildSasToken(self):
        targetUri = self.iotHost.lower()
        expiryTime = self._buildExpiryOn()
        toSign = '%s\n%s' % (targetUri, expiryTime)
        key = base64.b64decode(self.keyValue.encode('utf-8'))
        signature = urllib.parse.quote(
            base64.b64encode(
                hmac.HMAC(key, toSign.encode('utf-8'), hashlib.sha256).digest()
                )
        ).replace('/', '%2F')
        return self.TOKEN_FORMAT % (targetUri, signature, expiryTime, self.keyName)
    
    def createDeviceId(self, deviceId):
        sasToken = self._buildSasToken()
        url = 'https://%s/devices/%s?api-version=%s' % (self.iotHost, deviceId, self.API_VERSION)
        body = '{deviceId: "%s"}' % deviceId
        r = requests.put(url, headers={'Content-Type': 'application/json', 'Authorization': sasToken}, data=body)
        return r.text, r.status_code
    
    def retrieveDeviceId(self, deviceId):
        sasToken = self._buildSasToken()
        url = 'https://%s/devices/%s?api-version=%s' % (self.iotHost, deviceId, self.API_VERSION)
        r = requests.get(url, headers={'Content-Type': 'application/json', 'Authorization': sasToken})
        return r.text, r.status_code
    
    def listDeviceIds(self, top=None):
        if top == None:
            top = 1000
        sasToken = self._buildSasToken()
        url = 'https://%s/devices?top=%d&api-version=%s' % (self.iotHost, top, self.API_VERSION)
        r = requests.get(url, headers={'Content-Type': 'application/json', 'Authorization': sasToken})
        return r.text, r.status_code
        
    def deleteDeviceId(self, deviceId):
        sasToken = self._buildSasToken()
        url = 'https://%s/devices/%s?api-version=%s' % (self.iotHost, deviceId, self.API_VERSION)
        r = requests.delete(url, headers={'Content-Type': 'application/json', 'Authorization': sasToken, 'If-Match': '*' }) # If-Match Etag, but if * is used, no need to precise the Etag of the device. The Etag of the device can be seen in the header requests.text response 
        return r.text, r.status_code

if __name__ == '__main__':
    connectionString = <YOUR IOT HUB CONNECTION STRING>
    dm = DeviceManager(connectionString)
    deviceId = 'rpi_cluster_001'
    # print (dm.iotHost, dm.keyName, dm.keyValue)
    # print (dm.createDeviceId(deviceId))
    # print (dm.retrieveDeviceId(deviceId))
    print (dm.listDeviceIds())
    # print (dm.deleteDeviceId(deviceId))

