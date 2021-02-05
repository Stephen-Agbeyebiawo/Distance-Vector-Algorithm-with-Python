from socket import *
from time import sleep
from threading import *
from json import *
from configparser import ConfigParser

sleeptime = 30 #advert intervals in seconds
deadtime = sleeptime + 10 #dead timers in seconds
config = ConfigParser() #.ini parser to load and save .ini config file
parser = ConfigParser() 

#Classes
class interface:    #interface object with name of the interface, the cost and the state
    def __init__(self, name, cost, state = "down"): #default state set to "down"
        self.name = name
        self.state = state
        self.cost = cost

    def start_int(self):    #class function to set the state of the interface to "up" and display message to show change was susccessfull
        self.state = "up"
        print(f"[INFO]---Interface {self.name} state has changed to {self.state}")

    def stop_int(self):    #class function to set the state of the interface to "up" and display message to show change was susccessfull
        self.state = "down"
        print(f"[INFO]---Interface {self.name} state has changed to {self.state}")

    def change_cost(self, cost):    #class function to change cost fo interface
        self.cost = cost
        print(f"[INFO]---Cost of Interface {self.name} changed to {self.cost}")

class router: #router class
    def __init__(self, name, state = "stopped"):
        self.name = name
        self.state = state

class dv_object:    #Distance vector object class to populate DV database table
    def __init__(self, destination, cost, interface, source_router):
        self.destination = destination
        self.cost = cost
        self.interface = interface
        self.source_router = source_router

class neighbor: #Neighbor object class to create neighbors
    def __init__(self, name, interface, state, counter = 40):
        self.name = name
        self.interface = interface
        self.state = state
        self.counter = counter

    def change_neighbor_state(self, state):
        self.state = state
        print(f"[INFO]---Neighbor {self.name}'s state has changed to {self.state}")

class link: #Link object class to create links
    def __init__(self, local_node, remote_node, local_int, remote_int, cost, state = "down"):
        self.local_node = local_node
        self.remote_node = remote_node
        self.local_int = local_int
        self.remote_int = remote_int
        self.cost = cost
        self.state = state
    #class functions to enable or disable link    
    def enable_link(self):
        self.state = "up"
        
    def disable_link(self):
        self.state = "down"

class show_adverts: #class to create object with functions to turn on or off adverts
    def __init__(self, state = "disable"):
        self.state = state

    def enable_advert(self):
        self.state = "enable"
        print(f'[INFO]---Display adverts enabled')

    def disable_advert(self):
        self.state = "disable"
        print(f'[INFO]---Display adverts disabled')

#Functions
def start_routing():    #function to enable Distance vector algorithm to run on received routes and also to send adverts
    if R.state == "started":
        pass
    else:
        R.state = "started"
        create_dvDBList() # create DV Database to be sent out all interfaces
        print("Routing started")

def stop_routing(): #function to disable Distance vector algorithm from running on received routes and also to stop sending adverts
    if R.state == "stopped":
        pass
    else:
        R.state = "stopped"
        dvDBList = []
        print("[INFO]---Routing Protocol stopped")

def show_routing_table(): #Prints routing table
    if R.state == "started" and dvDBList != []: #if routing is not running or DV database is empty, skip
        print(f"------Router R{R.name} Routing Table------")
        print("|   Destination   |   Cost   |   Next Hop   |")
        for i in range(len(dvDBList)):
            try:
                print(f"|       {dvDBList[i][0]}        |     {dvDBList[i][1]}    |     {dvDBList[i][3]}    |")
            except:
                pass
    else:
        print(f"------Router R{R.name} Routing Table------")
        print("|   Destination   |   Cost   |   Next Hop   |")
        print("\n[INFO]---Routing Protocol is not running")
    
def update_dv_database(dvUpdate):   #updates dv table to update routing table
    if R.state == "started":
        for i in dvUpdate:
            if i not in dvDBList: #tests if route already exists in the DV database. If not, appends. It it exists, it skips
                dvDBList.append(i)
        if show_adverts1.state == "enable":
            print(f"[INFO]---Distance Vector Database Updated")
        else:
            pass
    else:
        pass

