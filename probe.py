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

    def search(self, queryList):
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
        return num

    def build(self):
        coverage={}
        specificity={}
        total=0
        rootquery=self.getquery("Root")
        for subcategory in rootquery.keys():
            coverage[subcategory]=0
            for query in rootquery[subcategory]:
                coverage[subcategory]=coverage[subcategory]+self.search(query)
            total=total+coverage[subcategory]
        for subcategory in rootquery.keys():
            specificity[subcategory]=1.0*coverage[subcategory]/total

        for category in rootquery.keys():
            query=self.getquery(category)
            total=0
            for subcategory in query.keys():
                coverage[subcategory]=0
                for queries in query[subcategory]:
                    coverage[subcategory]=coverage[subcategory]+self.search(queries)
                total=total+coverage[subcategory]
            for subcategory in query.keys():
                specificity[subcategory]=specificity[category]*coverage[subcategory]/total

        print coverage
        print specificity
        result=["Root"]
        for category in coverage.keys():
            if coverage[category]>=self.cov and specificity[category]>=self.spec:
                result.append(category)
        print result
        return result


if __name__ == '__main__':
    qprobe=probe('diabetes.org','OzVX5Yq6tlnpOrdFaJkqIdoVAs7zFQrn+dbBhFHBAhw', 100, 0.6)
    qprobe.build()