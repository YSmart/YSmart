YSmart: An SQL-to-MapReduce Translator

1. Overview

 YSmart is an SQL-to-MapReduce translator that translates an SQL command to Java codes for Hadoop. YSmart consists of two parts. The first part (SQL-to-XML), which convert a given SQL statement in a file to an XML file that represents the abstract syntax tree of the SQL command. The second part (XML-to-MapReduce) translates the XML file to Java codes. The two parts can be used individually.

As its name suggests, YSmart is only a translator from SQL to MapReduce. So, it gets an SQL file, and a data schema file as input and generated Hadoop jobs. Hive and Pig are also SQL-to-MapReduce translators, but unlike Hive or Pig, YSmart does not compile and execute translated queries, which means YSmart can be used on a machine with no Hadoop installed on it. On a machine with Hadoop, YSmart can be configured to not only translate but also tp compile and execute generated MapReduce jobs.

YSmart generates more efficient MapReduce jobs for complex queries with intra-query correlations compared to Hive and Pig. Please read YSmart's research paper for more details (http://www.cse.ohio-state.edu/hpcs/WWW/HTML/publications/papers/TR-11-7.pdf).

So far, YSmart is implemented as a teaching and learning tool for executing SQL queries using MapReduce programs. It is not a full functional database system. It only supports a subset of SQL SELECT queries. For example, it does not support "CREATE table" or "Load data" operations. Our experiments show that YSmart can support all SQL features that occur in the queries included in the test/ directory. These queries are:
    1) All the Star Schema Benchmark queries. The Star Schema Benchmark is derived from TPC-H and it is a benchmark to measure the performance of the data warehouses. All the ssb queries and a ssb schema are included in test/ssb_test directory.
    2) TPC-H query 1, 3, 5, 6, 10, 17, 18, 21. The queries and a tpch schema are included in test/tpch_test directory. 

YSmart does not support a subset of SQL SELECT features, which are listed below. You should avoid using these features when writing SQL queries. 
    1) user defined functions are not supported yet.
    2) window functions are not supported yet.
    3) CAST, CASE, BETWEEN, LIKE, NOT, IN are not supported yet.
    4) double quotes are not supported (use single quote instead).

Currently YSmart does not optimize the join sequence. Joins will be translated
in the sequence specified in the SQL file. YSmart is still under continuous development. Please refer to the project wiki
page to learn about our future plans (http://code.google.com/p/ysmart/wiki/Roadmap). 

2. Setup and Usage

We first introduce how to setup and use YSmart.
It is easy to install YSmart. Just download it from the website and extract it.

The simplest way to use YSmart is to execute translate.py that is a wrapper of the SQL-to-XML part and the XML-to-MapReduce part. The program needs five parameters.
 (1) The first one is a file that contains the input SQL command.
 (2) The second one is a schema file that describes the structures of the tables in the input SQL command. 
 (3) The third one is an optional query name (the default value is testquery).
 (4) The fourth one is an optional HDFS path that contains table data (the default value is YSmartInput/).
 (5) The fifth one is an optional HDFS path that contains query output data (the default value is YSmartOutput/).

The second parameter will be further introduced in Section 3. The fourth and the fifth parameters will be further introduced in Section 4.

After the translation, a directory named "result" will be created which contains:
 (1) a script which specifies how to compile the generated code and how to execute the code on Hadoop.
 (2) a directory named "YSmartCode" which contains all the source code files. The source code file is named with the pattern "queryname + number". Each source code file corresponds to one Hadoop job. The file with larger number will be executed first. You can refer to the script file to learn how to execute the codes on Hadoop.
 (3) a directory named "YSmartJar" which will contain the jar file if you set the YSmart to compile the generated codes. 

We then introduce YSmart's configuration options that are in the file XML2MapReduce/config.py. 

 (1) compile_jar: when set to True, YSmart will compile the generated code. Hadoop 0.20.x or Hadoop 0.21.x must be installed, and the  $HADOOP_HOME environment variable must be set prior to using this option.

 (2) exec_jar: when set to True, YSmart will execute the generated jars. Table data must be stored correctly on HDFS.

 (3) turn_on_correlation: when set to True, YSmart will use optimized translation as described in the YSmart paper.

 (4) advanced_agg: when set to True, YSmart will use map-phase aggregation that can reduce intermediate data size. 


3. Schema File Format

The schema file used in YSmart is a plain text file which describes the structures of one or more tables. Its format is defined as follows.
(1) Each line defines the structure of a single table.
(2) Each line contains multiple cells separated by "|".
(3) The first cell is the name of the table.
(4) Each one of the rest cells describes the name of a column and the data type of the column, separated by ":".
(5) Only four data types are allowed including INTEGER, DECIMAL, DATE, and TEXT.
(6) The file is not case-sensitive.

The tpch.schema file is included as an example schema file under the test/tpch_test directory, which describes the structures of eight tables in the TPC-H benchmark. YSmart needs the schema file to translate the TPC-H queries in this directory. We here use the first line of tpch.schema to explain the file.

NATION|N_NATIONKEY:INTEGER|N_NAME:TEXT|N_REGIONKEY:INTEGER|N_COMMENT:TEXT

The above line describes the schema of the NATION table. This table four columns. The type of the first column, N_NATIONKEY, is INTEGER.

We will extend the schema file format in the future versions to allow more features, such as whether a column is the primary key or nullable. 

4. Data Placement on HDFS

We first introduce how data should be placed on HDFS. YSmart requires that table data must be stored in a HDFS directory, which can be specified by users as a command line parameter. The default directory is "YSmartInput/" in the Hadoop user home. In that directory, the data of a table must be stored in a sub-directory that has the same name as the table. For example, if the HDFS directory /user/rubao/ysmart_input/ is used to store table data for YSmart, then all the data files for the table "NATION" must be stored in the sub-directory /user/rubao/ysmart_input/NATION/. Note that the name must be upper case. In that sub-directory, any files, no matter what their names are, would be viewed as data files for the table. However, sub-directories would be ignored (actually behavior undefined.)

Then we introduce how data should be organized in a data file. So far, YSmart only supports plain text data files. In such a file,
each line represents a record, and all the cells are separated by "|". The record must match the table structure defined in the schema file. For example, the following line shows a record in the TPC-H NATION table. It has four cells that are for the four columns in the table.

0|ALGERIA|0| haggle. carefully final deposits detect slyly agai

TPC-H data can be generated using dbgen tool, which is available on the TPC website. (http://www.tpc.org/tpch/)

Finally, we introduce where the output data of an SQL query are. Since a query could need a chain of MapReduce jobs, the final output data of the query are actually the output data of its last MapReduce job. First, job outputs are stored in a HDFS directory which can be specified by users as a command line parameter. The default directory is "YSmartOutput/" in the Hadoop user home. Second, in that directory, the "queryname1" sub-directory contains the final query output data.