def create_dvDBList():  #creates initial route table with neighbors
    for i in range(len(interfaceList)):
        dv_object1 = dv_object(neighborDBList[i].name,interfaceList[i].cost,interfaceList[i].name,R.name)
        dvDBList.append([dv_object1.destination,dv_object1.cost, dv_object1.interface, dv_object1.source_router])

def run_DV(dvList): #Computes best path with DV algorithm. It accepts DV database List created with the "create_dvDBList" function
    #Remove dead routes. If link to router route was learnt from is down remote the route from the DV table
    """for i in range(len(neighborDBList)):
        if neighborDBList[i].state == "down":
            for k in range(len(dvList)):
                try:
                    if dvList[k][3] == neighborDBList[i].name:
                        dvList.pop(k)
                    else:
                        pass
                except:
                    pass"""

    #1. remove routes pointing to self
    for i in range(len(dvList)):
        try:
            if dvList[i][0] == R.name:  #if this router's name is the source router of the received route, pop it from the list or received routes
                dvList.pop(i)
        except:
            pass
    dvList.sort()

    #2. remove duplicates and keep best routes. This prevent loops which can infinitely inclrease the cost of incoming routes (split horizon)
    b = set([]) #use set to remove duplicates
    dvIndex = []
    k = 0
    for i in dvList:
        dvIndex.append([k,i[0]])
        k += 1

    dvSet = set([])
    n = []

    dvIndex.sort()  #sort to get least cost routes to the top of the route list
    deleteList = []

    for i in dvList:
        dvSet.add(i[0])
    dvSet = list(dvSet)
    dvSet.sort()

    for i in dvList:
        n.append(i[0])

    #print(dv)

    for k in dvSet:
        if n.count(k) > 1:
            for i in dvIndex:
                if k == i[1]:
                    if k in b:
                        #print(f"{k} already in b")
                        #print(f"{dvList[i[0]]} removed")
                        deleteList.append(dvList[i[0]])
                    else:
                        b.add(k)
                else:
                    pass
    #print(deleteList)
    deleteList.sort()
    for x in deleteList:
        if x in dvList:
            dvList.remove(x)
    #print(dv)
    update_dv_database(dvList)
    
def start_router(): #sets router state to 'started' and starts listening and sending of DV database
    R.state = "started"
    print(f"[INFO]---Routing on R{R.name} has {R.state}")

def stop_router():
    R.state = "stopped"
    print(f"[INFO]---Routing on R{R.name} has {R.state}")

