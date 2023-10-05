William Porter

Intro-
  All the code for this project is found within the Eval.py file.
  The code for PageRank can be found here https://github.com/WPorter94/Pagerank.
  
BreakDown-
	Each measure is found in its own function. Each measure si self contained excpept for nDCG which uses a helper
	function(idealNDCG) and Fallout which calls recall and precision functions within it.
 
Description-
	eval.py is responsible for taking in 2 documents, one of document relevance and one of scored sets of documents.
	the files are tokenized and concantenated to house all the information needed in one dictionary. Other
	dictionaries are also used for data that might have been needed. eval.py outputs the results fo the program to 
	the specified output file
 
Libraries-
	os - used for checking if results file already exists in directory.
	sys - used to retrive command line arguments
	math - used to find logarithm
 
Dependencies- 
	-
 
Building/ running-
	on command line "python eval.py simple.trecrun qrels outputFile"
	where simple.trecrun holds the scored document sets and qrels holds document relevencies
	outputFile is any .eval file to be written to.    
