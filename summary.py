import subprocess
import re

class summary:
	def __init__(self, qprobe, resultList, host):
		self.qprobe = qprobe			# qprober of sample url associated with each category
		self.resultList = resultList	# classification result list of lists
		self.host = host				# database website
		self.rootUrlSet = set()			# set of sample url to eliminate duplicates
		self.rootContentSummary = {}	# content summary map<word, frequency>

	def __retrieveUrl(self, url):
		print "Getting: " + url

		# skip pdf or ppt
		if(url.split('.')[-1] == "pdf" or url.split('.')[-1] == "ppt"):
			print "skip"
			return set()

		# retrieve page dump, pass if error
		output = ""
		try:
			output = subprocess.check_output("lynx --dump " + url, shell=True)
		except Exception as e:
			pass

		# remove the references at the end of the dump
		end = output.find("\nReferences\n")

		# remove everything inside [], remove char other than alphabet, separate words by space, change txt to lowercase
		outputParsed = ""	
		recording = True 
		wrotespace = False		
		for i in range(0, end):
			char = output[i]
			if recording:			
				if char == '[':
					recording = False
					if not wrotespace:
						outputParsed += ' '
						wrotespace = True
				else:
					if char.isalpha() and ord(char) < 128:
						outputParsed += char.lower()
						wrotespace = False
					else:
						if not wrotespace:
							outputParsed += ' '
							wrotespace = True
			else:
				if char == ']':
					recording = True
	
		return set(outputParsed.split())

	def __generateForCategory(self, category):
		# eliminate url duplicates
		if category == "Root":
			contentSummary = self.rootContentSummary
			urlSet = set(self.qprobe.url[category]) - self.rootUrlSet
		else:
			contentSummary = {}
			urlSet = set(self.qprobe.url[category])

		count = 1
		for url in urlSet:
			print "\n", count, "/", len(urlSet), "url"
			count += 1

			# retrieve words in each sample url
			content = self.__retrieveUrl(url)

			# update each word frequency
			for word in content:
				if word in contentSummary.keys():
					contentSummary[word] += 1
				else:
					contentSummary[word] = 1
	
				if category != "Root" and url not in self.rootUrlSet:
					if word in self.rootContentSummary.keys():
						self.rootContentSummary[word] += 1
					else:
						self.rootContentSummary[word] = 1
			self.rootUrlSet.add(url)

		# write to file in alphabetic order
		f = open(category + "-" + self.host + ".txt", 'w')
		for word in sorted(contentSummary):
			f.write(word + "#" + str(contentSummary[word]) + "\n")
		f.close()	

	def generate(self):
		print "\nExtracting topic content summaries..."

		temp = set()

		# generate content summary for each non leaf category
        for category in self.resultList["Root"]:
            if category in ["Computers", "Health", "Sports"] and category not in temp:
                print "\nCreating Content Summary for: " + category
                self.__generateForCategory(category)
                temp.add(category)

        print "\nCreating Content Summary for: Root"
        self.__generateForCategory("Root")