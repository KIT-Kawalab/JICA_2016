import gattlib
import time
import binascii

# address to be conected
bdaddr = "80:7B:85:A0:00:EA"

BLE_protocolV1_recv = [
#   Field         , size, divide
    ['Id'         , 4   , 1     ],
    ['Temperature', 6   , 100.0 ],
    ['Pression'   , 6   , 100.0 ],
    ['Humidity'   , 6   , 1024.0],
    ['X'          , 2   , 1.0   ],
    ['Y'          , 2   , 1.0   ],
    ['Z'          , 2   , 1.0   ],
]
BLE_protocolV1_send = {
#   Field    : size
    'Id'     : 4   ,
    'Cmd'    : 4   ,
    'Args'   : 0   ,
}

# search for device
def searchForBdaddr(bdaddr = ""):
    while 1:
        finded = False
        service = gattlib.DiscoveryService("hci0")
        devices = service.discover(2)
        if not bdaddr:
                return devices.items()
        for address, name in devices.items():
            print("name: {}, address: {}".format(name, address))
            if bdaddr and address == bdaddr: finded = True
        if finded: break
        print
        time.sleep(2)
        
# connect to BLE
def BLE_connect(bdaddr):
    req = gattlib.GATTRequester(bdaddr)
    print id(req)
    return req
    
# receive
# receive the data in bytes from BLE, convert to string and return
def BLE_recv(req, handle = "", uuid = ""):
    try:
        if handle:
            recv = binascii.hexlify(req.read_by_handle(handle)[0])
    except:
        if handle:
            print "Error while reading handle=<0x{0:04X}> addr=<{1}>".format(handle, bdaddr)
    else:
        print "recv: " + recv
        return recv

# send
# receive data as string in parameters, transform to bytes and send to BLE
def BLE_send(req, data, handle = "", uuid = ""):
    print "send: " + data
    try:
        if handle:
            send = req.write_by_handle(handle, str(binascii.unhexlify(data)))
    except:
        if handle:
            print "Error while writing handle=<{0}> addr=<{1}>".format(handle, bdaddr)

# return the message string to be send
def BLE_MountProtocol_v1(data):
    dataCmd = ''
    dataCmd += strFixedSize(data['Id'  ], BLE_protocolV1_send['Id'  ])
    dataCmd += strFixedSize(data['Cmd' ], BLE_protocolV1_send['Cmd' ])
    dataCmd += strFixedSize(data['Args'], BLE_protocolV1_send['Args'])

    size = len(dataCmd)
    # max of 16 bytes to send
    if not 0 < size <= 32:
        print "Error: bad message size <{0}> for protocol v1".format(size)
    # dataCmd send in bytes, need to be pair to form the nibles
    if size%2 != 0:
        dataCmd = dataCmd + "0"
        size += 1
    # generate the message string to be send
    protoV1 = ("{0:02X}{1}{2}".format((size/2)+3,"000000",dataCmd))
    return protoV1
    
def strFixedSize(data, size):
    return "{0:0{1}d}".format(data, size if size > 0 else (len(str(data)) if len(str(data))%2 == 0 else len(str(data)) + 1))
    
# return a dictionary with the fields received
def BLE_ReeadProtocol_v1(data):
    utilDataSize = int(data[:2], base=16)
    if not 3 < utilDataSize < 20:
        print "Error - IMBLE BLE message size = <{0}>".format(utilDataSize)
    message = data[8:8+(utilDataSize-3)*2]

    if len(message) != sum([size for field, size, divide in BLE_protocolV1_recv]):
        print "Error - Message received invalid for Protocol V1"
        return None
    
    protoV1 = dict()
    readAux = 0
    for field, size, divide in BLE_protocolV1_recv:
        protoV1[field] = float(message[readAux:readAux+size])/divide
        readAux += size
    
    return protoV1
    
def IMBLE_BLE_recv(req):
    return BLE_ReeadProtocol_v1(BLE_recv(req, handle=0x001b))
    
def IMBLE_BLE_send(req, data):
    return BLE_send(req, BLE_MountProtocol_v1(data), handle=0x001e)
    
    
import thingspeak
import time
channel_id = 163970
write_key  = 'E98LWEFL09IPE4PB'
read_key   = 'PTVH6FD2YT2V6D1D'
thingspeak_time_api = 10        # time to sleep between calls to thingspeak


def ThingSpeak_SendProtocol_v1(channel, protocolV1):
    try:
        response = channel.update({1:protocolV1[BLE_protocolV1_recv[1][0]],2:protocolV1[BLE_protocolV1_recv[2][0]],3:protocolV1[BLE_protocolV1_recv[3][0]]})
    except:
        print "ThingSpeak Error - connection failed"
    print time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
    print response
    
    
# main function
def main():
    print searchForBdaddr()
    # wait for the BLE be finded and connect
    searchForBdaddr(bdaddr) 
    req = BLE_connect(bdaddr)
    print id(req)
    
    # receive data from BLE
    raw_input("press a key when value received: ")
    #recv = BLE_recv(req, handle=0x001b)
    #message = BLE_ReeadProtocol_v1(recv)
    message = IMBLE_BLE_recv(req)
    for field in BLE_protocolV1_recv:
        print field[0] + ": " + str(message[field[0]])
        
    # send data to ThingSpeak
    channel = thingspeak.Channel(id=channel_id,write_key=write_key)
    ThingSpeak_SendProtocol_v1(channel, message)
    
    # send data to BLE
    raw_input("press a key to send: ")
    #send = BLE_send(req, BLE_MountProtocol_v1("12345678901234567890123456789012"), handle=0x001e)
    send = IMBLE_BLE_send(req, {'Id': 1, 'Cmd': 2, 'Args': 3})
    # disconnect
    del req
    raw_input("fim")
    
if __name__ == "__main__":
    main()
    