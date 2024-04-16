# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 12:09:59 2024

@author: Riccardo
"""

from datetime import datetime as Datetime
import datetime


#argomento 1: dati di entrata nel robot
RE=open('C:/Users/Riccardo/OneDrive - Alma Mater Studiorum Università di Bologna/Documents/Desktop/SCRIPT_PYTHON/2024_0325-041/Tag20240401.csv', 'r').readlines()

#argomento 2: dati di uscita dal robot (report QUARTI)
RU=open('C:/Users/Riccardo/OneDrive - Alma Mater Studiorum Università di Bologna/Documents/Desktop/SCRIPT_PYTHON/2024_0325-041/Quarti20240401.csv', 'r').readlines()

#argomento 3: dati di uscita dal robot (report LATTE)
RL=open('C:/Users/Riccardo/OneDrive - Alma Mater Studiorum Università di Bologna/Documents/Desktop/SCRIPT_PYTHON/2024_0325-041/Latte20240401.csv', 'r').readlines()

#argomenti 4: pesi delle vacche
PV=open('C:/Users/Riccardo/OneDrive - Alma Mater Studiorum Università di Bologna/Documents/Desktop/SCRIPT_PYTHON/2024_0325-041/Pesi20240401.csv', 'r').readlines()

#argomento 5: dati sniffer
SN1=open('C:/Users/Riccardo/OneDrive - Alma Mater Studiorum Università di Bologna/Documents/Desktop/SCRIPT_PYTHON/2024_0325-041/Robot1-03252024004000-04012024004000.csv', 'r')

#argomento 6: dati sniffer
SN2=open('C:/Users/Riccardo/OneDrive - Alma Mater Studiorum Università di Bologna/Documents/Desktop/SCRIPT_PYTHON/2024_0325-041/Robot2-03252024004000-04012024004000.csv', 'r')

#dizionario con IDvacca come chiave e peso come valore
Dpv={}
for pv in PV[1:]:
    line=pv.split(",")
    Dpv[line[0]]=line[1].strip()

############################# LAVORO SUL REPORT TAG #############################
Dre={}
TU={}
GIORNI=set([])
for re in RE[1:]:
    line=re.split(",")
    if line[1] not in Dre.keys():
        Dre[line[1]]=[]
    T=line[0].split()
    #manipola stringa della data
    data=T[0].split("/")
    giorno=int(data[0])
    mese=int(data[1])
    anno=int(data[2])
    #manipola stringa dell'orario
    orario=T[1].split(":")
    ora=int(orario[0])
    minuti=int(orario[1])
    secondi=int(orario[2])
    #costruisce l'oggetto datatime
    time_tag=Datetime(anno, mese, giorno, ora, minuti, secondi)
    #GIORNI dato utile per calcolo del basale)
    GIORNI.add(time_tag.date())
    Dre[line[1]].append(time_tag)
for k,v in Dre.items():
    Dre[k].sort()
####################################################################################
############################## LAVORO SUL REPORT QUARTI ###########################
Dru={}
for ru in RU[1:]:
    line=ru.split(";")
    if line[1] not in Dru.keys():
        Dru[line[1]]=[]
    T=line[0].split()
    #manipola stringa della data
    data=T[0].split("/")
    giorno=int(data[0])
    mese=int(data[1])
    anno=int(data[2])
    #manipola stringa dell'orario
    orario=T[1].split(":")
    ora=int(orario[0])
    minuti=int(orario[1])
    secondi=int(orario[2])
    #costruisce l'oggetto datatime
    time_quarti=Datetime(anno, mese, giorno, ora, minuti, secondi)
    Dru[line[1]].append(time_quarti)
for k,v in Dru.items():
    Dru[k].sort()

#################################################################################
################## LAVORO SUL REPORT LATTE ######################################

DinfoLatte={}
Dtime={}
ROBOT1_IMPEGNATO=set([])
ROBOT2_IMPEGNATO=set([])
Lvacche_robot1=[]
Lvacche_robot2=[]
for rl in RL[1:]:
    rl_dot=rl.replace(",",".")
    line=rl_dot.split(";")
    gruppo=line[5]
    #crea stringe info latte: lattazione,gg_mungitura,produzione_kg,grasso%,proteina%,lattosio%
    info_latte=line[2]+","+line[4]+","+line[7]+","+line[9]+","+line[10]+","+line[12]
    T=line[0].split()
    #manipola stringa della data
    data=T[0].split("/")
    giorno=int(data[0])
    mese=int(data[1])
    anno=int(data[2])
    #manipola stringa dell'orario
    orario=T[1].split(":")
    ora=int(orario[0])
    minuti=int(orario[1])
    secondi=int(orario[2])
    #costruisce l'ogtime_report_lattegetto datatime
    time_latte=Datetime(anno, mese, giorno, ora, minuti, secondi)
    Ltag=Dre[line[1]].copy()
    Lqua=Dru[line[1]].copy()
    Ltag.append(time_latte)
    Ltag.sort()
    pos_closest_tag=Ltag.index(time_latte)-1
    closest_tag=Ltag[pos_closest_tag]
    Lqua.append(time_latte)
    Lqua.sort()
    pos_closest_qua=Lqua.index(time_latte)-1
    closest_qua=Lqua[pos_closest_qua]
    if closest_tag < closest_qua:
        chiave=line[1]+","+str(closest_tag)+","+str(closest_qua)
    else:
        chiave=line[1]+",N.A.,"+str(closest_qua)
    DinfoLatte[chiave]=info_latte
    spr=closest_qua-closest_tag
    secondi_passati_nel_robot=int(spr.total_seconds())+1
    ogni_secondo=[]
    if gruppo != '2':
        Lvacche_robot1.append(line[1])
        for i in range(secondi_passati_nel_robot):
            sec=closest_tag + datetime.timedelta(seconds=i)
            ogni_secondo.append(sec)
            ROBOT1_IMPEGNATO.add(sec)
    else:
        Lvacche_robot2.append(line[1])
        for i in range(secondi_passati_nel_robot):
            sec=closest_tag + datetime.timedelta(seconds=i)
            ogni_secondo.append(sec)
            ROBOT2_IMPEGNATO.add(sec)
    Dtime[chiave]=ogni_secondo
##########################################################################################
############## LAVORO SUI DATI MOOLOGGER installato sul ROBOT1 #################################################

sn1=SN1.readline()
sn1=SN1.readline().replace('"','')
Dsn1={}
while sn1:
    line=sn1.split(",")
    if line[1]!="N.A":
        CH4=float(line[2])
        FLOW=float(line[5])
        misurazioneCH4=CH4*FLOW/60.0
        misurazioneCH4ppm=float(line[1])
        misutazioneCO2ppm=float(line[3])
        #manipola stringa della data
        T=line[0].split()
        data=T[0].split("/")
        giorno=int(data[1])
        mese=int(data[0])
        anno=int(data[2])
        #manipola stringa dell'orario
        orario=T[1].split(":")
        ora=int(orario[0])
        minuti=int(orario[1])
        ORARIO=orario[2].split(".")
        secondi=int(ORARIO[0])
        time_misurazioni_UTC=Datetime(anno, mese, giorno, ora, minuti, secondi)
        time_misurazioni_LOCALE=time_misurazioni_UTC+datetime.timedelta(seconds=7196)
        #qui eventualmente bisogna correggere per ora solare/legale
        Dsn1[time_misurazioni_LOCALE]=[misurazioneCH4,misurazioneCH4ppm,misutazioneCO2ppm]
    sn1=SN1.readline().replace('"','')

#################################################################################################################
############## LAVORO SUI DATI MOOLOGGER installato sul ROBOT2 #################################################

sn2=SN2.readline()
sn2=SN2.readline().replace('"','')
Dsn2={}
while sn2:
    line=sn2.split(",")
    if line[1]!="N.A":
        CH4=float(line[2])
        FLOW=float(line[5])
        misurazioneCH4=CH4*FLOW/60.0
        misurazioneCH4ppm=float(line[1])
        misutazioneCO2ppm=float(line[3])
        #manipola stringa della data
        T=line[0].split()
        data=T[0].split("/")
        giorno=int(data[1])
        mese=int(data[0])
        anno=int(data[2])
        #manipola stringa dell'orario
        orario=T[1].split(":")
        ora=int(orario[0])
        minuti=int(orario[1])
        ORARIO=orario[2].split(".")
        secondi=int(ORARIO[0])
        time_misurazioni_UTC=Datetime(anno, mese, giorno, ora, minuti, secondi)
        time_misurazioni_LOCALE=time_misurazioni_UTC+datetime.timedelta(seconds=7196)
        #qui eventualmente bisogna correggere per ora solare/legale
        Dsn2[time_misurazioni_LOCALE]=[misurazioneCH4,misurazioneCH4ppm,misutazioneCO2ppm]
    sn2=SN2.readline().replace('"','')
#############################################################################################

############################ BASALE ROBOT1 ####################################################
GG=[]
for g in GIORNI:
	GG.append(g)
GG.sort()
Dbasale1={}
for g in GG[:7]:
    sommaCH4=0
    sommaCH4ppm=0
    sommaCO2ppm=0
    c=0
    for k,v in Dsn1.items():
        if k.date() == g:
            if k not in ROBOT1_IMPEGNATO:
                sommaCH4=sommaCH4+float(v[0])
                sommaCH4ppm=sommaCH4ppm+float(v[1])
                sommaCO2ppm=sommaCO2ppm+float(v[2])
                c=c+1
    mediaCH4=float(sommaCH4)/float(c)
    mediaCH4ppm=float(sommaCH4ppm)/float(c)
    mediaCO2ppm=float(sommaCO2ppm)/float(c)
    Dbasale1[g]=str(mediaCH4)+","+str(mediaCH4ppm)+","+str(mediaCO2ppm)+","
############################ BASALE ROBOT2 ####################################################
GG=[]
for g in GIORNI:
	GG.append(g)
GG.sort()
Dbasale2={}
for g in GG[:7]:
    sommaCH4=0
    sommaCH4ppm=0
    sommaCO2ppm=0
    c=0
    for k,v in Dsn2.items():
        if k.date() == g:
            if k not in ROBOT2_IMPEGNATO:
                sommaCH4=sommaCH4+float(v[0])
                sommaCH4ppm=sommaCH4ppm+float(v[1])
                sommaCO2ppm=sommaCO2ppm+float(v[2])
                c=c+1
    mediaCH4=float(sommaCH4)/float(c)
    mediaCH4ppm=float(sommaCH4ppm)/float(c)
    mediaCO2ppm=float(sommaCO2ppm)/float(c)
    Dbasale2[g]=str(mediaCH4)+","+str(mediaCH4ppm)+","+str(mediaCO2ppm)+","
####################################################################################################
###################### RISULTATI ROBOT 1 ###########################################################
f=open("results.csv",'w')
f.write("IDvacca,DataOraEntrata,DataOraUscita,Robot,media_CH4mgm3*FLOW/sec,media_CH4ppm,media_CO2ppm,basale_CH4mgm3*FLOW/sec,basale_CH4ppm,basale_CO2ppm,peso,lattazione,gg_mungitura,produzione_kg,grasso%,proteina%,lattosio%,NOTE,c_ch4,c_ch4ppm,c_co2ppm\n")
for k,v in Dtime.items():
    info_latte=DinfoLatte[k]
    info_k=k.split(",")
    IDvacca=info_k[0]
    sommaCH4=0
    sommaCH4ppm=0
    sommaCO2ppm=0
    c_ch4=0
    c_ch4ppm=0
    c_co2ppm=0
    if IDvacca in Lvacche_robot1:
        GRUPPO='robot1'
        for vv in v:
            if vv in Dsn1.keys():
                giorno=vv.date()
                if giorno in Dbasale1.keys():
                    basale_ch4=Dbasale1[giorno].split(',')[0]
                    basale_ch4ppm=Dbasale1[giorno].split(',')[1]
                    basale_co2ppm=Dbasale1[giorno].split(',')[2]
                if float(Dsn1[vv][0])-float(basale_ch4) > 0:
                    sommaCH4=sommaCH4+float(Dsn1[vv][0]-float(basale_ch4))
                    c_ch4=c_ch4+1
                if float(Dsn1[vv][1])-float(basale_ch4ppm) > 0:
                    sommaCH4ppm=sommaCH4ppm+float(Dsn1[vv][1]-float(basale_ch4ppm))
                    c_ch4ppm=c_ch4ppm+1
                if float(Dsn1[vv][2])-float(basale_co2ppm) > 0:
                    sommaCO2ppm=sommaCO2ppm+float(Dsn1[vv][2]-float(basale_co2ppm))
                    c_co2ppm=c_co2ppm+1
    elif IDvacca in Lvacche_robot2:
        GRUPPO='robot2'
        for vv in v:
            if vv in Dsn2.keys():
                giorno=vv.date()
                if giorno in Dbasale2.keys():
                    basale_ch4=Dbasale2[giorno].split(',')[0]
                    basale_ch4ppm=Dbasale2[giorno].split(',')[1]
                    basale_co2ppm=Dbasale2[giorno].split(',')[2]
                if float(Dsn2[vv][0])-float(basale_ch4) > 0:
                    sommaCH4=sommaCH4+float(Dsn2[vv][0]-float(basale_ch4))
                    c_ch4=c_ch4+1
                if float(Dsn2[vv][1])-float(basale_ch4ppm) > 0:
                    sommaCH4ppm=sommaCH4ppm+float(Dsn2[vv][1]-float(basale_ch4ppm))
                    c_ch4ppm=c_ch4ppm+1
                if float(Dsn2[vv][2])-float(basale_co2ppm) > 0:
                    sommaCO2ppm=sommaCO2ppm+float(Dsn2[vv][2]-float(basale_co2ppm))
                    c_co2ppm=c_co2ppm+1
    info_basale="N.A.,N.A.,N.A.,"
    if c_ch4>0 or c_ch4ppm>0 or c_co2ppm>0:
        data=v[0].date()
        info_basale="N.A.,N.A.,N.A.,"
        for kb in Dbasale1.keys():
            if data == kb:
                if IDvacca in Lvacche_robot1:
                    info_basale=Dbasale1[kb]
                elif IDvacca in Lvacche_robot2:
                    info_basale=Dbasale2[kb]
        try:
            mediaCH4=float(sommaCH4)/float(c_ch4)
        except: mediaCH4 = 'N.A.'
        try:
            mediaCH4ppm=float(sommaCH4ppm)/float(c_ch4ppm)
        except: mediaCH4ppm = 'N.A.'
        try:
            mediaCO2ppm=float(sommaCO2ppm)/float(c_co2ppm)
        except: mediaCO2ppm = 'N.A.'
        if IDvacca in Dpv.keys():
            f.write(k+","+GRUPPO+","+str(mediaCH4)+","+str(mediaCH4ppm)+","+str(mediaCO2ppm)+","+info_basale+Dpv[IDvacca]+","+info_latte+",N.A.,"+str(c_ch4)+","+str(c_ch4ppm)+","+str(c_co2ppm)+"\n")
        else:
            f.write(k+","+GRUPPO+","+str(mediaCH4)+","+str(mediaCH4ppm)+","+str(mediaCO2ppm)+","+info_basale+"N.A.,"+info_latte+",N.A.,"+str(c_ch4)+","+str(c_ch4ppm)+","+str(c_co2ppm)+"\n")
#        if c < 120:
#           f.write(",ATTENZIONE:rilevamento < 120 sec\n")
#        elif c > 2000:
#           f.write(",ATTENZIONE:rilevamento > 2000 sec\n")
#        else:
#            f.write("\n")
    else:
        if IDvacca in Dpv.keys():
            f.write(k+","+GRUPPO+",N.A.,N.A.,N.A.,"+info_basale+Dpv[IDvacca]+","+info_latte+",ATTENZIONE:nessun rilevamento,N.A,N.A.,N.A.\n")
        else:
            f.write(k+","+GRUPPO+",N.A.,N.A.,N.A.,"+info_basale+"N.A.,"+info_latte+",ATTENZIONE:nessun rilevamento,N.A,N.A.,N.A.\n")
f.close()
