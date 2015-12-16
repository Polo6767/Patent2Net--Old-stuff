# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 07:45:45 2015

@author: dreymond
"""

from multiprocessing import Process, Pool, Queue, Lock, JoinableQueue, freeze_support
import os

RequeteFolder = "..\\REQUESTS"
TempoFolderReq = "TEMPOREQ"



def SafeOpenWriteRequests(FileName, SavReq, TempoForderReq):
    #saving current file
    command = "copy /Y  ..\\requete.cql " + TempoForderReq+'\\' + SavReq
    os.system(command)
    try:    
        os.remove('..\\requete.cql')
    except:
        "print should put a request in folder... doing it for you"
    command = 'copy /Y ' +FileName +' ..\\requete.cql'
    os.system(command)
    print "done saving requete, replaced by", FileName    


def RestoreRequests(FileName, SavReq, TempoForderReq):
    #saving current file
    command = "copy /Y "+ TempoForderReq+'\\' + SavReq + ' ..\\requete.cql' 
    os.system(command)     
    os.remove(TempoForderReq+'\\' + SavReq)
    
    print "done restoring " , FileName," replacing by previous"   
    

if TempoFolderReq not in os.listdir('.'):
    os.makedirs(TempoFolderReq)
    
lstReq = [fic for fic in os.listdir(RequeteFolder) if fic.endswith('cql')] 
    
#    
#STEPS = dict()
#
#STEPS = { 1:"OPSGatherPatentsv2.exe", 
#            1.1: ["FormateExportDataTable.exe", "P2N-networksCit.exe", "P2N-networksMix.exe",
#                  "P2N-FreePlane.exe", "FormateExportBiblio.exe", "FormateExportAttractivityCartography.exe",
#                  "FormateExportCountryCartography.exe"],
#        2: "OPSGatherAugment-Families.exe",
#            2.1: ["FormateExportDataTableFamilies.exe", "FormateExportPivotTable.exe"],
#        3 :"OPSGatherContentsv2-Iramuteq.exe",
#            3.1: ["FusionCarrot2.exe", "FusionIramuteq2.exe"],
#        4:"Interface2.exe"
#        }
gatherers = ["OPSGatherPatentsv2.exe","OPSGatherAugment-Families.exe", "OPSGatherContentsv2-Iramuteq.exe"]
pretraite1 = "P2N-PreNetworks.exe"
traite1 = ["P2N-FreePlane.exe", "FormateExportBiblio.exe", "FormateExportAttractivityCartography.exe",
                  "FormateExportDataTable.exe","FormateExportCountryCartography.exe"]
NetProc = [ "P2N-Networks.exe", "P2N-NetworksJS.exe" ]
                   # these processing program can be launched after the first gatherer has ended
traite2 = ["FormateExportDataTableFamilies.exe", "FormateExportPivotTable.exe"] #same comment with second gatherer
traite3 = ["FusionCarrot2.exe"] # same again , "FusionIramuteq2.exe": this one is preocessed bu gatherContentsV2

Nets = ["CountryCrossTech", "CrossTech", "InventorsCrossTech", "Applicants_CrossTech", "Inventors",
 "ApplicantInventor", "Applicants", "References", "Citations", "Equivalents"]

if __name__ == '__main__':
    lock = Lock()
    freeze_support()
     # no max size for the moment
    QueueP2N = Pool (processes = 3)
    for req in lstReq:
#        try:
#            QueueP2N.apply(Gatherer (req)) # asynchronous mode impossible as  all programms uses requete.cql...
#        except:
        QueueGatherer = Pool (processes = 1)
        SafeOpenWriteRequests(RequeteFolder+"\\" +req, "requeteOld"+req, TempoFolderReq)    
        iterat = QueueGatherer.imap(os.system, gatherers)
        iterat.next()
        QueuePreNets = Pool (processes = 3)
        CommandsPreNets = []
        for net in Nets:
            CommandsPreNets.append(pretraite1 + " " + net) 
        QueuePreNets.map(os.system, CommandsPreNets)
        
        # PreNet should end **before** Nets process starts... this not appends always
        
        QueueForms = Pool (processes = 4)
        # I hope that formating process will slow sufficiently
        QueueForms.map(os.system, traite1)
        iterat.next()
        # nicer solution should implement a worker and mananger of process that allows to start when the previous process have finished
        QueueNets = Pool (processes = 4)
        
        QueueNets.map(os.system, traite1)
        CommandsNets = []
        for net in Nets:
            CommandsNets.append(NetProc[0] + " " + net) 
            CommandsNets.append(NetProc[1] + " " + net) 
        QueueNets.map(os.system, CommandsNets)
        
        QueueNets2 = Pool (processes = 2)
        QueueNets2.map(os.system, traite2)
        iterat.next()
        QueueNets3 = Pool (processes = 2)
        QueueNets3.map(os.system, traite3)
        os.system('.\\Interface2') # last program
    for req in lstReq:
        print req, " processed"
        
#