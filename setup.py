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


import os;
import subprocess;
import sys;

CURRENT_DIR = os.getcwd();
FRONTEND_DIR = 'SQL2XML';
BACKEND_DIR = 'XML2MapReduce';
EXEC_DIR = 'bin';


def install_frontend():
	os.mkdir(CURRENT_DIR + '/' + EXEC_DIR);
	print '--------------------------------------------------------------------';	
	print 'Compiling front-end SQL queries lexer and parser ...';
	print '--------------------------------------------------------------------';
	os.chdir(CURRENT_DIR + '/' + FRONTEND_DIR);
	subprocess.check_call('tar xzvf antlr-3.3.tar.gz', shell=True);
	print '--------------------------------------------------------------------';	
	print 'Generating lexer and parser ...';
	print "java -jar antlr-3.3/lib/antlr-3.3-complete.jar YSmart.g"
	print '--------------------------------------------------------------------';
	subprocess.check_call('java -jar antlr-3.3/lib/antlr-3.3-complete.jar YSmart.g', shell=True)
	
	os.chdir(CURRENT_DIR + '/' + FRONTEND_DIR + '/antlr-3.3/runtime/C/dist');
	subprocess.check_call(['tar', 'xzvf', 'libantlr3c-3.1.4-SNAPSHOT.tar.gz', '-C', CURRENT_DIR + '/' + FRONTEND_DIR]);

	os.chdir(CURRENT_DIR + '/' + FRONTEND_DIR + '/libantlr3c-3.1.4-SNAPSHOT');
	subprocess.check_call('./configure --prefix=/tmp/antrl_runtime_install_dir', shell=True);
	subprocess.check_call('make install', shell=True);

	os.chdir(CURRENT_DIR + '/' + FRONTEND_DIR);
	print '--------------------------------------------------------------------';	
	print 'Compiling ...';
	print 'gcc -o YSmartFront.exe YSmartMain.c YSmartLexer.c YSmartParser.c /tmp/antrl_runtime_install_dir/lib/libantlr3c.a -I . -I /tmp/antrl_runtime_install_dir/include/';
	print '--------------------------------------------------------------------';	
	subprocess.check_call(['gcc', '-m32', '-o', 'YSmartFront.exe', 'YSmartMain.c', 'YSmartLexer.c', 'YSmartParser.c', \
				   '/tmp/antrl_runtime_install_dir/lib/libantlr3c.a', '-I', '.', '-I', '/tmp/antrl_runtime_install_dir/include/']);
	subprocess.check_call(['mv', 'YSmartFront.exe', CURRENT_DIR + '/' + EXEC_DIR]);
	print '--------------------------------------------------------------------';	
	print 'Front-end SQL queries lexer and parser have been compiled';
	print '--------------------------------------------------------------------';	

	print '--------------------------------------------------------------------';	
	print 'Preoparing back-end hadoop job generator';
	print '--------------------------------------------------------------------';	

	#print 'TODO: make a soft link of job generation program in ./bin/';

def install_backend():
	os.chdir(CURRENT_DIR)
	subprocess.check_call(['ln', '-sf', BACKEND_DIR + '/main.py', EXEC_DIR + '/main.py']);


	

def uninstall():
	print '--------------------------------------------------------------------';	
	print 'Cleaning front-end SQL queries lexer and parser ...'
	print '--------------------------------------------------------------------';	
	os.chdir(CURRENT_DIR + '/' + FRONTEND_DIR);
	subprocess.check_call(['rm', '-rf', 'antlr-3.3', 'libantlr3c-3.1.4-SNAPSHOT', '/tmp/antrl_runtime_install_dir']);
	subprocess.check_call(['rm', 'YSmartLexer.h', 'YSmartLexer.c', 'YSmartParser.h', 'YSmartParser.c', 'YSmart.tokens']);
	
	print '--------------------------------------------------------------------';	
	print 'Cleaning ' + EXEC_DIR + ' ...';
	print '--------------------------------------------------------------------';	
	os.chdir(CURRENT_DIR);
	subprocess.check_call(['rm', '-rf', './' + EXEC_DIR]);
	
	print '--------------------------------------------------------------------';	
	print 'Done';
	print '--------------------------------------------------------------------';	

def print_usage():
	print 'usage: ./setup.py install/uninstall';

def main():
	if (len(sys.argv) != 2):
		print_usage();
		sys.exit(0);
	if (sys.argv[1] == 'install'):
		install_frontend();
#		install_backend();
	elif (sys.argv[1] == 'uninstall'):
		uninstall();
	else:
		print_usage();
		sys.exit(0);
	
if __name__ == "__main__":
    main();