def start_menu():
    #Interfactive Command line interface
    if __name__ == '__main__':    
        sleeptime = 30
        deadtime = sleeptime + 10
    print("Welcome to JerryOS. Run \"help\" for list of commands, \"quit\" to quit")
    while True:
        command = input(f"R{R.name} >> ").lower()
        if command == "quit":
            break
        elif command == "help":
            print("quit ----- Quit the program")
            print("help ----- Display command list")
            print("interface ----- Enter interface configuration mode")
            print("show int config ----- Show configuration of interfaces")
            print("stop all int ----- Stop all interfaces")
            print("start all int ----- Start all interfaces")
            print("start routing prot ----- Start routing protocol")
            print("stop routing prot ----- Stop routing protocol")
            print("show all config ----- Display the status of all virtual interfaces, links and the status of the routing protocol")
            print("show route adverts ----- Start displaying incoming and outgoing routing advertisements ")
            print("hide route adverts ----- Stop displaying incoming and outgoing routing advertisements ")
            print("show route table ----- Print current routing table")
            print("show links ----- Show link config")
            print("save config ----- Save config to file")
            print("load config ----- Load config from file")
            print("change advert intervals ---- Change intervals between sending advertisements")

        elif command == "show int config":
            print("--------Current Interface Configuration--------")
            for i in range(len(interfaceList)):
                print("Name:",interfaceList[i].name," State:",interfaceList[i].state," Cost:",interfaceList[i].cost)
        elif command == "interface":
            print("Enter interface name or \"exit\" to exit interface configuration")
            while True:
                intChoice = input(f"R{R.name} >> Interface >> ")
                if intChoice == str(interface1.name):
                    print("Enter \"enable\" to enable the interface. Enter \"disable\" to disable the interface. \"exit\" to exit this interface")
                    while True:
                        intState = input(f"R{R.name} >> Interface {intChoice} >> ")
                        if intState == "enable":
                            if interface1.state == "up":
                                print(f"[INFO]---Interface {intChoice} is already enabled")
                            else:
                                interface1.start_int()
                        elif intState == "disable":
                            if interface1.state == "down":
                                print(f"[INFO]---Interface {intChoice} is already disabled")
                            else:
                                interface1.stop_int()
                        elif intState == "help":
                            print("Enter \"enable\" to enable the interface. Enter \"disable\" to disable the interface. \"exit\" to exit this interface")
                        elif intState == "exit":
                            break
                        else:
                            print("Enter \"enable\" or \"disable\"")

                elif intChoice == str(interface2.name):
                    print("Enter \"enable\" to enable the interface. Enter \"disable\" to disable the interface. \"exit\" to exit this interface")
                    while True:
                        intState = input(f"R{R.name} >> Interface {intChoice} >> ")
                        if intState == "enable":
                            if interface2.state == "up":
                                print(f"[INFO]---Interface {intChoice} is already enabled")
                            else:
                                interface2.start_int()
                        elif intState == "disable":
                            if interface2.state == "down":
                                print(f"[INFO]---Interface {intChoice} is already disabled")
                            else:
                                interface2.stop_int()
                        elif intState == "help":
                            print("Enter \"enable\" to enable the interface. Enter \"disable\" to disable the interface. \"exit\" to exit this interface")
                        elif intState == "exit":
                            break
                        else:
                            print("[ERROR]---Enter \"enable\" or \"disable\"")
                elif intChoice == str(interface3.name):
                    print("Enter \"enable\" to enable the interface. Enter \"disable\" to disable the interface. \"exit\" to exit this interface")
                    while True:
                        intState = input(f"R{R.name} >> Interface {intChoice} >> ")
                        if intState == "enable":
                            if interface3.state == "up":
                                print(f"[INFO]---Interface {intChoice} is already enabled")
                            else:
                                interface3.start_int()
                        elif intState == "disable":
                            if interface3.state == "down":
                                print(f"[INFO]---Interface {intChoice} is already disabled")
                            else:
                                interface3.stop_int()
                        elif intState == "help":
                            print("Enter \"enable\" to enable the interface. Enter \"disable\" to disable the interface. \"exit\" to exit this interface")
                        elif intState == "exit":
                            break
                        else:
                            print("[ERROR]---Enter \"enable\" or \"disable\"")
                elif intChoice == "exit":
                    break
                else:
                    print("[ERROR]---Interface does not exist. Run \"show int config\" to display interfaces")
        elif command == "stop all int":
            for i in range(len(interfaceList)):
                if interfaceList[i].state == "down":
                    print(f"[INFO]---Interface {interfaceList[i].name} state is already down. No change done")
                else:
                    interfaceList[i].stop_int()
        elif command == "start all int":
            for i in range(len(interfaceList)):
                if interfaceList[i].state == "up":
                    print(f"[INFO]---Interface {interfaceList[i].name} state is already up. No change done")
                else:
                    interfaceList[i].start_int()
        elif command == "start routing prot":
            if R.state == "started":
                print("[INFO]---Routing protocol is already started")
            else:
                start_router()
                start_routing()
        elif command == "stop routing prot":
            if R.state == "stopped":
                print("[INFO]---Routing protocol is already stopped")
            else:
                stop_router()
                stop_routing()
        elif command == "save config":
            pass
            #Use python's config parser to write to .ini file
        elif command == "change advert intervals":
            print(f'Enter advert interval. Default value is 30 secs')
            sleeptime = float(input(">> "))
            deadtime = sleeptime + 10
        elif command == "load config":
            pass
        elif command == "show route table":
            show_routing_table()
            #Use python's config parser to read from .ini file
        elif command == "show" or command == "start" or command == "stop" or command == "hide":
            print("[ERROR]---Incomplete Command. Run \"help\" for list of commands")
        elif command == "show route adverts":
            if show_adverts1.state == "enable":
                print("[INFO]---Showing adverts already")
            else:
                show_adverts1.enable_advert()
        elif command == "hide route adverts":
            if show_adverts1.state == "disable":
                print("[INFO]---Adverts already not showing")
            else:
                show_adverts1.disable_advert()
        elif command == "show all config":
            print(f"-----Running Configuration - R{R.name}------")
            print(f"Routing Protocol is {R.state}")
            print(f"Adverts Interval: {sleeptime}secs")
            print(f"Dead time: {deadtime}secs")
            print(f"--------------Interfaces--------------")
            for i in range(len(interfaceList)):
                print(f"Interface {interfaceList[i].name}. State: {interfaceList[i].state}. Cost:{interfaceList[i].cost}")
            print("\n")
            print(f"--------------Links---------------")
            for i in range(len(linkList)):
                print(f"Link to R{neighborDBList[i].name}: State: {linkList[i].state}")
        elif command == "show links":
            print("-------------Links-------------")
            for i in range(len(linkList)):
                print(f"Link to R{linkList[i].remote_node}: Local Interface: {linkList[i].local_int}. Remote Interface: {linkList[i].remote_int}. State: {linkList[i].state}")
        elif command == "save config":  #https://docs.python.org/3/library/configparser.html
            save_config()
        elif command == "load config":
            load_config()
        else:
            print("[ERROR]---Unrecognized Command. Run \"help\" to see list of commands")

