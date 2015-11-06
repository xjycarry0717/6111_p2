import os
import urllib2
import base64
import json

class probe:
    def __init__(self,site, accountKey, ECoverage,ESpecificity):
        self.site=site
        self.accountKey=accountKey
        self.cov= ECoverage
        self.spec=ESpecificity
        self.url={"Root":[],"Computers":[],"Health":[],"Sports":[]}
        #self.category={"Root":{"Computers":["Hardware","Programming"],"Health":["Fitness","Diseases"],"Sports":["Basketball","Soccer"]}}
        return

    def getquery(self,category):
        file=open(category+'.txt','r')
        querydict={}
        for f in file.xreadlines():
            s=(f.replace("\n","")).replace(" \n","")
            s=s.split(" ")
            if s==[]:
                continue
            if s[0] not in querydict.keys():
                querydict.setdefault(s[0],[])
            querydict[s[0]].append(" ".join(s[1:]))
        file.close()
        #print querydict
        return querydict

    def search(self, category,queryList):
        #change blank space in the query into %20
        query = queryList.replace(" ","%20")
        bingUrl ='https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a'+self.site+'%20'+query+'%27&$top=10&$format=json'
        #print "URL: ", bingUrl

        accountKeyEnc = base64.b64encode(self.accountKey + ':' + self.accountKey)
        headers = {'Authorization': 'Basic ' + accountKeyEnc}
        req = urllib2.Request(bingUrl, headers = headers)
        response = urllib2.urlopen(req)
        content = json.loads(response.read())
        num=int(content["d"]["results"][0]["WebTotal"])
        for i in range(len(content["d"]["results"][0]["Web"])):
            if i==4:
                break
            address=content["d"]["results"][0]["Web"][i]["Url"]
            #print address
            self.url[category].append(address)
        return num

    def build(self):
        coverage={}
        specificity={}
        total=0
        print "Classifying..."
        rootquery=self.getquery("Root")
        for subcategory in rootquery.keys():
            coverage[subcategory]=0
            for query in rootquery[subcategory]:
                coverage[subcategory]=coverage[subcategory]+self.search("Root",query)
            total=total+coverage[subcategory]
        for subcategory in rootquery.keys():
            specificity[subcategory]=1.0*coverage[subcategory]/total
            print "Specificity for category "+subcategory+" is "+str(specificity[subcategory])
            print "Coverage for category "+subcategory+" is "+str(coverage[subcategory])

        result={}
        result["Root"]={}
        for category in rootquery.keys():
            if coverage[category]>=self.cov and specificity[category]>=self.spec:
                result["Root"][category]=[]
                query=self.getquery(category)
                total=0
                for subcategory in query.keys():
                    coverage[subcategory]=0
                    for queries in query[subcategory]:
                        coverage[subcategory]=coverage[subcategory]+self.search(category,queries)
                    total=total+coverage[subcategory]
                for subcategory in query.keys():
                    specificity[subcategory]=specificity[category]*coverage[subcategory]/total
                    print "Specificity for category "+subcategory+" is "+str(specificity[subcategory])
                    print "Coverage for category "+subcategory+" is "+str(coverage[subcategory])
                    if coverage[subcategory]>=self.cov and specificity[subcategory]>=self.spec:
                        result["Root"][category].append(subcategory)


        print ""
        print "Classification:"
        #print result

        if result["Root"]=={} :
            print "/Root"
        else:
            for category in result["Root"]:
                if not len(result["Root"][category]):
                    print "/Root/"+category
                else:
                    for subcategory in result["Root"][category]:
                        print "/Root/"+category+"/"+subcategory
        return result



