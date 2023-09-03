#2023-08-27


# -*- coding: utf-8 -*-
import csv
import pprint
import math
import os
from functools import singledispatch


class Setting:
    FROM          = "RJCB" #出発空港
    TO            = "RJCK" #到着空港

    ClimbOAT      = 17   # 上昇時外気温度
    DescentOAT    = (15,)   # 降下時外気温度
    FE            = 500  # 飛行場標点標高[ft]
    V_climb       = 111  # 上昇時速度[kt](CAS)
    V_cruise      = 142  # 巡航速度[kt](CAS)
    V_descent     = 142  # 降下時速度[kt](CAS)
    V_Vrep        = 121
    Cruise_ALT    = 3500 # 巡航高度[ft]
    DescentRate   = 500  # 降下率[fpm]
    Variation     = 9    # 磁方位の偏差(西が+, 東が-)

    FuelCruise    = 15
    FuelDescent   = 12   # 降下時の燃料消費量[GPH]

    ClimbWind     = (50,7) #上昇中の風向風速
    DescentWind   = (10,8) #降下中の風向風速



VrepALT = {"白糠":2200}

Time_to_Climb_Ref = [#気圧高度[ft]、外気温度、上昇時対気速度[KIAS]、上昇率[fpm]、時間[min]、燃料[gal]、距離[nm]
                    (0,               15,               108,       1251,        0,        0,      0),
                    (1000,            13,               107,       1194,      0.8,      0.3,    1.5),
                    (2000,            11,               107,       1136,      1.7,      0.7,    3.1),
                    (3000,             9,               106,       1079,      2.6,      1.0,    4.8),
                    (4000,             7,               105,       1021,      3.6,      1.4,    6.7),
                    (5000,             5,               104,        964,      4.7,      1.7,    8.6),
                    (6000,             3,               104,        906,      5.8,      2.1,   10.7),
                    (7000,             1,               103,        849,      6.9,      2.5,   12.9)
                    ]


def ClimbPerformance(FE, Cruise_ALT, OAT): #引数：（出発地のFE、巡航高度、外気温度）→ 返す値：(上昇時間, 消費燃料) 
    i = 1
    while True:
        if FE <= Time_to_Climb_Ref[i][0]:
            break
        else:
            i += 1

    ISATemp = Time_to_Climb_Ref[i][1] * (FE - Time_to_Climb_Ref[i-1][0]) / 1000 + Time_to_Climb_Ref[i-1][1] * (Time_to_Climb_Ref[i][0] - FE) / 1000

    time1 = Time_to_Climb_Ref[i][4] * (FE - Time_to_Climb_Ref[i-1][0]) / 1000 + Time_to_Climb_Ref[i-1][4] * (Time_to_Climb_Ref[i][0] - FE) / 1000
    fuel1 = Time_to_Climb_Ref[i][5] * (FE - Time_to_Climb_Ref[i-1][0]) / 1000 + Time_to_Climb_Ref[i-1][5] * (Time_to_Climb_Ref[i][0] - FE) / 1000
    dist1 = Time_to_Climb_Ref[i][6] * (FE - Time_to_Climb_Ref[i-1][0]) / 1000 + Time_to_Climb_Ref[i-1][6] * (Time_to_Climb_Ref[i][0] - FE) / 1000

    i = 1
    while True:
        if Cruise_ALT <= Time_to_Climb_Ref[i][0]:
            break
        else:
            i += 1
    
    time2 = Time_to_Climb_Ref[i][4] * (Cruise_ALT - Time_to_Climb_Ref[i-1][0]) / 1000 + Time_to_Climb_Ref[i-1][4] * (Time_to_Climb_Ref[i][0] - Cruise_ALT) / 1000
    fuel2 = Time_to_Climb_Ref[i][5] * (Cruise_ALT - Time_to_Climb_Ref[i-1][0]) / 1000 + Time_to_Climb_Ref[i-1][5] * (Time_to_Climb_Ref[i][0] - Cruise_ALT) / 1000
    dist2 = Time_to_Climb_Ref[i][6] * (Cruise_ALT - Time_to_Climb_Ref[i-1][0]) / 1000 + Time_to_Climb_Ref[i-1][6] * (Time_to_Climb_Ref[i][0] - Cruise_ALT) / 1000

    alpha = (OAT - ISATemp) // 10

    time = time2 - time1
    fuel = fuel2 - fuel1
    dist = dist2 - dist1

    if alpha > 0:
        time *= ( 1 + alpha / 10)
        fuel *= ( 1 + alpha / 10)
        dist *= ( 1 + alpha / 10)

    return (time, fuel)




    