def listen(localPort,serverSocket): #listen for incoming adverts
    while listening:
        if interfaceDict[str(localPort)].state == "up" and R.state == "started":
            if show_adverts1.state == "enable":
                print('[INFO]---Listening on port',localPort)
            else:
                pass
            data, remoteSocket = serverSocket.recvfrom(4096)
            data.decode()
            if data:
                #if data was received from remoteSocket, then neighbor on this link is up. Reset neighbor's counter to 40
                neighborStateDict[str(remoteSocket[1])[0:2]] = "up"     #set neighbor state to up since data was received from its port
                neighborCounterDict[str(remoteSocket[1])[0:2]] = deadtime   #reset dead timer on this remote interface
                linkDict[str(remoteSocket[1])[0:2]][0].state = "up" #set remote interface to up if it was down due to dead timer timeout
                if show_adverts1.state == "enable": #show notification of incoming advert if displaying adverts is enabled
                    print(f"Received advert from {remoteSocket}")
                else:
                    pass
                data = loads(data.decode())
                for key in data:
                    for i in range(len(data[key])):
                        data[key][i][1] += interfaceDict[str(localPort)].cost   #update the cost of incoming routes to account for links to non neighbor routers
                    run_DV(data[key])
                    if dvDBList != []:
                        run_DV(dvDBList)
                #response = dumps({str(R.name):dvDBList})
                #sent = serverSocket.sendto(response.encode(), remoteSocket)
        else:
            pass
        if dvDBList == []:  #create initial route table incase it is empty to prevent index out of range exception during iteration to print out routing table
            create_dvDBList()

def send(serverSocket,remotePort):  #send adverts to remote port on the link at regular intervals (default 30secs)
    while sending:
        if interfaceDict[str(serverSocket.getsockname()[1])].state == "up" and R.state == "started":    #test that routing is started and interface is up
            if show_adverts1.state == "enable":
                print(f"Sending update to {remotePort}")
            else:
                pass
            message = dumps({str(R.name):dvDBList}) #dump data to json before sending to neighbor
            sent = serverSocket.sendto(message.encode(), ('localhost',remotePort)) # send advert to neighbor
            sleep(sleeptime)    #wait to send the next route advert (30secs)
        else:
            pass

