import sys
from probe import *
from summary import *

def main(argv):
	# parse input arguments
	accountKey = sys.argv[1]
	tes = float(sys.argv[2])
	tec = int(sys.argv[3])
	host = sys.argv[4]

	# classification
	qprobe = probe(host,accountKey, tec, tes)
	resultList = qprobe.build()

	# content summary
	contentSummary = summary(qprobe, resultList, host)
	contentSummary.generate()

if __name__ == '__main__':
	main(sys.argv[1:4])