class Legs:
    #地点間の距離とTC（真方位）をまとめる。
    #地点1-地点2 = (距離[nm], TC（真方位）[deg], "地点1", "地点2", 偏差, SEA[ft])

    RJCB_Moiwabashi      = (13, 72, "RJCB", "茂岩橋", 9, 2000)
    Moiwabashi_RJCB      = (13,  252, "茂岩橋", "RJCB", 9, 2000)

    Moiwabashi_Otsu      = (9.5, 139, "茂岩橋", "大津", 9, 1600)
    Otsu_Moiwabashi      = (9.5, 319, "大津", "茂岩橋", 9, 1600)

    Otsu_Shiranuka       = (24, 49, "大津", "白糠", 9, 2100)
    Shiranuka_Otsu       = (24, 229, "白糠", "大津", 9, 2100)

    Shiranuka_RJCK       = (7, 43, "白糠", "RJCK", 9, "")
    RJCK_Shiranuka       = (7, 223, "RJCK", "白糠", 9, "")

    Moiwabashi_Nukanai   = (8, 259, "茂岩橋", "糠内", 9, "")


    RJCB_Arashiyama      = (11.5, 298, "RJCB", "嵐山") # ARP-東の橋
    Arashiyama_Shintoku  = (16  , 335, "嵐山", "新得")   # 過去資料より 
    Shintoku_Furano      = (24.5, 311, "新得", "富良野") # 駅-駅

    Shintoku_Yamabe      = (21.5, 297, "新得", "山部") # 駅-地図 

    Yamabe_Kamihurano    = (13.5, 16, "山部", "上士幌")  # 地図-Vrep

    Furano_Biei          = (14.5, 10, "富良野", "美瑛")  # 駅-Vrep

    Kamihurano_Biei      = (8, 357, "上士幌", "美瑛")    # Vrep-Vrep
    Biei_RJEC            = (5, 356, "美瑛", "RJEC")    # Vrep-ARP


def Increment05(a):
    return round(a * 2)/2


def Config(leg):
    dist = leg[0]
    tc   = leg[1]
    pos1 = leg[2]
    pos2 = leg[3]
    var  = leg[4]
    sea  = leg[5]
    WindDir = leg[6]
    WindVel = leg[7]
    oat     = leg[8]

    mc = tc + var

    return dist, tc, pos1, pos2, var, sea, WindDir, WindVel, oat, mc


def TAS(CAS, OAT, ALT): # Rule of Thumb に基づく（今後修正の必要あり）
    return round((1 + ALT * 0.02/1000) * CAS, 0)

def WCA(TAS, TC, WindDir, WindVel): # WCA[deg], GS[kt]を整数で返す
    wca = math.asin(( WindVel / TAS ) * math.sin(math.radians(WindDir - TC)))
    gs  = math.sqrt(TAS ** 2 + WindVel ** 2 - 2 * TAS * WindVel * math.cos( math.radians(math.pi - math.degrees(wca) - (WindDir - TC) )))
    wca = math.degrees(wca)
    return round(wca, 0), round(gs, 0)

def ETE(GS, ZoneDist):   #レグのETEを0.5刻みで返す
    return Increment05(60 * (ZoneDist / GS))