def timer():    #timer function to age links which are not receiving updates to remove them from the routing table
    while True:
        sleep(1)
        for i in neighborCounterDict:
            if neighborStateDict[i] == "down":
                pass
            else:
                if neighborCounterDict[i] > 0:
                    neighborCounterDict[i] = neighborCounterDict[i] - 1 #reduce timer by 1 each second
                    #print(neighborCounterDict[i])
                else:
                    if neighborStateDict[i] == "down":  #set nighbor state to down when timer expires
                        pass
                    else:
                        neighborStateDict[i] = "down"
                        for k in range(len(linkList)):
                            if linkList[k].remote_node == int(i):
                                linkList[k].state = "down"  #set link state to 'down' when timer expires
                                linkDict[i][0].state = "down"
                        #print(neighborStateDict[i])

def create_link_Dict(): #create dictionary out of the list of Links to use in listen() and timer() to set the state of the link to up or down
    for i in range(len(linkList)):
        #linkDict[str(linkList[i].remote_node)] = [linkList[i].local_node,linkList[i].remote_node,linkList[i].local_int,linkList[i].remote_int,linkList[i].cost,linkList[i].state]
        linkDict[str(linkList[i].remote_node)] = [linkList[i]]

def save_config():  #write config to .ini file
    config['Configuration'] = {'router.name': R.name,'interface1.name' : interface1.name,'interface2.name' : interface2.name,'interface3.name' : interface3.name,'interface1.cost' : interface1.cost,'interface2.cost' : interface2.cost,'interface3.cost' : interface3.cost,'neighbor1.name' : neighbor1.name,'neighbor2.name' : neighbor2.name,'neighbor3.name' : neighbor3.name,'neighbor1.interface' : neighbor1.interface,'neighbor2.interface' : neighbor2.interface,'neighbor3.interface' : neighbor3.interface,'sleeptime' : sleeptime,'deadtime' : deadtime,'interface1.state' : interface1.state,'interface2.state' : interface2.state,'interface3.state' : interface3.state}
    with open('./R'+str(R.name)+'.ini', 'w') as f:
        config.write()


def load_config():  #load config from .ini file
    parser.read('R'+str(R.name)+'.ini')
    R.name = parser.getint('Configuration', 'router.name')
    interface1.name = parser.getint('Configuration', 'interface1.name')
    interface2.name = parser.getint('Configuration', 'interface2.name')
    interface3.name = parser.getint('Configuration', 'interface3.name')
    interface1.cost = parser.getint('Configuration', 'interface1.cost')
    interface2.cost = parser.getint('Configuration', 'interface2.cost')
    interface3.cost = parser.getint('Configuration', 'interface3.cost')
    neighbor1.name = parser.getint('Configuration', 'neighbor1.name')
    neighbor2.name = parser.getint('Configuration', 'neighbor2.name')
    neighbor3.name = parser.getint('Configuration', 'neighbor3.name')
    neighbor1.interface = parser.getint('Configuration', 'neighbor1.interface')
    neighbor2.interface = parser.getint('Configuration', 'neighbor2.interface')
    neighbor3.interface = parser.getint('Configuration', 'neighbor3.interface')
    sleeptime = parser.getint('Configuration', 'sleeptime')
    deadtime = parser.getint('Configuration', 'deadtime')
    interface1.state = parser.getint('Configuration', 'interface1.state')
    interface2.state = parser.getint('Configuration', 'interface2.state')
    interface3.state = parser.getint('Configuration', 'interface3.state')    

R = router(10)  #create router instance
sending = True  #set senidng to True for use in send() function
listening = True    #set listeneing to True for use in listen() function
interface1 = interface(10001,1,"down")  #create interface instances, default state is down until enabled on the CLI
interface2 = interface(10002,2,"down")
interface3 = interface(10003,4,"down")

