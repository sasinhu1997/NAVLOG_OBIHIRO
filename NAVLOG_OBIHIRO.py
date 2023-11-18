#2023-09-24


# -*- coding: utf-8 -*-
import csv
import pprint
import math
import os
from functools import singledispatch


FROM          = "RJCB" #出発空港
TO            = "RJCB" #到着空港





VrepALT = {"中札内": 2000, "駒畠": 2000, "糠内": 2000, "更別": 2000, "富士": 2000, "白糠":2200}

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


def ClimbPerformance(FE, Cruise_ALT, OAT):
    '''
    飛行規程のデータに基づいて上昇性能を計算する。
    引数　: 出発地FE[ft], 巡航高度[ft]、外気温度[℃]
    返り値: 上昇時間[min], 消費燃料[G] 
    '''
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

    print("ClimbTime: ", time, "/", "ClimbFuel: ", fuel)

    return (time, fuel)

    
class Legs:
    #地点間の距離とTC（真方位）をまとめる。
    #地点1-地点2 = (距離[nm], TC（真方位）[deg], "地点1", "地点2", 偏差, SEA[ft])

    RJCB_Moiwa      = (13.5,  69, "RJCB", "茂岩", 9, 2000)  #Moiwa：茂岩橋
    Moiwa_RJCB      = (13.5, 249, "茂岩", "RJCB", 9, 2000)  #Moiwa：茂岩橋

    Moiwa_Kamishihoro = (27, 337, "茂岩", "上士幌", 9, "")
    Kamishihoro_Moiwa = (27, 157, "上士幌", "茂岩", 9, "")

    Kamishihoro_Mikage = (21.5, 225, "上士幌", "御影", 9, "")
    Mikage_Kamishihoro = (21.5,  45, "御影", "上士幌", 9, "")

    Mikage_Nakasatsunai = (15.5, 157, "御影", "中札内", 9, "")
    Nakasatsunai_Mikage = (15.5, 337, "中札内", "御影", 9, "")

    #RJCB_Nakasatsunai = 


    Moiwa_Otsu      = (9.5, 139, "茂岩橋", "大津", 9, 1600)
    Otsu_Moiwa      = (9.5, 319, "大津", "茂岩橋", 9, 1600)

    Otsu_Shiranuka       = (24,  49, "大津", "白糠", 9, 2100)
    Shiranuka_Otsu       = (24, 229, "白糠", "大津", 9, 2100)

    Shiranuka_RJCK       = (7,  43, "白糠", "RJCK", 9, "")
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
    Wind = leg[6:8]
    oat  = leg[8]

    mc = tc + var

    return dist, tc, pos1, pos2, var, sea, Wind, oat, mc


def TAS(CAS, OAT, ALT): 
    '''
    TAS を計算する。
    Rule of Thumb に基づく（今後修正の必要あり）
    引数　: CAS[kt], OAT[℃], ALT[ft]
    返り値: TAS[kt] 
    '''
    return round((1 + ALT * 0.02/1000) * CAS, 0)


def WCA(TAS, TC, Wind): 
    '''
    TC[deg] 及び TAS[kt] と Wind[deg, kt] に基づいて WCA[deg] と GS[kt] を計算する。
    風力三角形に余弦定理を適用することで計算される。
    WCA, GSについては、四捨五入して整数で返す
    '''
    WindDir = Wind[0]
    WindVel = Wind[1]

    wca = math.asin(( WindVel / TAS ) * math.sin(math.radians(WindDir - TC)))
    gs  = math.sqrt(TAS ** 2 + WindVel ** 2 - 2 * TAS * WindVel * math.cos( math.radians(math.pi - math.degrees(wca) - (WindDir - TC) )))
    wca = math.degrees(wca)
    return round(wca, 0), round(gs, 0)


def ZoneETE(GS, ZoneDist): 
    '''
    与えられた1レグの ZONE ETE を計算する。
    学生訓練実施要領に基づき, ZONE ETEを 0.5[min] 単位で計算する。
    引数　: GS[kt], ZONE DIST[nm]
    返り値: ZONE ETE[min]
    '''
    return Increment05(60 * (ZoneDist / GS))


