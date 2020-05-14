import socket, pickle, thread, time, random 
import sys
import copy 

class packet:
    def __init__(self, s , d):
        self.sourc = s
        self.dest = d
        self.hops = 0
        self.path = []
        self.reply = []

def droprate(x):
    drop = random.randrange(1,100)
    if drop<=x:
        return True
    else:
        return False

neighbours=[]
cache = {}
drop_rate=-1
req=False
rep=False

def listening_node(server_port):
    global req
    global rep
    s = socket.socket()          
    print ("Socket successfully created")
    s.bind(('', server_port))         
    print ("socket binded to %s" %(server_port)) 
    s.listen(5) 
    print ("socket is listening")   
    
    while True: 
        # Establish connection with client. 
        conn, addr = s.accept()      
        #print ('Got connection from', addr) 
        # send a thank you message to the client.  
        data = conn.recv(4096)
        stringdata = data.decode('utf-8')
        stringdata = str(stringdata)
        #print (stringdata)
        if (stringdata[:9]=="DSRPACKET"):
            data_variable = pickle.loads(stringdata[10:])
            if (len(data_variable.reply)<1):
                print ("%.20f" % time.time())
                print ("DSRPACKET received!!")
                req=False
                rep=False
            else:
                if (droprate(drop_rate)!=True):
                    firstnode=data_variable.reply[-1]                
                    msg_socket = socket.socket() 
                    msg_socket.connect(('127.0.0.1', firstnode))
                    #print ("check2",data_variable.reply)
                    #cache[data_variable.reply[0]]=data_variable.reply
                    del data_variable.reply[-1]
                    data_string = pickle.dumps(data_variable)
                    msg_socket.send("DSRPACKET:"+data_string)
                    msg_socket.close()
                else:
                    print ("!!Drop Message!!")
            del data_variable
        elif (stringdata[:6]=="PACKET"):
            data_variable = pickle.loads(stringdata[7:])
            #data_variable.path = list(set(data_variable.path)) 
            data_variable.path = [i for n, i in enumerate(data_variable.path) if i not in data_variable.path[:n]] 
            if (data_variable.dest==server_port):
                print ("%.20f" % time.time())
                print ("Packet received!!")
                print (data_variable.path)
            else:
                if (droprate(drop_rate)!=True):
                    for i in range(len(neighbours)):
                        #print (neighbours,len(neighbours))
                        #print (data_variable.path)
                        if (neighbours[i] in data_variable.path):
                            print ("visited neighbour")
                        else:
                            msg_socket = socket.socket() 
                            msg_socket.connect(('127.0.0.1', neighbours[i]))
                            #print ("check-x")
                            data_variable.path.append(server_port)
                            data_string = pickle.dumps(data_variable)
                            #print ("helllo\n",data_string)
                            msg_socket.send("PACKET:"+data_string)
                            msg_socket.close()
                    
                else:
                    print ("!!Drop Message!!")
            del data_variable
        elif (stringdata[:4]=="RREQ"):
            data_variable = pickle.loads(stringdata[5:])
            data_variable.path = [i for n, i in enumerate(data_variable.path) if i not in data_variable.path[:n]] 
            if (data_variable.dest==server_port):
                print ("RREQ received!!")
                print (data_variable.path)
                if (req==False):
                    req=True
                    cache[data_variable.path[0]]= copy.deepcopy(data_variable.path)
                firstnode=data_variable.path[-1]
                msg_socket = socket.socket() 
                msg_socket.connect(('127.0.0.1', firstnode))
                del data_variable.path[-1]
                data_variable.reply.append(server_port)
                data_string = pickle.dumps(data_variable)
                msg_socket.send("RREP:"+data_string)
                msg_socket.close()
            else:
                for i in range(len(neighbours)):
                    if (neighbours[i] in data_variable.path):
                        h=10
                    else:
                        msg_socket = socket.socket() 
                        msg_socket.connect(('127.0.0.1', neighbours[i]))
                        cache[data_variable.path[0]]=copy.deepcopy(data_variable.path)
                        data_variable.path.append(server_port)
                        data_string = pickle.dumps(data_variable)
                        msg_socket.send("RREQ:"+data_string)
                        msg_socket.close()
            del data_variable
        elif (stringdata[:4]=="RREP"):
            data_variable = pickle.loads(stringdata[5:])
            if (len(data_variable.path)<1):
                print ("RREP received!!")
                #print (data_variable.reply)
                firstnode=data_variable.reply[-1]
                msg_socket = socket.socket() 
                msg_socket.connect(('127.0.0.1', firstnode))
                #cache[data_variable.reply[0]]=data_variable.reply
                cache[data_variable.reply[0]]=copy.deepcopy(data_variable.reply)
                #print ("check1",data_variable.reply)
                del data_variable.reply[-1]
                data_string = pickle.dumps(data_variable)
                msg_socket.send("DSRPACKET:"+data_string)
                msg_socket.close()
            else:
                firstnode=data_variable.path[-1]                
                msg_socket = socket.socket() 
                msg_socket.connect(('127.0.0.1', firstnode))
                cache[data_variable.reply[0]]=copy.deepcopy(data_variable.reply)
                del data_variable.path[-1]
                data_variable.reply.append(server_port)
                data_string = pickle.dumps(data_variable)
                #print ("helllo\n",data_string)
                msg_socket.send("RREP:"+data_string)
                msg_socket.close()
            del data_variable
        elif (stringdata[:4]=="DROP"):
            print ("Drop function")
            #print(int(stringdata[5:]))
            if (len(neighbours)>1):
                neighbours.remove(int(stringdata[5:]))
                conn.send("DONE")
            else:
                print ("Can't break connections only 1 left")
                conn.send("ERR")

        else:
            neighbours.append(int(stringdata))
            print ("Adding neighbour",neighbours)

        conn.close()      