def CruiseDescentLegList(leg: list, CumDist, CumEte, DescentTime, DescentDist, Vrep, DistToVrep): #Phase...1:Climb, 2:Cruise, 3:Descent

    dist, tc, pos1, pos2, var, sea, WindDir, WindVel, oat, mc = Config(leg)   #巡航高度に達して以降の情報

    tas      = TAS(Setting.V_cruise, oat, Setting.Cruise_ALT)
    wca, gs  = WCA(tas, tc, WindDir, WindVel)
    mh       = mc + wca
    ete      = ETE(gs, dist)
        

    print(pos1, pos2, DistToVrep, DescentDist)
    if DistToVrep - dist <= DescentDist:
            
        distEOC = DistToVrep - round(DescentDist, 1) #dist - (DescentDist - DistToVrep)
        if pos2 == Vrep:
            EOCtoVrep = dist - distEOC
            tasDescent            = TAS(Setting.V_descent, Setting.DescentOAT, (Setting.Cruise_ALT + VrepALT[Vrep]) / 2)
            wcaDescent, gsDescent = WCA(tasDescent, tc, Setting.DescentWind[0], Setting.DescentWind[1])
            mhDescent             = mc + wcaDescent

            etetoEOC  = ETE(gs, distEOC)
            etetoVrep = ETE(gsDescent, EOCtoVrep)
            ete = etetoEOC + etetoVrep
            CumEte  += ete
            CumDist += dist
            DistToVrep -= dist
            EOCtoVrep = round(EOCtoVrep, 1)

            return [
                [pos1,  pos2,           " ",                " ",               " ",         "", tc, var, mc,                                                             " ",         "",        "",      str(dist) + "/" + str(CumDist),       " ",  str(ete)       + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
                [" " , "EOC",           "↘︎",                oat,  Setting.V_cruise,        tas, "", "",  "",                               str(WindDir) + "/" + str(WindVel),        wca,        mh,   str(distEOC) + "/"               ,        gs,  str(etetoEOC)  + "/", "", "", "", "SECT/REM FUEL"],
                [" " ,  pos2, VrepALT[Vrep], Setting.DescentOAT[0], Setting.V_descent, tasDescent, "", "",  "", str(Setting.DescentWind[0]) + "/" + str(Setting.DescentWind[1]), wcaDescent, mhDescent, str(EOCtoVrep) + "/"               , gsDescent,  str(etetoVrep) + "/", "", "", "", "SECT/REM FUEL"],
                [" ", "[" + str(sea) + "]"]
                    ], ete, True
    CumEte  += ete
    CumDist += dist

    DistToVrep -= dist

    tasDescent            = TAS(Setting.V_descent, Setting.DescentOAT, (Setting.Cruise_ALT + VrepALT["白糠"]) / 2)
    wcaDescent, gsDescent = WCA(tasDescent, tc, Setting.DescentWind[0], Setting.DescentWind[1])

    mhDescent           = mc + wcaDescent

    DescentTime = (Setting.Cruise_ALT - VrepALT["白糠"]) / Setting.DescentRate
    DescentDist = DescentTime * gsDescent / 60



    return [
            [pos1, pos2, Setting.Cruise_ALT, oat, Setting.V_cruise, tas, tc, var, mc, str(WindDir) + "/" + str(WindVel), wca, mh, str(dist) + "/" + str(CumDist), gs, str(ete) + "/" + str(CumEte), "", "", "", "/"],
            [" ", "[" + str(sea) + "]"]
           ], ete, False


def ClimbLegList(leg: list, CumDist, CumEte, ClimbTime, ClimbDist):

    dist, tc, pos1, pos2, var, sea, WindDir, WindVel, oat, mc = Config(leg)   #巡航高度に達して以降の情報

    tasClimb          = TAS(Setting.V_climb, Setting.ClimbOAT, (Setting.Cruise_ALT + Setting.FE) / 2)
    wcaClimb, gsClimb = WCA(tasClimb, tc, Setting.ClimbWind[0], Setting.ClimbWind[1])
    mhClimb           = mc + wcaClimb

    ClimbDist        += ( gsClimb / 60 ) * ClimbTime
        

    tasRCA            = TAS(Setting.V_cruise, oat, Setting.Cruise_ALT)
    wcaRCA, gsRCA     = WCA(tasRCA, tc, WindDir, WindVel)
    mhRCA             = mc + wcaRCA

    CumDist += dist

    if CumDist < ClimbDist:

        ete  = ETE(gsClimb, ClimbDist)
        CumEte += ete

        return [
                [pos1,  pos2, " ",               "",              "",       "", tc, var, mc,                                "",     "",        "", str(dist)    + "/" + str(CumDist),      "", str(ete) + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
                [" " ,  pos2, "↗︎", Setting.ClimbOAT, Setting.V_Climb, tasClimb, "",  "", "", str(WindDir) + "/" + str(WindVel), wcaClimb, mhClimb, str(dist) + "/"                  ,   gsRCA, str(ete) + "/"              , "", "", "", "SECT/REM FUEL"],
                [" ", "[" + str(sea) + "]"]
               ], ete, False   #False：上昇継続 True：上昇完了
    else:

        distRCA = dist - ClimbDist

        ClimbDist = Increment05( gsClimb * ClimbTime / 60)   #0.5nm単位に変更
        distRCA   = Increment05( distRCA )   #0.5nm単位に変更
        eteRCA    = ETE(gsRCA, distRCA)
        ete = ClimbTime + eteRCA
        CumEte += ete

        distRCA   = Increment05( distRCA )   #0.5nm単位に変更

        return [
            [pos1,  pos2, "    "            ,              " ",              " ",      " ", tc, var, mc,                                                          " ",        "",      "",   str(dist)    + "/" + str(CumDist),      "",  str(ete)   + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
            [" " , "RCA", "↗︎"               , Setting.ClimbOAT,  Setting.V_climb, tasClimb, "",  "", "", str(Setting.ClimbWind[0]) +  "/" + str(Setting.ClimbWind[1]),  wcaClimb, mhClimb, str(ClimbDist) + "/"               , gsClimb,  str(ClimbTime) +  "/", "", "", "", "SECT/REM FUEL"],
            [" " ,  pos2, Setting.Cruise_ALT,              oat, Setting.V_cruise,   tasRCA, "",  "", "",                            str(WindDir) + "/" + str(WindVel),    wcaRCA,   mhRCA, str(distRCA)   + "/"               ,   gsRCA,  str(eteRCA)    +  "/", "", "", "", "SECT/REM FUEL"],
            [" ", "（" + str(leg[5]) + "）"]
            ], ete, True


def VrepDist(Course, Vrep): #コースの合計距離を返す コース（List） → 距離（Double）
    dist = 0
    for leg in Course:
        dist += leg[0]
        if leg[3] == Vrep:
            break
    return dist

def DescentPerformance(Vrep):
    '''
    Descent に必要な時間と燃料を返す
    Descent が2レグ以上に渡って行われる場合、風向風速はVrepへのレグのものを採用する。
    '''

    DescentALT = VrepALT[Vrep]
    DescentTime = (Setting.Cruise_ALT - DescentALT) / Setting.DescentRate
    DescentFuel = (Setting.FuelDescent / 60) * DescentTime

    return DescentTime, DescentFuel


def WriteFile(Course, WindsTemp, Vrep, DescentLeg):
    ClimbDist = 0
    CumDist = 0
    CumEte  = 0

    DistToVrep = VrepDist(Course, Vrep)
    DescentALT = VrepALT[Vrep]

    RCA = False  #上昇中：False　巡航：True　
    EOC = False  #巡航中：False　降下：True

    ClimbTime ,ClimbFuel     = ClimbPerformance(FE = Setting.FE, Cruise_ALT = Setting.Cruise_ALT, OAT = Setting.ClimbOAT)
    DescentTime, DescentFuel = DescentPerformance(Vrep)


    DescentLegDist = 0
    DescentDist    = 0

    while True:
        tmp = Course[DescentLeg]
        tmp += (Setting.DescentWind + Setting.DescentOAT)
        
        dist, tc, pos1, pos2, var, sea, WindDir, WindVel, oat, mc = Config(tmp)
        DescentLegDist += dist

        tasDescent = TAS(Setting.V_descent, Setting.DescentOAT, (Setting.Cruise_ALT + DescentALT) / 2)
        wcaDescent, gsDescent = WCA(tasDescent, tc, Setting.DescentWind[0], Setting.DescentWind[1])
        mhDescent           = mc + wcaDescent

        ete = dist / (gsDescent / 60)

        DescentDist += DescentTime * gsDescent / 60


        if DescentTime >= ete:
            DescentTime -= ete
        else:
            break



    #ClimbTime = Increment05(ClimbTime)

    for i in range(len(Course)): #レグのタプルの末尾に風向風速を追加
        Course[i] += WindsTemp[i]


    with open('sample.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["FROM", "TO", "PA", "TOAT", "CAS", "TAS", "TC", "VAR", "MC", "WIND", "WCA", "MH", "ZONE/CUM DIST", "GS", "ZONE/CUM ETE", "ETO", "ATO", "ATE", "SECT/REM FUEL"])
        for leg in Course:
            dist, tc, pos1, pos2, var, sea, WindDir, WindVel, oat, mc = Config(leg)   #巡航高度に達して以降の情報
            if RCA == False:
                legLists, ete, RCA = ClimbLegList(leg, CumDist, CumEte, ClimbTime, ClimbDist)

                if RCA:
                    legList   = legLists[0]
                    climbList = legLists[1]
                    RCAList   = legLists[2]
                    seaList   = legLists[3]

                    writer.writerow(legList)
                    writer.writerow(climbList)
                    writer.writerow(RCAList)
                    writer.writerow(seaList)
                    writer.writerow([])
                
                else:
                    legList   = legLists[0]
                    climbList = legLists[1]
                    seaList   = legLists[2]

                    writer.writerow(legList)
                    writer.writerow(climbList)
                    writer.writerow(seaList)
                    writer.writerow([])

                    ClimbTime -= ete
                    ClimbDist += dist

                #else:
                #    writer.writerow([pos1, pos2, "↗︎",               "TOAT", Setting.V_climb,  "TAS", tc, "VAR", "MC", "WIND", "WCA", "MH",  str(leg[0]) + "/" + str(CumDist), "GS", "ZONE/CUM ETE", "ETO", "ATO", "ATE", "SECT/REM FUEL"])
            elif EOC == False:
                #print(leg)
                legLists, ete, EOC = CruiseDescentLegList(leg, CumDist, CumEte, DescentTime, DescentDist, Vrep, DistToVrep)
                if EOC == True:
                    legList     = legLists[0]
                    CruiseList  = legLists[1]
                    DescentList = legLists[2]
                    seaList     = legLists[3]

                    writer.writerow(legList)
                    writer.writerow(CruiseList)
                    writer.writerow(DescentList)
                    writer.writerow(seaList)
                    writer.writerow([])
                
                else:
                    legList     = legLists[0]
                    seaList     = legLists[1]

                    writer.writerow(legList)
                    writer.writerow(seaList)
                    writer.writerow([])

                    
                
            CumEte += ete
            CumDist += dist
            DistToVrep -= dist

           # print(CumDist)


def main():

    Course      = [Legs.RJCB_Moiwabashi, Legs.Moiwabashi_Otsu, Legs.Otsu_Shiranuka, Legs.Shiranuka_RJCK]
    WindsTemp   = [(340, 4, 14),         (340, 5, 15),         (350, 7, 15),        (10, 8, 15)]
    DescentLeg  = 2
    Vrep        = "白糠"

    WriteFile(Course, WindsTemp, Vrep, DescentLeg)


if __name__ == "__main__":
    main()