import sys
import os
import time
import rdt3 as reliabledtata


def main():
    MSG_LEN = reliabledtata.PAYLOAD 
    server_IP = "localhost"
    filename = str(input("Please Enter filename: "))
    drop_Rate = str(input("Enter drop rate: "))
    error_Rate = str(input("Enter Error rate:"))

    try:
        file_object = open(filename, 'rb')
    except OSError as emsg:
        print("Open file error: ", emsg)
        sys.exit(0)
    print("Open file successfully")

    filelength = os.path.getsize(filename)
    print("File bytes are ", filelength)

    reliabledtata.rdt_network_init(drop_Rate, error_Rate)

    rdtsocket = reliabledtata.rdt_socket()
    if rdtsocket == None:
        sys.exit(0)

    if reliabledtata.rdt_bind(rdtsocket, reliabledtata.CPORT) == -1:
        sys.exit(0)

    if reliabledtata.rdt_peer(server_IP, reliabledtata.SPORT) == -1:
        sys.exit(0)

    obj_size = reliabledtata.rdt_send(rdtsocket, str(filelength).encode("ascii"))
    if obj_size < 0:
        print("Cannot send message1")
        sys.exit(0)
    obj_size = reliabledtata.rdt_send(rdtsocket, filename.encode("ascii"))
    if obj_size < 0:
        print("Cannot send message2")
        sys.exit(0)
    rmsg = reliabledtata.rdt_recv(rdtsocket, MSG_LEN)
    if rmsg == b'':
        sys.exit(0)
    elif rmsg == b'ERROR':
        print("Server experienced file creation error.\nProgram terminated.")
        sys.exit(0)
    else:
        print("Received server positive response")

    print("Start the file transfer . . .")
    starttime = time.monotonic()  
    sent = 0
    while sent < filelength:
        print("---- Client progress: %d / %d" % (sent, filelength))
        smsg = file_object.read(MSG_LEN)
        if smsg == b'':
            print("EOF is reached!!")
            sys.exit(0)
        obj_size = reliabledtata.rdt_send(rdtsocket, smsg)
        if obj_size > 0:
            sent += obj_size
        else:
            print("Experienced sending error! Has sent", sent, "bytes of message so far.")
            sys.exit(0)

    endtime = time.monotonic()  
    print("Completed the file transfer.")
    lapsed = endtime - starttime
    print("Total elapse time: %.3f s\tThroughtput: %.2f KB/s" % (lapsed, filelength / lapsed / 1000.0))

    file_object.close()
    reliabledtata.rdt_close(rdtsocket)
    print("Client program terminated")


if __name__ == "__main__":
    main()
