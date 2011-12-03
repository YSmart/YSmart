YSMART: Yet another SQL-to-MapReduce Translator

1. Overview

 YSmart is an SQL-to-MapReduce translator that translates an SQL command to JAVA codes for Hadoop. YSmart consists of two parts. The first part (SQL-to-XML), which is implemented in C, is to convert the SQL statement in a file to an XML file that represents the abstract grammar tree of the SQL command. And the second part (XML-to-MapReduce), which is implemented in Python, is to translate the XML file to JAVA codes. The two parts can be used individually.

 As its name shows, YSmart is only a translator from SQL to MapReduce. So, its inputs are an SQL file and a data schema file, and its outputs are only generated JAVA codes that are used to execute an SQL command on Hadoop. But, unlike Hive or Pig, it is not YSmart's responsibility to compile and execute those codes, although YSmart can also be configured to do that. Therefore, YSmart can be used in a machine where even no Hadoop is installed. 

 The main advantage of YSmart over Hive or Pig is that it can efficiently translate complex queries that have intra-query correlations. Please read YSmart's research paper for more details (http://www.cse.ohio-state.edu/hpcs/WWW/HTML/publications/papers/TR-11-7.pdf).

 So far, YSmart is implemented as a teaching and learning tool for executing SQL queries using MapReduce programs. It is not a full functional database system. It does not support "CREATE table" or "Loading data". It only supports SQL SELECT queries. Our tests show that YSmart can support all SQL features that occur in the TPC-H queries included in the tpch_test directory.

2. Setup and Usage

 We first introduce how to setup and use YSmart.
 It is easy to install YSmart. Just execute "Python setup.py install". After that, a bin directory would be created.

 The simplest way to use YSmart is to execute translate.py that is a wrapper of the SQL-to-XML part and the XML-to-MapReduce part. The program needs five parameters.
 (1) The first one is a file that contains the input SQL command.
 (2) The second one is a file that describes the structures of the tables in the input SQL command. 
 (3) The third one is an optional query name (its default value is testquery).
 (4) The fourth one is an optional HDFS path that contains table data.
 (5) The fifth one is an optional HDFS path that contains query output data.

 The second parameter would be further introduced in Section 3. The fourth and the fifth parameters would be further introduced in Section 4.

 We then introduce YSmart's configuration options that are in the file XML2MapReduce/config.py. 

 (1) compile_jar: when it is True, YSmart will compile its generate code. Hadoop 0.21.0 must be installed, and $HADOOP_HOME$ must be setup.

 (2) exec_jar: when it is True, YSmart will execute its generated jars. Table data must be stored on HDFS directories.

 (3) turn_on_correlation: when it is True, YSmart will use optimized translation as described in the YSmart paper.

 (4) advanced_agg: when it is True, YSmart will use map-phase aggregation that can reduce intermediate data size. 


3. Schema File Format

A schema file used in YSmart is a plain text file to describe the structures of one or more tables. Its format is defined as follows.
(1) Each line defines the structure of a single table.
(2) Each line contains multiple cells separated by "|".
(3) The first cell is the name of a table.
(4) Each one of the rest cells describes the name of a column and the data type of the column, separated by ":".
(5) Only four data types are allowed including INTEGER, DECIMAL, DATE, and TEXT.
(6) The file is not case-sensitive.

An example file tpch.schema is included in the tpch_test directory, which describes the structures of eight tables in the TPC-H benchmark. The file is needed when using YSmart to translate the TPC-H queries in the directory. We here use the first line to explain the file.

NATION|N_NATIONKEY:INTEGER|N_NAME:TEXT|N_REGIONKEY:INTEGER|N_COMMENT:TEXT

The line describes the schema of table NATION that has four columns. For example, the type of the first column N_NATIONKEY is INTEGER.

We will extend the schema file format in the future version to allow more features, such as whether a column is the primary key or nullable. 

4. Data Placement on HDFS

We first introduce how data should be placed on HDFS. YSmart requires that table data must be stored in a HDFS directory, which can be specified by users as a command line parameter. The default directory is "YSmartInput/" in the Hadoop user home. In that directory, the data of a table must be stored in a sub-directory that has the same name as the table. For example, if the HDFS directory /user/rubao/ysmart_input/ is used to store table data for YSmart, then all the data files for the table "NATION" must be stored in the sub-directory /user/rubao/ysmart_input/NATION/. Note that the name must be upper case. In that sub-directory, any files, no matter what their names are, would be viewed as data files for the table. However, sub-directories would be ignored (actually behavior undefined.)

Then we introduce how data should be organized in a data file. So far, YSmart only supports plain text data file. In such a file,
each line represents a record, and all the cells are separated by "|". The record must match the table structure defined in the schema file. For example, the following line shows a record in the TPC-H NATION table. It has four cells that are for the four columns in the table.

0|ALGERIA|0| haggle. carefully final deposits detect slyly agai

TPC-H data can be generated using dbgen tool that can be found on TPC website. (http://www.tpc.org/tpch/)

Finally, we introduce where are the output data of an SQL query. Since a query could need a chain of MapReduce jobs, the final output data of the query are actually the output data of its last MapReduce job. First, job outputs are stored in a HDFS directory which can be specified by users as a command line parameter. The default directory is "YSmartOutput/" in the Hadoop user home. Second, in that directory,  the sub-directory with the name as "queryname1" contains the final query output data.
