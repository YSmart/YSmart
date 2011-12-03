1. YSmart is an SQL-to-MapReduce translator that translates an SQL command to JAVA codes for Hadoop. YSmart consists of two parts. The first part (SQL-to-XML), which is implemented in C, is to convert the SQL statement in a file to an XML file. And the second part (XML-to-MapReduce), which is implemented in Python, is to translate the XML file to JAVA codes. This readme.txt is to describe the first part.

2. This SQL-to-XML part needs to use ANTLR v3.3 (http://www.antlr.org/download/antlr-3.3.tar.gz). We include it in our distribution. We provide an SQL grammar file (YSmart.g), which is used to generate the lexer and parser for SQL commands. We also provide a C program (YSmartMain.c), which is the main program for the SQL-to-XML part.

3. Manual install steps are as follows.

   1). Decompress ANTLR: 
         tar xzvf antlr-3.3.tar.gz

   2). Generate Lexer and Parser: 
         java -jar antlr-3.3/lib/antlr-3.3-complete.jar YSmart.g

   3). Install C runtime:
         cd antlr-3.3/runtime/C/dist
	 tar xzvf libantlr3c-3.1.4-SNAPSHOT.tar.gz
	 cd libantlr3c-3.1.4-SNAPSHOT
	 ./configure --prefix=/tmp/antrl_runtime_install_dir
	 make install
	 cd ../../../../../

   4). Compile and Link:
       	 gcc -o YSmartFront.exe YSmartMain.c YSmartLexer.c YSmartParser.c /tmp/antrl_runtime_install_dir/lib/libantlr3c.a -I . -I /tmp/antrl_runtime_install_dir/include/
       
       Notice that on a 64-bit machine, -m32 is needed.	          

4. Eventually, we can get the SQL-to-XML part, namely YSmartFront.exe (I like to use a Windows style file name on Unix), which converts an SQL file to an XML file. The command is "./YSmartFront.exe input_sql_file > output_xml_file". The input SQL file must contain an SQL SELECT command ended by ";". The output XML file represents the abstract grammar tree of the input SQL SELECT command. And the XML file will be used as an input to the next XML-to-MapReduce step.

5. The current version of YSmartFront.exe only accepts a limited range of standard SQL features. So far, the only thing we can say is that those features occured in the included TPC-H queries (in the tpch_test directory) are acceptable. Additionally, we hereby highlight several features that YSmart does not support so far.

   1). First of all, non-SELECT commands are unacceptable.
   2). Nested sub-queries are unacceptable. (They must be flattened as TPC-H Q17/Q18/Q21 in the tpch_test directory).
   3). UDFs (User Defined Function) are unacceptable.
   4). Window functions are unacceptable.
   5). CAST, CASE, BETWEEN, LIKE, NOT, IN, are unacceptable.