#create neigbor instances. Set counter to 40s. If counter gets to zero, neighbor will be considered down and link to it will be down
neighbor1 = neighbor(20,20001,"down")
neighbor2 = neighbor(30,30001,"down")
neighbor3 = neighbor(50,50001,"down")

interfaceList = [interface1,interface2,interface3]
interfaceDict = {str(interface1.name):interface1,str(interface2.name):interface2,str(interface3.name):interface3} # Used to get cost of interface to be added to received DV database List
neighborDBList = [neighbor1,neighbor2,neighbor3]
neighborCounterDict = {str(neighbor1.name):neighbor1.counter,str(neighbor2.name):neighbor2.counter,str(neighbor3.name):neighbor3.counter} # Used to set the counter of the neighbors
neighborStateDict = {str(neighbor1.name):neighbor1.state,str(neighbor2.name):neighbor2.state,str(neighbor3.name):neighbor3.state}

#create link instances. Default state is down until enabled in listen() function
link1 = link(R.name,neighbor1.name,interface1.name,neighbor1.interface,interface1.cost,"down")
link2 = link(R.name,neighbor2.name,interface2.name,neighbor2.interface,interface2.cost,"down")
link3 = link(R.name,neighbor3.name,interface3.name,neighbor3.interface,interface3.cost,"down")
linkList = [link1,link2,link3]  #create link list for use in listen()
linkDict = {}   #create link dictionary for use in listen()
dvDBList = [] # DV List before addting to Dict for sending to neighbor
routingTableList = [] # Empty routing table before DV is used to extend it

#create_routing_table(neighborDBList) # Build routing table from neighbor List
create_link_Dict() # create Link Dictionary to use in listen function to set link state
show_adverts1 = show_adverts("disable") # Disable showing incoming and outgoing adverts
create_dvDBList()

#Local ports. One for each interface
serverPort1 = interface1.name
serverPort2 = interface2.name
serverPort3 = interface3.name

#Remote ports. One for each neighbor
remotePort1 = neighbor1.interface
remotePort2 = neighbor2.interface
remotePort3 = neighbor3.interface

#create sockets and bind to each of the local ports. One socket per local port (serverPort). Then set them to nonblocking and make them resuable
serverSocket1=socket(AF_INET, SOCK_DGRAM)
serverAddress1 = ('localhost', serverPort1)
serverSocket1.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket1.bind(serverAddress1)

serverSocket2=socket(AF_INET, SOCK_DGRAM)
serverAddress2 = ('localhost', serverPort2)
serverSocket2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket2.bind(serverAddress2)

serverSocket3=socket(AF_INET, SOCK_DGRAM)
serverAddress3 = ('localhost', serverPort3)
serverSocket3.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket3.bind(serverAddress3)

#Create thread to run CLI
startConsole = Thread(target=start_menu)
#Create threads for each port to enable the router listen on all ports "at the same time" and send to the neighbors "at the same time". Set daemon to True to enable graceful dying of the thread
listenPort1 = Thread(target=listen, args=[serverPort1, serverSocket1], daemon = True)
listenPort2 = Thread(target=listen, args=[serverPort2, serverSocket2], daemon = True)
listenPort3 = Thread(target=listen, args=[serverPort3, serverSocket3], daemon = True)
sendPort1 = Thread(target=send, args=[serverSocket1,remotePort1], daemon = True)
sendPort2 = Thread(target=send, args=[serverSocket2,remotePort2], daemon = True)
sendPort3 = Thread(target=send, args=[serverSocket3,remotePort3], daemon = True)
#Create thread to handle countdown
timer1 = Thread(target=timer, daemon=True)
#start threads
startConsole.start()
listenPort1.start()
listenPort2.start()
listenPort3.start()
sendPort1.start()
sendPort2.start()
sendPort3.start()
timer1.start()