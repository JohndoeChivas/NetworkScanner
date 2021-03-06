import sys
import os 
import netifaces
from Colors import Colors
from termcolor import colored
import colorama
import random
import ipaddress 
from scapy.all import ARP, Ether, srp
import nmap3
import stun
import publicip
from ip2geotools.databases.noncommercial import DbIpCity
import  socket
from Target import Target


#colors = list(vars(colorama.Fore).values())




class Network:

    def __init__(self):
        self.colors = Colors()
        self.color = colorama.Fore.GREEN
        self.interfaces = netifaces.interfaces()
        self.routers = netifaces.gateways()
        self.netmask = None
        self.network = None
        self.interface = None
        self.ip = None
        self.mac = None
        self.router = None
        self.country = None
        self.city = None
        self.lat = None
        self.lng = None
        self.region = None
        self.target = None
        self.ipTarget = None
        self.countryTarget = None
        self.cityTarget = None
        self.regionTarget = None
        self.latTarget = None
        self.lngTarget = None
        self.run = True
        self.ips = []
        self.macs = []
        self.os = []
        self.public = None

    def getNetwork(self):
        if self.network is None : 
            if self.getNetmask() :
                try :
                    self.network = ipaddress.ip_network(self.getIP()+'/'+self.getNetmask(), strict=False)
                except ValueError :
                    self.network = 'no network'
        return self.network
        
    def getPublicIp(self):
        if self.public is None :
            self.public = stun.get_ip_info()[1]
            if self.public is None :
                self.public = str(publicip.get())
                
        
        return self.public

            
        
    def getIP(self):
        if self.ip is None :
            try:
                ipkey = netifaces.ifaddresses(self.interface)
                self.ip = (ipkey[netifaces.AF_INET][0]['addr'])
            except KeyError:
                self.ip ="No IP"
        return self.ip
    
    def getNetmask(self):
        if self.netmask is None:
            try:
                ipkey = netifaces.ifaddresses(self.interface)
                self.netmask = ipkey[netifaces.AF_INET][0]['netmask']
            except KeyError:
                self.netmask ="No netmask"

        return self.netmask

    def getMAC(self):
        if self.mac is None :
            
            ipkey = netifaces.ifaddresses(self.interface)
            
            try:
                self.mac = (ipkey[netifaces.AF_LINK][0]['addr'])
            except KeyError :
                self.mac = ipkey[10][0]['addr']
                

        return self.mac
    
    def getInterface(self):
        if self.interface is None : 
            self.defineInterface()
        return self.interface
    
    def getGateway(self):
        if self.router is None :
            self.router = (self.routers['default'][netifaces.AF_INET][0])
        return self.router

    def getLocation(self):
        if self.country is None :
            location =  DbIpCity.get(self.getPublicIp(), api_key='free')
            self.country = location.country
            self.city = location.city
            self.region = location.region
            self.lat = location.latitude
            self.lng = location.longitude
        return self.country,self.city,self.region,self.lat,self.lng

    

    def resetConfig(self):
        self.network = None
        self.public = None 
        self.ip = None
        self.netmask = None
        self.mac = None
        self.country = None
        self.city = None
        self.region = None
        self.lat = None
        self.lng = None
            

    def showInterface(self):
        print("[*] Searching...")
        print('\r\n')
        cpt = 1
        for interface in self.interfaces :
            text = '['+str(cpt)+'] '+"Detected interface"+str(cpt)+': '+str(interface)
            print(text)
            cpt += 1
        print('\r\n')
        
    def showMACAddress(self):
        if self.interface:
            ipkey = netifaces.ifaddresses(self.interface)
            self.mac = (ipkey[netifaces.AF_LINK][0]['addr'])
            print('[*] Your MAC address on '+self.interface+' interface is '+self.getMAC())

    
    def showIPadresse(self):
        if self.interface:
            ipkey = netifaces.ifaddresses(self.interface)
            self.ip = (ipkey[netifaces.AF_INET][0]['addr'])
            print('[*] Your IP on '+self.interface+' interface is '+self.getIP())


    def showGateway(self):
        if self.routers :
            self.router = (self.routers['default'][netifaces.AF_INET][0])
            print('[*] Your default gateway is '+self.getGateway()+'.')

    def defineInterface(self):
        self.showInterface()
        self.resetConfig()
        #print('[*] Choose your interface. (For example type 1 for '+self.interfaces[0]+' interface): ',self.color)
        choiceInterface = input('[*] Choose your interface. (For example type 1 for '+self.interfaces[0]+' interface): ')
        try:
            choiceInterface = int(choiceInterface) - 1
            interface = self.interfaces[choiceInterface] 
            if interface in self.interfaces and choiceInterface >= 0 :
                self.interface = interface
                print(interface+' => ON\r\n')
            else: 
                print('This interface doesn\'t exist\r\n')

        except IndexError:
            print('This interface doesn\'t exist\r\n')
        except ValueError:
            print('Please read before typing..\r\n')
    
    def getResume(self):
        self.colors.print_random_color('[INFO NETWORK INTERFACE]\r\n')
        self.color = None
        print('INTERFACE: '+self.getInterface())
        print('LOCAL IP: '+self.getIP())
        print('MAC: '+self.getMAC())
        print('NETMASK: '+self.getNetmask())
        print('GATEWAY: '+self.getGateway())
        print('NETWORK: '+str(self.getNetwork()))
        print('PUBLIC IP: '+self.getPublicIp())
        print('COUNTRY: '+self.getLocation()[0])
        print('CITY: '+self.getLocation()[1])
        print('REGION: '+self.getLocation()[2])
        print('LATITUDE: '+str(self.getLocation()[3]))
        print('LONGITUDE: '+str(self.getLocation()[4]))
        print('\r\n')
    
    def scanNetwork(self):
        self.ips.clear()
        self.macs.clear()
        self.os.clear()
        cpt = 0
        nmap = nmap3.Nmap()
        ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=str(self.getNetwork())),timeout=2)
        for snd,rcv in ans:
            self.ips.append(rcv[ARP].psrc)
            self.macs.append(rcv[Ether].src)
        print('/!\ This operation may take a while')
        for ip in self.ips:
            print('[*] Searching OS for '+str(ip))
            resultnmap = nmap.nmap_os_detection(ip)
            try:
                self.os.append(resultnmap[0]['name'])

            except IndexError :
                self.os.append('')

        sizeIP = len(self.ips)
        sizeMAC = len(self.macs)
        print('\r\n')
        if sizeIP == sizeMAC :

            
            print('IP: '+' '*15+'MAC: '+' '*20+'OS: ')
            for i in range(sizeIP):
                print(self.ips[i]+' '*7+self.macs[i]+' '*7+self.os[i])
        
        print('\r\n')
       

    def askChoice(self):
        print('[Network Scanner] : What do you want do ? \r\n')
        print('[1]: Get resume of your network')
        print('[2]: Define your interface')
        print('[3]: Scan network')
        print('[4]: Find details target')
        print('[5]: Quit\r\n')
        answer = input('Your choice: ')
        print('\r\n')
        return answer

    
    def assumeChoice(self,choice):
        listChoice = ['1','2','3','4','5']
        if choice in listChoice :
            if choice == '1':
                self.getResume()
            if choice == '2':
                self.defineInterface()
            if choice == '3':
                self.scanNetwork()
            if choice == '4':
                target = Target()
                target.getResumeTarget()

            if choice == '5':
                print('[*] Bye...\r\n')
                self.run = False
                sys.exit(0)
        else:
            print('Bad choice, try again...\r\n')
    
    def start(self):
        print('\r\n')
        print('[*] For start, you have to define which interface you want use.')
        self.defineInterface()
        while self.run :
            choice = self.askChoice()
            self.assumeChoice(choice)




        



net = Network()
net.start()