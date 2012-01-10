#!/usr/bin/env python

"""
   Copyright (c) 2012 The Ohio State University.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


import datetime
import os;
import subprocess;
import sys;

CURRENT_DIR = os.getcwd();
EXEC_DIR = 'bin';
TEMP_DIR = '.tmp';

def genXMLTree(queryFile, tmpFilePath):
	try:
		os.mkdir(TEMP_DIR);
	except:
		pass

	subprocess.check_call(EXEC_DIR + '/YSmartFront.exe ' +  queryFile + ' > ' + tmpFilePath, shell=True);

def genHadoopJobs(schemaFile, tmpFilePath, queryName, queryInputPath, queryOutputPath):
	#print 'TODO: call job generation program in ./bin/';
	os.chdir(CURRENT_DIR)
	cmd = 'python XML2MapReduce/main.py ' + schemaFile + ' ' + tmpFilePath + ' ' + queryName + ' ' + queryInputPath + ' ' + queryOutputPath
	print cmd
	subprocess.check_call(cmd, shell=True)

def print_usage():
	print 'usage 1: ./translate.py <query-file>.sql <schema-file>.schema';
	print 'usage 2: ./translate.py <query-file>.sql <schema-file>.schema <query-name> <query-input-path> <query-output-path>';

def main():
	if (len(sys.argv) != 6 and len(sys.argv) != 3):
		print_usage();
		sys.exit(0);

	queryFile = sys.argv[1];
	schemaFile = sys.argv[2];
	tmpFile = str(datetime.datetime.now()).replace(' ', '_') + '.xml';
	tmpFilePath = './' + TEMP_DIR + '/' + tmpFile;

	if (len(sys.argv) == 3):
		queryName = "testquery"
		queryInputPath = "YSmartInput/"
		queryOutputPath = "YSmartOutput/"
	else:
		queryName = sys.argv[3];
		queryInputPath = sys.argv[4];
		queryOutputPath = sys.argv[5];

	print '--------------------------------------------------------------------';	
	print 'Generating XML tree ...';
	genXMLTree(queryFile, tmpFilePath);

	print 'Generating Hadoop jobs ...';
	genHadoopJobs(schemaFile, tmpFilePath, queryName, queryInputPath, queryOutputPath);

	print 'Done';
	print '--------------------------------------------------------------------';
	subprocess.check_call(['rm', '-rf', './' + TEMP_DIR]);


	
if __name__ == "__main__":
    main();

