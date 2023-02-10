import os
import sys
import math
import matplotlib.pyplot as plt
def main():
    
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else 'simple.trecrun'
    queriesFile = sys.argv[2] if argv_len >= 3 else 'qrels'
    outputFile = sys.argv[3] if argv_len >= 4 else 'simple.eval'

    runsData = open(inputFile)
    runsData = evaluateTecRun(runsData)
    relevanceData = open(queriesFile)
    relevanceData, onlyRelevant = evaluateQrels(relevanceData)

    runsRelData = combineRelAndScore(runsData,onlyRelevant)
    #trecTotals = getTotalQueryDocs(runsRelData)
    #docTotals, relevanceTotals = getRelevanceTotals(relevanceData)
    relevanceTotals = GetOnlyRelTotals(onlyRelevant)
    idealDict = idealNDCG(relevanceData)

    totalRel = getTotalRelevant(onlyRelevant)
    p15Dict = precision(runsRelData,15)
    r20Dict = recall(runsRelData,totalRel, 20)
    apDict = avgPrecision(runsRelData,relevanceTotals)
    rrDict = reciprocalRank(runsRelData)
    ndcgDict = nDCG(runsRelData,75,idealDict)
    f25Dict = fallout(runsRelData,25,totalRel)
    if os.path.exists(outputFile):
        os.remove(outputFile)
    opFile = open( outputFile,'a')
    keys = list(runsRelData.keys())
    keys.append("all")
    r20 = []
    p15 = []
    for key in keys:
        ndcgNum = round(ndcgDict[key],4)
        rrNum = round(rrDict[key], 4)
        p15Num = round(p15Dict[key],4)
        r20Num = round(r20Dict[key],4)
        f25Num = round(f25Dict[key],4)
        apNum = round(apDict[key],4)
        

        opFile.write("NDCG@75" +" "+key+" "+ str(ndcgNum) + '\n')
        opFile.write("RR" +" "+key+" "+ str(rrNum) + '\n')
        opFile.write("P@15" +" "+key+" "+ str(p15Num)+ '\n')
        opFile.write("R@20" +" "+key+" "+ str(r20Num)+ '\n')
        opFile.write("F1@25" +" "+ key +" "+ str(f25Num)+ '\n')
        opFile.write("AP" +" "+key+" "+ str(apNum)+ '\n')
        
        #print(row[0],time2-time1)
        if int(key) == 660:
            r20.append(r20Num)
            p15.append(p15Num)
            plt.plot(r20, p15, label = 'BM-25')
            plt.xlabel("Recall")
            plt.ylabel("Precision")
            plt.legend()
            plt.show()

def evaluateTecRun(fD):
    keys = ['query','skip','docid','rank','score','text']
    myDict = {}
    returnedDict = {}
    queriesList = []
    for line in fD:
        tokens = line.split()
        iter = 0
        for word in tokens:
            myDict[keys[iter]] = word
            if iter == 0 and word not in queriesList:
                queriesList.append(word)
                returnedDict[word] = []
                query = word          
            iter += 1
        returnedDict[query].append(dict(myDict))
    return returnedDict

def getTotalQueryDocs(runs):
    totals = {}
    keys = runs.keys()
    for thoseDicts in runs:
        newDict = {}
        qNum = thoseDicts
        for thisDict in runs[thoseDicts]: 
            if qNum in totals:
                totals[qNum]["total"] = totals[qNum]["total"] + 1
                if int(thisDict["relevance"]) > 0:
                    totals[qNum]["totalRelevant"] = totals[qNum]["totalRelevant"] + 1
            else:
                if int(thisDict["relevance"]) > 0:
                    totals[qNum] = {"total":1, "totalRelevant": 1}
                else:
                    totals[qNum] = {"total":1, "totalRelevant": 0}
    return totals

def evaluateQrels(qrel):
    keys= ['query', 'skip', 'docid','relevance']
    myDict={}
    returnedList =[]
    returnedDict ={}
    relList = []
    temp = None
    for line in qrel:
        tokens = line.split()
        iter = 0
        for token in tokens:
            myDict[keys[iter]] = token
            iter += 1
        if int(myDict["relevance"]) > 0:
            relList.append(dict(myDict))
        returnedList.append(dict(myDict))
    for row in relList:
        if row['query'] in returnedDict.keys():
            returnedDict[row['query']].append(dict(row))
        else:
            returnedDict[row['query']] = [dict(row)]

    return returnedList, returnedDict

def getRelevanceTotals(rD):
    temp = None
    totalsDict = {}
    totalsRelDict={}
    for relDict in rD:
        #print(totalsDict.keys())
        if relDict["query"] in totalsDict.keys():
            totalsDict[relDict["query"]] = totalsDict[relDict["query"]] + 1
        else:
            totalsDict[relDict["query"]] = 1
        if relDict["query"] in totalsRelDict.keys() and int(relDict["relevance"]) == 1:
            totalsRelDict[relDict["query"]] = totalsRelDict[relDict["query"]] + 1
        elif int(relDict["relevance"]) == 1:
            totalsRelDict[relDict["query"]] = 1
    return totalsDict, totalsRelDict

def GetOnlyRelTotals(rD):
    returnDict ={}
    for query in rD:
        total = len(rD[query])
        returnDict[query] = total
    return returnDict