def TAS_WCA_GS_MH(V, OAT, ALT, TC, MC, Wind):
    tas      = TAS(V, OAT, ALT)
    wca, gs  = WCA(tas, TC, Wind)
    mh       = MC + wca
    return tas, wca, gs, mh


def CruiseDescentLegList(leg: list, CruiseALT, CumDist, CumEte, DescentTime, DescentDist, Vrep, DistToVrep, DescentWindOAT):

    print('Function "CruiseDescentLegList" Initiated... ')

    dist, tc, pos1, pos2, var, sea, Wind, oat, mc = Config(leg)   #巡航高度に達して以降の情報

    tas, wca, gs, mh = TAS_WCA_GS_MH(V_cruise, oat, CruiseALT, tc, mc, Wind)

    ete      = ZoneETE(gs, dist)
    #ete　レグのETE[min]

    if EOC == False:
        #計算対象のレグの FROM の時点では EOC を迎えていない場合
        print("EOC == False...")
        
        if DistToVrep - dist <= DescentDist:
            #計算対象のレグの FROM の時点では EOC を迎えていないが、計算対象レグにおいてEOCを迎える場合
            print("EOC is on this course...")
            distEOC = DistToVrep - round(DescentDist, 1) #dist - (DescentDist - DistToVrep)
            if pos2 == Vrep:
                print("POS2 == Vrep...")
                #計算対象のレグで EOC を迎える場合であり、かつ、計算対象レグの TO が Vrep である場合

                EOCtoVrep = dist - distEOC

                tasDescent, wcaDescent, gsDescent, mhDescent = TAS_WCA_GS_MH(V_descent, DescentOAT, (CruiseALT + VrepALT[Vrep]) / 2, tc, mc, DescentWindOAT[:2])

                etetoEOC  = ZoneETE(gs, distEOC)
                etetoVrep = ZoneETE(gsDescent, EOCtoVrep)
                ete = etetoEOC + etetoVrep
                CumEte  += ete
                CumDist += dist
                DistToVrep -= dist
                EOCtoVrep = round(EOCtoVrep, 1)

                distEOC = Increment05(distEOC)


                return [
                    [pos1,  pos2,  CruiseALT,         " ",               " ",         "", tc, var, mc,                                                             " ",         "",        "",      str(dist) + "/" + str(CumDist),       " ",  str(ete)       + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
                    [],
                    ["[" + str(sea) + "]", "EOC",           "↘︎",                oat,  V_cruise,        tas, "", "",  "",                               str(Wind[0]) + "/" + str(Wind[1]),        wca,        mh,   str(distEOC) + "/"               ,        gs,  str(etetoEOC)  + "/", "", "", "", "SECT/REM FUEL"],
                    [" " ,  pos2, VrepALT[Vrep], DescentOAT, V_descent, tasDescent, "", "",  "", str(DescentWindOAT[0]) + "/" + str(DescentWindOAT[1]), wcaDescent, mhDescent, str(EOCtoVrep) + "/"               , gsDescent,  str(etetoVrep) + "/", "", "", "", "SECT/REM FUEL"],
                        ], ete, True
        
            else:
                #計算対象のレグで EOC を迎える場合であり、かつ、計算対象レグの TOが Vrep でない場合
                print("POS2 != Vrep...")

                tasDescent, wcaDescent, gsDescent, mhDescent = TAS_WCA_GS_MH(V_descent, DescentOAT, (CruiseALT + VrepALT[Vrep]) / 2, tc, mc, DescentWindOAT[:2])
                EOCtoPos2 = dist - distEOC

                etetoEOC  = ZoneETE(gs, distEOC)
                etetoPos2 = ZoneETE(gsDescent, EOCtoPos2)
                ete = etetoEOC + etetoPos2
                CumEte  += ete
                CumDist += dist
                DistToVrep -= dist
                

                distEOC = Increment05(distEOC)
                EOCtoPos2 = Increment05(EOCtoPos2)


                return [
                [pos1,  pos2,  CruiseALT,                " ",               " ",         "", tc, var, mc,                                                             " ",         "",        "",      str(dist) + "/" + str(CumDist),       " ",  str(ete)       + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
                [],
                ["[" + str(sea) + "]", "EOC",           "↘︎",                oat,  V_cruise,        tas, "", "",  "",                               str(Wind[0]) + "/" + str(Wind[1]),        wca,        mh,   str(distEOC) + "/"               ,        gs,  str(etetoEOC)  + "/", "", "", "", "SECT/REM FUEL"],
                [" " ,  pos2, "↘︎", DescentOAT, V_descent, tasDescent, "", "",  "", str(DescentWindOAT[0]) + "/" + str(DescentWindOAT[1]), wcaDescent, mhDescent, str(EOCtoPos2) + "/"               , gsDescent,  str(etetoPos2) + "/", "", "", "", "SECT/REM FUEL"],
                    ], ete, True

        else:
            #計算対象のレグの FROM の時点では EOC を迎えておらず、計算対象レグにおいても EOC を迎えない場合。
            CumEte  += ete
            CumDist += dist

            DistToVrep -= dist

            tasDescent, wcaDesecnt, gsDescent, mhDescent = TAS_WCA_GS_MH(V_descent, DescentOAT, (Cruise_ALT + VrepALT["白糠"]) / 2, tc, mc, DescentWindOAT[:2])

            DescentTime = (CruiseALT - VrepALT["白糠"]) / DescentRate
            DescentDist = DescentTime * gsDescent / 60

            return [
                [pos1, pos2, CruiseALT, oat, V_cruise, tas, tc, var, mc, str(Wind[0]) + "/" + str(Wind[1]), wca, mh, str(dist) + "/" + str(CumDist), gs, str(ete) + "/" + str(CumEte), "", "", "", "/"],
                [],
                [],
                ["[" + str(sea) + "]", pos2, ""       , "" , "", "" , "", "", "", "", "", "", "", "", "", "", "", "", "/"]
                ], ete, False


    else:
        #計算対象のレグの FROM の時点で既に降下を開始している場合
        print("EOC == True...")
        distEOC = DistToVrep - round(DescentDist, 1) #dist - (DescentDist - DistToVrep)
        if pos2 == Vrep:
            #計算対象のレグ のFROMの時点で既に降下を開始しており、TOがVrep である場合

            tasDescent, wcaDescent, gsDescent, mhDescent = TAS_WCA_GS_MH(V_descent, DescentOAT, (CruiseALT + VrepALT[Vrep]) / 2, tc, mc, DescentWindOAT[:2])
            CumEte  += ete
            CumDist += dist

            return [
                    [pos1,  pos2,  "↘︎",                " ",               " ",         "", tc, var, mc,                                                             " ",         "",        "",      str(dist) + "/" + str(CumDist),       " ",  str(ete)       + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
                    [],
                    ["[" + str(sea) + "]", "" ,"↘︎", oat,  V_cruise,        tas, "", "",  "",                               str(Wind[0]) + "/" + str(Wind[1]),        wca,        mh,    "/"               ,        gs,  "/", "", "", "", "SECT/REM FUEL"],
                    [" " ,  pos2, VrepALT[Vrep], DescentOAT, V_descent, tasDescent, "", "",  "", str(DescentWindOAT[0]) + "/" + str(DescentWindOAT[1]), wcaDescent, mhDescent,  "/"               , gsDescent,   "/", "", "", "", "SECT/REM FUEL"],
                    ], ete, True

        else:
            #計算対象のレグ の FROM の時点で既に降下を開始しており、TOがVrep ではない場合
            return [
                    [pos1,  pos2,  "↘︎",                " ",               " ",         "", tc, var, mc,                                                             " ",         "",        "",      str(dist) + "/" + str(CumDist),       " ",  str(ete)       + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
                    [],
                    ["[" + str(sea) + "]", "C'k Point","↘︎", oat,  V_cruise,        tas, "", "",  "",                               str(Wind[0]) + "/" + str(Wind[1]),        wca,        mh,   str(distEOC) + "/"               ,        gs,  str(etetoEOC)  + "/", "", "", "", "SECT/REM FUEL"],
                    [" " ,  pos2, "", DescentOAT, V_descent, tasDescent, "", "",  "", str(DescentWindOAT[0]) + "/" + str(DescentWindOAT[1]), wcaDescent, mhDescent, str(EOCtoVrep) + "/"               , gsDescent,  str(etetoVrep) + "/", "", "", "", "SECT/REM FUEL"],
                    ], ete, True

            pass
        


def ClimbLegList(leg: list, ClimbTime, ClimbWindOAT, CruiseALT):
    global ClimbDist, CumDist, CumEte

    dist, tc, pos1, pos2, var, sea, Wind, oat, mc = Config(leg)   #巡航高度に達して以降の情報

    CumDist += dist

    tasClimb, wcaClimb, gsClimb, mhClimb = TAS_WCA_GS_MH(V_climb, ClimbOAT, (CruiseALT + FE) / 2, tc, mc, ClimbWindOAT[:2])        
    tasRCA, wcaRCA, gsRCA, mhRCA         = TAS_WCA_GS_MH(V_cruise, oat, CruiseALT, tc, mc, Wind)

    if CumDist < (ClimbDist + ( gsClimb / 60 ) * ClimbTime):
        #計算対象 Leg において RCA に到達しない場合

        ete  = ZoneETE(gsClimb, ClimbDist)
        ete = Increment05(ete)
        CumEte += ete
        ClimbDist += dist

        return [
                [pos1,  pos2, " ",               "",              "",       "", tc, var, mc,                                "",       "",      "", str(dist)    + "/" + str(CumDist),      "", str(ete) + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
                [],
                [],
                ["[" + str(sea) + "]",  pos2, "↗︎", ClimbOAT, V_climb, tasClimb, "",  "", "", str(Wind[0]) + "/" + str(Wind[1]), wcaClimb, mhClimb, str(dist) + "/"                  ,   gsRCA, str(ete) + "/"              , "", "", "", "SECT/REM FUEL"],
               ], ete, False   #False：上昇継続 True：上昇完了

    else:
        #計算対象 Leg において RCA に到達する場合

        ClimbDist += ( gsClimb / 60 ) * ClimbTime
        ClimbDist = Increment05( ClimbDist ) #0.5nm単位に変更

        distRCA = dist - ClimbDist
        distRCA   = Increment05( distRCA )   #0.5nm単位に変更
        
        eteRCA    = ZoneETE(gsRCA, distRCA)
        ete = ClimbTime + eteRCA
        ete = Increment05(ete)
        CumEte += ete

        ClimbTime = Increment05(ClimbTime)


        return [
            [pos1,  pos2, "    "            ,              " ",              " ",      " ", tc, var, mc,                                                          " ",        "",      "",   str(dist)    + "/" + str(CumDist),      "",  str(ete)   + "/" + str(CumEte), "", "", "", "SECT/REM FUEL"],
            [],
            [" " , "RCA", "↗︎"               , ClimbOAT, V_climb, tasClimb, "",  "", "", str(ClimbWindOAT[0]) +  "/" + str(ClimbWindOAT[1]),  wcaClimb, mhClimb, str(ClimbDist) + "/"               , gsClimb,  str(ClimbTime) +  "/", "", "", "", "SECT/REM FUEL"],
            ["[" + str(sea) + "]" ,  pos2, CruiseALT,              oat, V_cruise,   tasRCA, "",  "", "",                            str(Wind[0]) + "/" + str(Wind[1]),    wcaRCA,   mhRCA, str(distRCA)   + "/"               ,   gsRCA,  str(eteRCA)    +  "/", "", "", "", "SECT/REM FUEL"],
            ], ete, True


def VrepDist(Course, Vrep): 
    '''
    設定した経路について、出発点から Vrep までの合計距離[nm]を返す
    引数　: （コース（List）、Vrep）
    返り値: 出発点〜Vrep の合計距離
    '''
    dist = 0
    for leg in Course:
        dist += leg[0]
        if leg[3] == Vrep:
            break
    return dist


def DescentPerformance(Vrep, CruiseALT):
    '''
    Descent に必要な時間と燃料を返す
    Descent が2レグ以上に渡って行われる場合、風向風速はVrepへのレグのものを採用する。
    '''

    DescentALT = VrepALT[Vrep]
    DescentTime = (CruiseALT - DescentALT) / DescentRate
    DescentFuel = (FuelDescent / 60) * DescentTime

    

    return DescentTime, DescentFuel
    

def DescentDistance(Course, DescentLeg, DescentALT):
    """
    DescentDistの計算を行う。
    """
    global DescentDist

    while True:
        
        tmp = Course[DescentLeg] + DescentWindOAT

        dist, tc, pos1, pos2, var, sea, Wind, oat, mc = Config(tmp)

        gsDescent = TAS_WCA_GS_MH(V_descent, DescentOAT, (Cruise_ALT + DescentALT) / 2, tc, mc, DescentWindOAT[:2])[2]

        ete = dist / (gsDescent / 60)

        DescentDist += DescentTime * gsDescent / 60

        if DescentTime >= ete:
            # 計算対象 Leg の ETE よりも DescentTime の方が長い場合（＝その Leg で降下完了しない場合）
            DescentTime -= ete
        else:
            # 計算対象 Leg の ETE の方が DescentTime の方が長い場合（＝その Leg で降下完了する場合）
            break




def WriteFile(Course, WindsTemp, ClimbWindOAT, DescentWindOAT, Vrep, DescentLeg, CruiseALTs):

    global ClimbDist, CumDist, CumEte
    global DescentDist
    global RCA, EOC

    DistToVrep = VrepDist(Course, Vrep)
    #DistToVrep　【定義】計算対象の Leg の FROM から Vrep までの距離[nm]
    # 　　　　　　　初期値: 出発点から Vrep までの距離[nm]

    DescentALT = VrepALT[Vrep]
    #DescentALT　【定義】Vrep を通過する時の高度[ft]

    ClimbTime, ClimbFuel     = ClimbPerformance(FE = FE, Cruise_ALT = CruiseALTs[0], OAT = ClimbOAT)
    #ClimbTime 【定義】計算対象 Leg の FROM から巡航高度までの上昇に必要な時間[min]
    #ClimbFuel 【定義】計算対象 Leg の FROM から巡航高度までの上昇に必要な燃料量[G]



    DescentTime, DescentFuel = DescentPerformance(Vrep, CruiseALTs[DescentLeg])
    #DescentTime 【定義】巡航高度からVrep通過高度までの降下にかかる時間[min]
    #DescentFuel 【定義】巡航高度からVrep通過高度までの降下に必要な燃料量[G]
    

    while True:
        """
        DescentDistの計算を行う。
        """
        tmp = Course[DescentLeg] + DescentWindOAT

        dist, tc, pos1, pos2, var, sea, Wind, oat, mc = Config(tmp)

        gsDescent = TAS_WCA_GS_MH(V_descent, DescentOAT, (CruiseALTs[DescentLeg] + DescentALT) / 2, tc, mc, DescentWindOAT[:2])[2]
        ete = dist / (gsDescent / 60)
        DescentDist += DescentTime * gsDescent / 60

        if DescentTime >= ete:
            # 計算対象 Leg の ETE よりも DescentTime の方が長い場合（＝その Leg で降下完了しない場合）

            DescentLeg -= 1

            DescentTime = DescentPerformance(Vrep, CruiseALTs[DescentLeg])[0] - ete

        else:
            # 計算対象 Leg の ETE の方が DescentTime の方が長い場合（＝その Leg で降下完了する場合）
            break
        
         

    for i in range(len(Course)): #レグのタプルの末尾に風向風速を追加
        Course[i] += WindsTemp[i]

    with open('sample.csv', 'w') as f:
        writer = csv.writer(f)

        #LOGの一行目
        writer.writerow(["FROM", "TO", "PA", "TOAT", "CAS", "TAS", "TC", "VAR", "MC", "WIND", "WCA", \
                         "MH", "ZONE/CUM DIST", "GS", "ZONE/CUM ETE", "ETO", "ATO", "ATE", "SECT/REM FUEL"])
        
        i = 0
        for leg in Course:
            #各レグに関する計算

            dist, tc, pos1, pos2, var, sea, Wind, oat, mc = Config(leg)   #巡航高度に達して以降の情報

            #LOG（＠RCAの到達前）
            if RCA == False:

                legLists, ete, RCA = ClimbLegList(leg, ClimbTime, ClimbWindOAT, CruiseALTs[i])

                for leglist in legLists:
                    writer.writerow(leglist)
                writer.writerow([])

                if RCA == False:
                    ClimbTime -= ete
                
                DistToVrep -= dist

            else:
                #LOG（＠RCAの到達後）

                if EOC == False:
                    #LOG（＠EOCの到達前）
                    legLists, ete, EOC = CruiseDescentLegList(leg, CruiseALTs[i], CumDist, CumEte, DescentTime, DescentDist, Vrep, DistToVrep, DescentWindOAT)

                    for leglist in legLists:
                        writer.writerow(leglist)
                    writer.writerow([])

                else:
                    #LOG（@EOCの到達後かつVrep到達前）
                    legLists, ete, EOC = CruiseDescentLegList(leg, CruiseALTs[i], CumDist, CumEte, DescentTime, DescentDist, Vrep, DistToVrep, DescentWindOAT)

                    for leglist in legLists:
                        writer.writerow(leglist)
                    writer.writerow([])


                CumEte += ete
                CumDist += dist
                DistToVrep -= dist

                i += 1


def main():

    Course      = [Legs.RJCB_Moiwa, Legs.Moiwa_Kamishihoro, Legs.Kamishihoro_Mikage, Legs.Mikage_Nakasatsunai]
    ClimbWindOAT     = (260, 2, 23) #上昇中の風向風速
    DescentWindOAT   = (10,  8, 14) #降下中の風向風速
    WindsTemp   = [(310, 7, 21),         (300, 7, 18),         (290, 9, 15),        (0, 0, 18)]
    CruiseALTs  = [6500, 6500, 6500, 6500]
    DescentLeg  = len(Course) - 2
    Vrep        = "中札内"

    WriteFile(Course, WindsTemp, ClimbWindOAT, DescentWindOAT, Vrep, DescentLeg, CruiseALTs)


if __name__ == "__main__":

    Cruise_ALT    = 3500 # 巡航高度[ft]
    DescentRate   = 500  # 降下率[fpm]
    ClimbOAT      = 23   # 上昇時外気温度
    V_climb       = 111  # 上昇時速度[kt](CAS)
    V_cruise      = 142  # 巡航速度[kt](CAS)
    V_descent     = 142  # 降下時速度[kt](CAS)
    V_Vrep        = 121

    Variation     = 9      # 磁方位の偏差(西が+, 東が-)
    FE            = 500  # 飛行場標点標高[ft]
    DescentOAT    = 14   # 降下時外気温度

    FuelCruise    = 15
    FuelDescent   = 12   # 降下時の燃料消費量[GPH]

    ClimbDist = CumDist = CumEte = 0
    #ClimbDist　【定義】RCA到達前において、計算対象 Leg の TO までに移動した距離[nm]
    #CumDist  　【定義】計算対象 Leg の TO までに移動した距離[nm]
    #CumEte   　【定義】計算対象 Leg の TO までの ETE [min]

    DescentDist    = 0
    #DescentDist　【定義】巡航高度からVrep通過高度までの降下に必要な距離[nm]

    RCA = EOC = False  
    #RCA　　【定義】到達前：False　到達後：True　
    #EOC　　【定義】到達前：False　到達後：True

    main()