def main(filepath):
    global drop_rate
    #server_port =  input("Enter server port: ")            
    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            #print("Line {}: {}".format(cnt, line.strip()))
            x=line.strip()
            if (x=="sleep"):
                time.sleep(5)
            else:
                if (cnt>1):
                    #print (x[0],x[2:])
                    print(x)
                    main_input=int(x[0])
                    if (len(x)>2):
                        second_input=int(x[2:])
                    if (main_input == 1):
                        #val = input("Enter port to connect to: ")
                        val=second_input
                        client_socket = socket.socket()  
                        port = val
                        client_socket.connect(('127.0.0.1', port))
                        neighbours.append(port) 
                        client_socket.send(str(server_port))
                        client_socket.close()
                    elif (main_input == 2):
                        #print ("helooo jeee")
                        if (len(neighbours)>1):
                            rand = random.randrange(0,len(neighbours))
                            #rand = 
                            #print ("Random Number ", rand)
                            #print (neighbours[rand])
                            client_socket = socket.socket() 
                            client_socket.connect(('127.0.0.1', neighbours[rand]))
                            client_socket.send("DROP:"+str(server_port))
                            data1 = client_socket.recv(4096)
                            stringdata1 = data1.decode('utf-8')
                            stringdata1 = str(stringdata1)
                            #print("Reply from broked node!",stringdata1)
                            if (stringdata1 == "DONE"):
                                neighbours.pop(rand)
                                print ("!!Dropped neighbour!!")
                            client_socket.close()
                        else:
                            print ("Can't break connections only 1 left")
                    elif (main_input == 3):
                        print ("My neighbours",neighbours)
                    elif (main_input == 4):
                        #dp=input("Enter Destination port: ")
                        #print("helloooo",second_input)
                        print ("%.20f" % time.time())
                        dp=second_input
                        p=packet(server_port,dp)
                        p.path.append(server_port)
                        for i in range(len(neighbours)):
                            client_socket = socket.socket() 
                            client_socket.connect(('127.0.0.1', neighbours[i]))
                            data_string = pickle.dumps(p)
                            client_socket.send("PACKET:"+data_string)
                            client_socket.close()
                    elif (main_input == 5):
                        #dp=input("Enter Destination port: ")
                        print ("%.20f" % time.time())
                        dp=second_input
                        p=packet(server_port,dp)
                        if (cache.get(dp)!=None):
                            p.reply=cache.get(dp)
                            firstnode=p.reply[-1]
                            msg_socket = socket.socket() 
                            msg_socket.connect(('127.0.0.1', firstnode))
                            del p.reply[-1]
                            data_string = pickle.dumps(p)
                            msg_socket.send("DSRPACKET:"+data_string)
                            msg_socket.close()
                        else:
                            p.path.append(server_port)
                            for i in range(len(neighbours)):
                                client_socket = socket.socket() 
                                client_socket.connect(('127.0.0.1', neighbours[i]))
                                data_string = pickle.dumps(p)
                                client_socket.send("RREQ:"+data_string)
                                client_socket.close()
                    elif (main_input == 6):
                        print ("Cache",cache)
                    elif (main_input == 7):
                        print ("Setting drop rate",drop_rate)
                        #k=input("Enter drop rate in percentage (%): ")
                        k=second_input
                        if (k<100 and k>0):
                            drop_rate=k
                        else:
                            print ("Out of range input!")
                        print ("Setting drop rate",drop_rate)
                    main_input=""
                elif (cnt==1):
                    server_port = int(x)
                    thread.start_new_thread(listening_node,(server_port,))
            line = fp.readline()
            cnt += 1
        time.sleep(50)    
    
    # while True:
    #     time.sleep(1)
    #     main_input = input("==ENTER OPTION==\n1:Connect to port\n2:Breaking connections\n3:Print Neighbours\n4:Send Message (Flooding)\n5:Send Message (DSR)\n6:Print Cache\n7:Set Drop Rate\n")
    #     main_input = int(main_input)
       

main(sys.argv[1])
# thread.start_new_thread(main,('node1.txt',))
# thread.start_new_thread(main,('node2.txt',))
# thread.start_new_thread(main,('node3.txt',))
# thread.start_new_thread(main,('node4.txt',))
#main('node1.txt')
#main('node2.txt')
#main('node3.txt')
#main('node4.txt')