def combineRelAndScore(sD, rD):
    for scoreDicts in sD:
        for scoreDict in sD[scoreDicts]:
            for relDict in rD[scoreDicts]:
            #for relDict in rD:
                if "relevance" not in scoreDict.keys():
                    scoreDict['relevance' ] = 0
                if int(scoreDict["query"]) == int(relDict["query"]) and scoreDict["docid"] == relDict["docid"] :
                    scoreDict['relevance'] = int(relDict['relevance'])
                    break
    return sD
def getTotalRelevant(relDocs):
    totalsDict = {}
    for key in  relDocs:
        totalsDict[key] = len(relDocs[key])
        #for row in relDocs[key]:
            #if row["query"] in totalsDict:
                #totalsDict[row["query"]] = totalsDict[row["query"]] + 1
            #else:
                #totalsDict[row["query"]] = 1
    return totalsDict

def precision(scoreList,n):
    sum = 0
    max = n
    queries = 0
    p15Dict = {}
    for query in scoreList:
        queries += 1
        iter = 0
        relCount = 0
        for row in scoreList[query]:
            if iter == max and max > 0:
                break
            if int(row["relevance"]) > 0:
                relCount += 1
            iter += 1
        p15Dict[query] = relCount/iter
        sum+= relCount/iter
    p15Dict["all"] = sum/queries
    #print("p15", p15Dict)
    return p15Dict
def recall(scoreList, tR,n):
    sum = 0
    max = n
    queries = 0
    r20Dict = {}
    for query in scoreList:
        queries += 1
        iter = 0
        relCount = 0
        for row in scoreList[query]:
            if iter == max and max > 0:
                break
            if int(row["relevance"]) > 0:
                relCount += 1
            iter += 1
        if int(tR[query]) > 0:
            r20Dict[query] = relCount/tR[query]
            sum+= relCount/tR[query]
        else: 
            r20Dict[query] = 0
            sum+= 0 
    r20Dict["all"] = sum/queries
    #print("r20", r20Dict)
    return r20Dict
def avgPrecision(scoreList,relTotals):
    sum = 0

    apDict = {}
    queries = 0
    for query in scoreList:
        sum2 = 0
        queries += 1
        prec = 0
        docs = 0
        for row in scoreList[query]:
            docs += 1
            if int(row['relevance']) > 0:
                prec += 1
                sum2 += prec/docs
        if sum2 > 0:
            apDict[query] = sum2/int(relTotals[query])
            sum += sum2/int(relTotals[query])
        else:
            apDict[query] = sum2
            sum += sum2
        #sum += sum2/int(relTotals[query])
    apDict["all"] = sum/queries
    #print("ap",apDict)
    return apDict

def reciprocalRank(scoreList):
    sum = 0

    rrDict = {}
    queries = 0
    for query in scoreList:
        sum2 = 0
        queries += 1
        docs = 0
        for row in scoreList[query]:
            docs += 1
            if int(row['relevance']) > 0:
                sum2 += 1/docs
                break

        rrDict[query] = sum2

        sum += sum2
    rrDict["all"] = sum/queries
    #print("rr",rrDict)
    return rrDict

def nDCG(scoreList, n, iNDCG):

    scoresDict = {}
    idealScoresDict = {}
    returnedDict = {}
    total = 0
    queries = 0
    for query in scoreList:
        queries+=1
        iter = 1
        score = 0
        trackScores = 0
        for row in scoreList[query]:
            if n > 0 and iter > n:
                break
            if iter > 1:
                score = int(row["relevance"])/math.log(iter,2)
            else:
                score = int(row["relevance"])
            trackScores += score
            iter += 1
        scoresDict[query] = trackScores
        iter = 1
        score = 0
        trackIdealScores=0
        for row in iNDCG[query]:
            if n > 0 and iter > n:
                break
            elif iter > 1:
                score = int(row["relevance"])/math.log(iter,2)
            else:
                score = int(row["relevance"])
            trackIdealScores += score
            iter += 1
        if trackIdealScores != 0:
            returnedDict[query] = trackScores/trackIdealScores
            total += trackScores/trackIdealScores
            idealScoresDict[query] = trackIdealScores
        else :
            returnedDict[query] = 0
            total += 0
            idealScoresDict[query] = 0
    returnedDict["all"] = total/queries
    #print("ndcg" ,returnedDict)
    return returnedDict


def idealNDCG(onlyR):
    temp = None
    sortOnlyR = {}
    sortedDict = {}
    count = 0
    for row in onlyR:
        if str(row["query"]) == temp:
            sortOnlyR[row["query"]].append(dict(row))
        else:
            sortOnlyR[row["query"]] = [dict(row)]
            temp = str(row["query"])
    for query in sortOnlyR:
        sortedDict[query] = sorted(sortOnlyR[query], key = lambda d: d["relevance"], reverse = True )
    return sortedDict

def fallout(scoreList,n,tR):
    r = recall(scoreList,tR,n)
    p = precision(scoreList,n)
    falloutDict = {}
    sum = 0
    itr = 0
    for query in scoreList:
        itr +=1
        top = 2* r[query] * p[query]
        bottom = r[query]+p[query]
        if bottom == 0:
            falloutDict[query] = 0
        else:
            falloutDict[query] = top/bottom
            sum += (top/bottom)
    falloutDict["all" ] = sum/itr
    #print("f75" ,falloutDict)
    return falloutDict

main()
