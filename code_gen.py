#! /usr/bin/python

import sys
import os.path
import ystree
import copy

##input exp should be YFuncExp

math_func_dict = {"PLUS":" + ","MINUS":" - ","DIVIDE":" / ","MULTIPLY":" * "}

agg_func_list = ["SUM","AVG","COUNT","MAX","MIN","COUNT_DISTINCT"]

bool_func_dict = {"AND":" && ","OR":" || "}

rel_func_dict = {"EQ":" == ","GTH":" > ", "LTH":" < ","NOT_EQ":" != ","GEQ":" >= ","LEQ":" <= "}

packagepath = "edu/ohiostate/cse/ysmart/"
packagename = "edu.ohiostate.cse.ysmart"

################Function definion. For aggregate functions and user define functions

def __func_print__(fo):

	print >>fo, "\tpublic String AVG(String[] input){\n"
	print >>fo, "\t\tDouble res = 0;"
	print >>fo,"\t\tfor(int i=0;i<input.size();i++){\n"
	print >>fo,"\t\t\tres += Double.parseDouble(input[i]);"
	print >>fo,"\t\t}\n"
	print >>fo,"\t\tres = res/input.size();"
	print >>fo, "\t\treturn res.toString();"
	print >>fo, "\t}\n"


	print >>fo, "\tpublic String SUM(String[] input){\n"
	print >>fo, "\t\tDouble res = 0;"
	print >>fo, "\t\tfor(int i=0;i<input.size();i++){\n"
	print >>fo, "\t\t\tres += Double.parseDouble(input[i]);"
	print >>fo, "\t\t}\n"
	print >>fo, "\t\treturn res.toString();"
	print >>fo, "\t}\n"


	print >>fo, "\tpublic String COUNT(String[] input){\n"
	print >>fo, "\t\treturn input.size().toString();"
	print >>fo, "\t}\n"


	print >>fo, "\tpublic String MAX(String[] input){\n"
	print >>fo, "\t\t Double max = 0;"
	print >>fo, "\t\tfor(int i=0;i<input.size();i++){\n"
	print >>fo, "\t\t\tif(i==0){\n"
	print >>fo, "\t\t\t\tmax = Double.parseDouble(input[i]);"
	print >>fo, "\t\t\t}else if(Double.parseDouble(input[i]) > max){\n"
	print >>fo, "\t\t\t\tmax = Double.parseDouble(input[i]);"
	print >>fo, "\t\t\t}\n"
	print >>fo, "\t\t}\n"
	print >>fo, "\t\treturn max.toString()"
	print >>fo, "\t}\n"


	print >>fo, "\tpublic String MIN(String[] input){\n"
	print >>fo, "\t\tDouble min = 0;"
	print >>fo, "\t\tfor(int i=0;i<input.size();i++){\n"
	print >>fo, "\t\t\tif(i==0){\n"
	print >>fo, "\t\t\t\tmin = Double.parseDouble(input[i]);"
	print >>fo, "\t\t\t}else if(Double.parseDouble(input[i]) < max){\n"
	print >>fo, "\t\t\t\tmin = Double.parseDouble(input[i]);"
	print >>fo, "\t\t\t}\n"
	print >>fo, "\t\t}\n"
	print >>fo, "\t\treturn min.toString()"
	print >>fo, "\t}\n"


	print >>fo,"\tpublic String COUNT_DISTINCT(String[] input){\n"
	print >>fo, "\t\treturn \"\""
	print >>fo, "\t}\n"

###############end of function definition

### start translating

###__select_func_convert_to_java__ is mainly used to convert the math function in the select list into jave expression
####input: @exp: the sql expression than you want to translate. If the exp is an agg operation, it will return the jave exp of its argument
####

def __select_func_convert_to_java__(exp,buf_dict):

	return_str = ""

	if not isinstance(exp,ystree.YFuncExp):
		return
	
	if exp.func_name in math_func_dict.keys():
##### +, -, *, / operations

		para1 = exp.parameter_list[0]
		para2 = exp.parameter_list[1]
		
		if isinstance(para1,ystree.YRawColExp):
			return_str += "("
			return_str += __para_to_java__(para1.column_type,para1.column_name,buf_dict[para1.table_name])

		elif isinstance(para1,ystree.YFuncExp):
			return_str += "("
			return_str += __select_func_convert_to_java__(para1,buf_dict)

		else:
			#return_str += __para_to_java__(para1.cons_type,para1.cons_value,None)
			return_str += "("
			return_str += para1.cons_value
	
		if exp.func_name == "PLUS":
			return_str += " + "
		elif exp.func_name == "MINUS":
			return_str += " - "
		elif exp.func_name == "DIVIDE":
			return_str += " /  "
		elif exp.func_name == "MULTIPLY":
			return_str += " * "

		if isinstance(para2,ystree.YRawColExp):
			return_str += __para_to_java__(para2.column_type,para2.column_name,buf_dict[para2.table_name])
			return_str += ")"

		elif isinstance(para2,ystree.YFuncExp):
			return_str += __select_func_convert_to_java__(para2,buf_dict)
			return_str += ")"

		else:
			#return_str += __para_to_java__(para2.cons_type,para2.cons_value,None)
			return_str += para2.cons_value
			return_str += ")"
		

	elif exp.func_name in agg_func_list:

		if len(exp.parameter_list) != 1:
			print "This should be Grammar error. "
			print 1/0

		para = exp.parameter_list[0]
		
		if isinstance(para,ystree.YRawColExp):
			return_str += __para_to_java__(para.column_type,para.column_name,buf_dict[para.table_name])

		elif isinstance(para,ystree.YFuncExp):
			return_str += "("
			return_str += __select_func_convert_to_java__(para, buf_dict)
			return_str += ")"

		else:
			#return_str += __para_to_java__(para.cons_type,para.cons_value,None)
			return_str += str(para.cons_value)
	

	else:
		print "user defined functioin not supported yet",exp.func_name
		print 1/0
		
	return return_str

def __para_to_java__(para_type,value,buf_name):
	return_str = ""

	if buf_name is not None:

		if para_type == "INTEGER":
			return_str = "Integer.parseInt(" + buf_name + "[" + str(value) + "])"
		
		elif para_type == "DECIMAL":
			return_str = "Double.parseDouble(" + buf_name + "[" +str(value) + "])"

		elif para_type == "TEXT":
			return_str =  buf_name + "[" + str(value) + "]"
		
		elif para_type == "DATE":
			return_str = buf_name + "[" + str(value) + "]"

		else:
			print 1/0

	else:
		if para_type == "INTEGER":
			return_str = str(value)
		
		elif para_type == "DECIMAL":
			return_str = str(value)

		elif para_type == "TEXT":
			return_str =  str(value) 
		
		elif para_type == "DATE":
			return_str = str(value)

		else:
			print 1/0
		

	return return_str

def __operator_to_java__(op_type,op_name,op_list):
	
	res_str = ""

	if op_name in rel_func_dict.keys(): 
		if op_type == "INTEGER" or op_type == "DECIMAL":
			res_str = op_list[0] + rel_func_dict[op_name] + op_list[1]

		elif op_type == "TEXT":
			res_str = op_list[0] + ".compareTo(" + op_list[1] + ")" + rel_func_dict[op_name] +"0"

		elif op_type =="DATE":
			res_str = op_list[0] + ".compareTo(" + op_list[1] + ")" + rel_func_dict[op_name] +"0"

	elif op_name in math_func_dict.keys():
		if op_type == "INTEGER" or op_type == "DECIMAL":
			res_str = op_list[0] + math_func_dict[op_name] + op_list[1]

		elif op_type == "TEXT":
			print 1/0

		elif op_type == "DATE":
			print 1/0

	elif op_name in bool_func_dict.keys():
		count = 0
		for tmp in op_list:
			count = count +1
			if count != len(op_list):
				res_str = res_str + tmp + bool_func_dict[op_name]
			else:
				res_str = res_str + tmp
	else:
		print 1/0

	return res_str



#### translate the where exp to java. not for the groupby node
def __where_convert_to_java__(exp,buf_dict):

	return_str = ""	

	if isinstance(exp,ystree.YFuncExp):

		if exp.func_name in rel_func_dict.keys() or exp.func_name in math_func_dict.keys():
			tmp_list = []
			op_type = None

			for tmp_exp in exp.parameter_list:

				if isinstance(tmp_exp,ystree.YRawColExp):
					if tmp_exp.table_name != "AGG":
						tmp_str = __para_to_java__(tmp_exp.column_type,tmp_exp.column_name,buf_dict[tmp_exp.table_name])
					else:
						tmp_str = buf_dict[tmp_exp.table_name] + "[" + str(tmp_exp.column_name) + "]"
					tmp_list.append(tmp_str)
					op_type = tmp_exp.column_type

				elif isinstance(tmp_exp,ystree.YFuncExp):
					tmp_str = __where_convert_to_java__(tmp_exp,buf_dict)
					tmp_list.append(tmp_str)
					op_type = "DECIMAL"

				else:
					tmp_str = tmp_exp.cons_value
					tmp_list.append(tmp_str)
					op_type = tmp_exp.cons_type

			if len(tmp_list) != 2:
				print 1/0

			return_str = __operator_to_java__(op_type,exp.func_name,tmp_list)

		elif exp.func_name in agg_func_list:
			tmp_exp = exp.parameter_list[0]
			if isinstance(tmp_exp,ystree.YRawColExp):
				return_str = buf_dict[tmp_exp.table_name] + "[" + str(tmp_exp.column_name) + "]"

			elif isinstance(tmp_exp,ystree.YFuncExp):
				return_str = __where_convert_to_java__(tmp_exp,buf_dict)


		elif exp.func_name in bool_func_dict.keys():
			tmp_list = []
			op_type = "BOOLEAN"
			
			for tmp_exp in exp.parameter_list:

				tmp_str = __where_convert_to_java__(tmp_exp,buf_dict)
				tmp_list.append(tmp_str)

			return_str = __operator_to_java__(op_type,exp.func_name,tmp_list)

		else:
			return_str += "("
			if exp.func_name == "IS":
				para1 = exp.parameter_list[0]
				para2 = exp.parameter_list[1]

				if isinstance(para1,ystree.YRawColExp):
					return_str += buf_dict[para1.table_name] + "[" + str(para1.column_name) + "]"
				else:
					print 1/0

				return_str +=  ".compareTo(\""

				if isinstance(para2,ystree.YConsExp):
					return_str += str(para2.cons_value)
					return_str += "\") == 0"
				else:
					print 1/0

				return_str += ")"
				

	elif isinstance(exp, ystree.YConsExp):
		if exp.cons_type == "BOOLEAN":
			if exp.cons_value == "FALSE":
				return "false"
			else:
				return "true"


	return return_str

sql_type_to_java = {"INTEGER":"IntWritable","DECIMAL":"DoubleWritable","TEXT":"Text","DATE":"Text"}
java_type_to_sql = {"IntWritable":"INTEGER","Double":"DECIMAL","Text":"TEXT","Date":"DATE"}

##input arg should be an exp list
def __get_key_value_type__(exp_list):
	res = ""

	if len(exp_list) !=1:
		res = sql_type_to_java["TEXT"]
	
	else:

		exp = exp_list[0]

		if isinstance(exp,ystree.YRawColExp):
			res = sql_type_to_java[exp.column_type]

		elif isinstance(exp,ystree.YFuncExp):
			res = sql_type_to_java["DECIMAL"]

		else:
			res = sql_type_to_java[exp.cons_type]

	return res


def __gen_des__(fo):
	print >>fo,"/*\n\
		The following code is automatically generated by YSmart.\n\
		Author: Rubao Lee, Yuan Yuan	\n\
		Email: yuanyu@cse.ohio-state.edu\n\
*/\n"

def __gen_header__(fo):
	print >>fo, "package " + packagename + ";" 
	print >>fo,"import java.io.IOException;"
	print >>fo,"import java.util.*;"
	print >>fo,"import java.text.*;"
	print >>fo,"import org.apache.hadoop.fs.Path;"
	print >>fo,"import org.apache.hadoop.conf.*;"
	print >>fo,"import org.apache.hadoop.io.*;"
	print >>fo,"import org.apache.hadoop.mapred.*;"
	print >>fo,"import org.apache.hadoop.util.*;"
	print >>fo,"\n"

def __gen_mr_key__(exp_list,type,buf_dict):

	res = ""
	
	if len(exp_list) == 0:
		res = "\" \""
		return res

	for exp in exp_list:

		if isinstance(exp,ystree.YRawColExp):
			res +=  __para_to_java__(exp.column_type,exp.column_name,buf_dict[exp.table_name]) 
			if type == "Text":
				res += "+ \"|\" +"
			else:
				res += "+"

		elif isinstance(exp,ystree.YFuncExp):
			res += __select_func_convert_to_java__(exp,buf_dict)
			if type == "Text":
				res += "+ \"|\" +"
			else:
				res += "+"

		else:
			res +=  __para_to_java__(exp.cons_type,exp.cons_value,None) 
			if type == "Text":
				res += "+ \"|\" +"
			else:
				res += "+"

	res = res[:-1]
	
	return res	


def __gen_mr_value__(exp_list,type,buf_dict):
	res = ""

	if len(exp_list) == 0:
		res = "\" \""
		return res

	for exp in exp_list:
		if isinstance(exp,ystree.YRawColExp):
			res +=  __para_to_java__(exp.column_type,exp.column_name,buf_dict[exp.table_name]) 
			if type == "Text":
				res += "+ \"|\" +"
			else:
				res += "+"

		elif isinstance(exp,ystree.YFuncExp):
			res += __select_func_convert_to_java__(exp,buf_dict)
			if type == "Text":
				res += "+ \"|\" +"
			else:
				res += "+"
			
		else:
			res += __para_to_java__(exp.cons_type,exp.cons_value,None)
			if type == "Text":
				res += "+ \"|\" +"
			else:
				res += "+"
			
	res = res[:-1]

	return res

def __get_max_index__(exp_list):
	ret = -1

	for exp in exp_list:
		if isinstance(exp,ystree.YRawColExp):
			if ret < int(exp.column_name):
				ret = int(exp.column_name)
		elif isinstance(exp,ystree.YFuncExp):
			col_list = []
			ystree.__get_func_para__(exp,col_list)
			for x in col_list:
				if ret< int(x.column_name):
					ret = int(x.column_name)
	ret = ret +1
	return ret


def __tablenode_gen_mr__(tree,fo):

###
###	This is the map part
###
	line_buffer = "line_buf"
	if tree.select_list is None:
		print "no select list for table node"
		return 

	buf_dict = {}

	buf_dict[tree.table_name] = line_buffer
	buf_dict[tree.table_alias] = line_buffer
	
	#map_key_type = __get_key_value_type__(tree.select_list.tmp_exp_list[:1])	
	#map_key = __gen_mr_key__(tree.select_list.tmp_exp_list[:1],map_key_type,buf_dict)
	map_key_type = "NullWritable"
	map_value_type = __get_key_value_type__(tree.select_list.tmp_exp_list)	
	map_value = __gen_mr_value__(tree.select_list.tmp_exp_list,map_value_type,buf_dict)

	max_index = __get_max_index__(tree.select_list.tmp_exp_list) 


	print >>fo,"\tpublic static class Map extends MapReduceBase implements Mapper<Object, Text,"+map_key_type+","+map_value_type+">{\n"

	print >>fo,"\t\tpublic void map(Object key, Text value, OutputCollector<"+ map_key_type + ","+map_value_type + "> output, Reporter reporter) throws IOException{\n"
	
	print >>fo,"\t\t\tString line = value.toString();"

	print >>fo,"\t\t\tString[] "+ line_buffer +" = new String["+ str(max_index)+"];"
	print >>fo, "\t\t\tint prev=0,i=0,n=0;"
	print >>fo, "\t\t\tfor(i=0,n=0,prev=0;i<line.length();i++){\n"
	print >>fo, "\t\t\t\tif (line.charAt(i) == \'|\'){"
	print >>fo, "\t\t\t\t\t" + line_buffer + "[n] = line.substring(prev,i);"
	print >>fo, "\t\t\t\t\tn = n+1;"
	print >>fo, "\t\t\t\t\tprev = i+1;"
	print >>fo, "\t\t\t\t}"
	print >>fo, "\t\t\t\tif(n == "+str(max_index)+")"
	print >>fo, "\t\t\t\t\tbreak;"
	print >>fo,"\t\t\t}\n"

	if tree.where_condition is None:
		print >>fo,"\t\t\tNullWritable key_op = NullWritable.get();"
		tmp_output =  "\t\t\toutput.collect(" 
		#tmp_output += "new " + map_key_type + "(" + map_key + ")" 
		tmp_output += "key_op" 
		tmp_output += " , "
		tmp_output += "new " + map_value_type + "(" + map_value + ")" 
		tmp_output += ");"

		print >>fo, tmp_output


	else:
		where_str = "\t\t\tif("
		where_str +=__where_convert_to_java__(tree.where_condition.where_condition_exp,buf_dict)
		where_str += "){\n"
		print >>fo,where_str

		print >>fo,"\t\t\t\tNullWritable key_op = NullWritable.get();"
		tmp_output =  "\t\t\t\toutput.collect(" 
		#tmp_output += "new " + map_key_type + "(" + map_key + ")" 
		tmp_output += "key_op"
		tmp_output += " , "
		tmp_output += "new " + map_value_type + "(" + map_value + ")" 
		tmp_output += ");"

		print >>fo, tmp_output
		
		print >>fo,"\t\t\t}" # end of if
		

	print >>fo,"\t\t}\n"

	print >>fo,"\t}\n"

###
### no reduce part for the table_node
###
	__gen_main__(tree,fo,map_key_type,map_value_type,map_key_type,map_value_type,False)

def __orderby_gen_mr__(tree,fo):

	line_buffer = "line_buf"

	buf_dict = {}
	for x in tree.table_list:
		buf_dict[x] = line_buffer
	
	od_len = len(tree.order_by_clause.orderby_exp_list)

	if isinstance(tree.child,ystree.TableNode):
		map_key_type = __get_key_value_type__(tree.order_by_clause.orderby_exp_list)
                map_value = __gen_mr_value__(tree.child.select_list.tmp_exp_list,map_value_type,buf_dict)
		map_value_type = __get_key_value_type__(tree.child.select_list.tmp_exp_list)
		map_key = __gen_mr_key__(tree.child.select_list.tmp_exp_list[:od_len],map_key_type,buf_dict)
		max_index = __get_max_index__(tree.child.select_list.tmp_exp_list)
	else:
		map_key = ""
		for i in range(0,od_len):
			map_key += line_buffer + "[" + str(i) + "] +"
			map_key += "\"|\"+"
		map_key = map_key[:-1]

		map_key_type = "Text"

		map_value = ""
		for i in range(od_len,len(tree.child.select_list.tmp_exp_list)):
			map_value += line_buffer + "[" + str(i) + "] +"
			map_value += "\"|\"+"

		map_value = map_value[:-1]

		map_value_type = "Text"
		max_index = len(tree.child.select_list.tmp_exp_list)


	print >>fo,"\tpublic static class Map extends MapReduceBase implements Mapper<Object, Text,"+map_key_type+","+map_value_type+">{\n"

	print >>fo,"\t\tpublic void map(Object key, Text value, OutputCollector<"+ map_key_type + ","+map_value_type + "> output, Reporter reporter) throws IOException{\n"
	
	print >>fo,"\t\t\tString line = value.toString();"

	print >>fo,"\t\t\tString[] "+ line_buffer +" = new String["+ str(max_index)+"];"
	print >>fo, "\t\t\tint prev=0,i=0,n=0;"
	print >>fo, "\t\t\tfor(i=0,n=0,prev=0;i<line.length();i++){\n"
	print >>fo, "\t\t\t\tif (line.charAt(i) == \'|\'){"
	print >>fo, "\t\t\t\t\t" + line_buffer + "[n] = line.substring(prev,i);"
	print >>fo, "\t\t\t\t\tn = n+1;"
	print >>fo, "\t\t\t\t\tprev = i+1;"
	print >>fo, "\t\t\t\t}"
	print >>fo, "\t\t\t\tif(n == "+str(max_index)+")"
	print >>fo, "\t\t\t\t\tbreak;"
	print >>fo,"\t\t\t}\n"

        if not isinstance(tree.child,ystree.TableNode) or tree.child.where_condition is None:
                tmp_output = "\t\t\toutput.collect("
                tmp_output += "new " + map_key_type + "(" + map_key +")"
                tmp_output += ","
                tmp_output += "new " + map_value_type + "(" + map_value + ")"
                tmp_output += ");"

                print >>fo, tmp_output

        else:
                where_str = "\t\t\tif("
                where_str +=__where_convert_to_java__(tree.child.where_condition.where_condition_exp,buf_dict)
                where_str += "){\n"
                print >>fo,where_str

                tmp_output =  "\t\t\t\toutput.collect( "
                tmp_output += "new " + map_key_type + "(" + map_key +")"
                tmp_output += ","
                tmp_output += "new " + map_value_type + "(" + map_value + ")"
                tmp_output += ");"

                print >>fo, tmp_output

                print >>fo,"\t\t\t}" # end of if

	print >>fo,"\t\t}\n"
	print >>fo,"\t}\n"


### reduce part

	reduce_key_type = "NullWritable"
        reduce_value_type = "Text"

        print >>fo,"\tpublic static class Reduce extends MapReduceBase implements Reducer<"+ map_key_type+","+map_value_type+","+reduce_key_type+","+reduce_value_type+">{\n"

        print >>fo,"\t\tpublic void reduce("+map_key_type+" key, Iterator<"+map_value_type+"> values, OutputCollector<"+reduce_key_type+","+reduce_value_type+"> output, Reporter reporter) throws IOException{\n"

	print >>fo, "\t\t\tNullWritable key_op = NullWritable.get();"

	print >>fo,"\t\t\twhile(values.hasNext()){\n"
	
	print >>fo, "\t\t\t\tString tmp = values.next().toString();"

	print >>fo, "\t\t\t\toutput.collect(key_op,new Text(tmp));" 

	print >>fo, "\t\t\t}\n"

	print >>fo,"\t\t}\n"

	print >>fo,"\t}\n"

#### generate main	

	key_spec = ""
	for i in range(0,od_len):
		k= i+1
		key_spec += "-k" + str(k) + "," + str(k) 
		exp = tree.order_by_clause.orderby_exp_list[i]
		if exp.get_value_type() in ["INTEGER","DECIMAL"]:
			key_spec += "n"

		order= tree.order_by_clause.order_indicator_list[i]
		if order == "DESC":
			key_spec += "r"
		key_spec += " "

	print >>fo,"\tpublic static void main(String[] args) throws Exception{\n"

	print >>fo,"\t\tJobConf conf = new JobConf("+fo.name.split(".java")[0]+".class);"
	print >>fo,"\t\tconf.setJobName(\"ysmart\");"
	print >>fo,"\t\tconf.setMapOutputKeyClass(" + map_key_type+".class);"
	print >>fo,"\t\tconf.setMapOutputValueClass(" + map_value_type+ ".class);"
	print >>fo,"\t\tconf.setOutputKeyClass("+reduce_key_type+".class);"
	print >>fo,"\t\tconf.setOutputValueClass("+reduce_value_type+".class);"
	print >>fo,"\t\tconf.setMapperClass(Map.class);"
	print >>fo,"\t\tconf.setReducerClass(Reduce.class);"
	print >>fo,"\t\tconf.set(JobContext.MAP_OUTPUT_KEY_FIELD_SEPERATOR, \"|\");"
	print >>fo,"\t\tconf.setKeyFieldComparatorOptions(\"" +key_spec + "\");"
	print >>fo,"\t\tFileInputFormat.addInputPath(conf, new Path(args[0]));"
	print >>fo,"\t\tFileOutputFormat.setOutputPath(conf, new Path(args[1]));"
	print >>fo, "\t\tJobClient.runJob(conf);"

        print >>fo,"\t}\n"


def __groupby_func_name__(exp):
	if not isinstance(exp,ystree.YFuncExp):
		return None

	if exp.func_name in  agg_func_list:
		return exp.func_name

	for x in exp.parameter_list:
		if isinstance(x,ystree.YFuncExp):
			tmp_name = __groupby_func_name__(x) 
			if tmp_name is not None:
				return tmp_name

def __groupby_gen_mr__(tree,fo):

###
###	This is the map part
###
	
	line_buffer = "line_buf"
	
	if tree.select_list is None or tree.child.select_list is None:
		print "select list in None  when generating code for groupby node"
		print 1/0

	buf_dict = {}
	for x in tree.child.table_list:
		buf_dict[x] = line_buffer

	if tree.group_by_clause is None:
		print 1/0
	else:
		gb_len = len(tree.group_by_clause.groupby_exp_list)

	exp_list = list(tree.child.select_list.tmp_exp_list)
	if isinstance(tree.child,ystree.TableNode):
		map_key_type = __get_key_value_type__(tree.group_by_clause.groupby_exp_list)
		map_key = __gen_mr_key__(tree.child.select_list.tmp_exp_list[:gb_len],map_key_type,buf_dict)
		map_value_type = __get_key_value_type__(tree.child.select_list.tmp_exp_list[gb_len:])
		map_value = __gen_mr_value__(tree.child.select_list.tmp_exp_list[gb_len:],map_value_type,buf_dict)
		if tree.child.where_condition is not None:
			exp_list.append(tree.child.where_condition.where_condition_exp)
		max_index = __get_max_index__(exp_list)
	else:
### in this case, do nothing, just output all the input
		map_key = ""
		map_key_type = "Text"
		for i in range(0,gb_len):
			map_key += line_buffer + "[" + str(i) + "]" + "+ \"|\"+"
		map_key = map_key[:-1]

		map_value_type = "Text"
		map_value = ""
		for i in range(gb_len,len(tree.child.select_list.tmp_exp_list)):
			map_value += line_buffer + "[" + str(i) + "]" + "+ \"|\"+"
		map_value = map_value[:-1]
		max_index = len(tree.child.select_list.tmp_exp_list)
		


	print >>fo,"\tpublic static class Map extends MapReduceBase implements Mapper<Object, Text,"+ map_key_type+","+map_value_type+">{\n"

	print >>fo,"\t\tpublic void map(Object key, Text value, OutputCollector<"+map_key_type+","+map_value_type+"> output, Reporter reporter) throws IOException{\n"
	
	print >>fo,"\t\t\tString line = value.toString();"
	print >>fo,"\t\t\tString[] "+ line_buffer +" = new String["+ str(max_index)+"];"
	print >>fo, "\t\t\tint prev=0,i=0,n=0;"
	print >>fo, "\t\t\tfor(i=0,n=0,prev=0;i<line.length();i++){\n"
	print >>fo, "\t\t\t\tif (line.charAt(i) == \'|\'){"
	print >>fo, "\t\t\t\t\t" + line_buffer + "[n] = line.substring(prev,i);"
	print >>fo, "\t\t\t\t\tn = n+1;"
	print >>fo, "\t\t\t\t\tprev = i+1;"
	print >>fo, "\t\t\t\t}"
	print >>fo, "\t\t\t\tif(n == "+str(max_index)+")"
	print >>fo, "\t\t\t\t\tbreak;"
	print >>fo,"\t\t\t}\n"


	if not isinstance(tree.child,ystree.TableNode) or tree.child.where_condition is None:
		tmp_output = "\t\t\toutput.collect("
		tmp_output += "new " + map_key_type + "(" + map_key +")"
		tmp_output += ","
		tmp_output += "new " + map_value_type + "(" + map_value + ")"
		tmp_output += ");"

		print >>fo, tmp_output

	else:
		where_str = "\t\t\tif("
                where_str +=__where_convert_to_java__(tree.child.where_condition.where_condition_exp,buf_dict)
                where_str += "){\n"
                print >>fo,where_str

                tmp_output =  "\t\t\t\toutput.collect( "
		tmp_output += "new " + map_key_type + "(" + map_key +")"
		tmp_output += ","
		tmp_output += "new " + map_value_type + "(" + map_value + ")"
		tmp_output += ");"

		print >>fo, tmp_output

                print >>fo,"\t\t\t}" # end of if


	print >>fo,"\t\t}\n"	

	print >>fo,"\t}\n"

###
### This is the reduce part
###
	line_counter = "al_line"
	agg_buffer = "result"
	d_count_buffer = "d_count_buf"

	buf_dict = {}
	for x in tree.table_list:
		buf_dict[x] = line_buffer
	i = 0
	for i in range(0,len(tree.select_list.tmp_exp_list)):
		exp = tree.select_list.tmp_exp_list[i]
		if not isinstance(exp,ystree.YRawColExp):
			break

	if i ==0:
		i = 1

	#reduce_key_type = __get_key_value_type__(tree.select_list.tmp_exp_list[:i])
	#reduce_value_type = __get_key_value_type__(tree.select_list.tmp_exp_list[i:])
	reduce_key_type = "NullWritable"
	reduce_value_type = "Text"

	print >>fo,"\tpublic static class Reduce extends MapReduceBase implements Reducer<"+ map_key_type+","+map_value_type+","+reduce_key_type+","+reduce_value_type+">{\n"
	
	print >>fo,"\t\tpublic void reduce("+map_key_type+" key, Iterator<"+map_value_type+"> values, OutputCollector<"+reduce_key_type+","+reduce_value_type+"> output, Reporter reporter) throws IOException{\n"
	print >>fo, "\t\t\tDouble[] "+agg_buffer+" = new Double[" + str(len(tree.select_list.tmp_exp_list)) + "];"	

	print >>fo, "\t\t\tArrayList[] "+d_count_buffer+" = new ArrayList[" + str(len(tree.select_list.tmp_exp_list)) + "];"

	print >>fo, "\t\t\tint " + line_counter + " = 0;"
	
	print >>fo, "\t\t\tString tmp = \"\";"

	print >>fo, "\t\t\tfor(int i=0;i<"+str(len(tree.select_list.tmp_exp_list))+";i++){\n"

	print >>fo, "\t\t\t\t"+agg_buffer+"[i] = 0.0;"

	print >>fo, "\t\t\t\t" + d_count_buffer + "[i] = new ArrayList();"

	print >>fo, "\t\t\t}\n"

	print >>fo,"\t\t\twhile(values.hasNext()){\n"
	
	print >>fo, "\t\t\t\ttmp = values.next().toString();"

	if map_key_type == "Text":

		print >>fo, "\t\t\t\ttmp = key.toString().concat(tmp);"

	else:
		print >>fo, "\t\t\t\ttmp = key.toString().concat(\"|\" + tmp);"

	print >>fo, "\t\t\t\tString[] " + line_buffer + " = tmp.split(\"\\\|\");"


	for i in range(0,len(tree.select_list.tmp_exp_list)):
		exp = tree.select_list.tmp_exp_list[i]
		if isinstance(exp,ystree.YFuncExp):
			tmp_output = __select_func_convert_to_java__(exp,buf_dict)
			tmp_name = __groupby_func_name__(exp)
			if tmp_name == "SUM" or tmp_name == "AVG":
				print >>fo, "\t\t\t\t"+agg_buffer+"[" + str(i) + "] = "+agg_buffer+"[" +str(i) + "] + " + tmp_output + ";" 

			elif tmp_name == "COUNT":
				pass

			elif tmp_name == "COUNT_DISTINCT":
				print >>fo, "\t\t\t\tif("+d_count_buffer+"[" + str(i) + "].contains(" +tmp_output+  ") == false)"
				print >>fo, "\t\t\t\t\t"+d_count_buffer+"[" + str(i) + "].add(" + tmp_output + ");" 

			elif tmp_name == "MAX":
				print >>fo,"\t\t\t\tif("+line_counter+"==0)"
				print >>fo,"\t\t\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)" + tmp_output + ";"
				print >>fo,"\t\t\t\telse{"
				print >>fo, "\t\t\t\t\tif("+agg_buffer+"[" + str(i) + "] < " + tmp_output + ")"
				print >>fo, "\t\t\t\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)" + tmp_output + ";"  
				print >>fo, "\t\t\t\t}" 

			elif tmp_name == "MIN":
				print >>fo,"\t\t\t\tif(!i)"
				print >>fo,"\t\t\t\t\t"+agg_buffer+"[" + str(i) + "] = " + tmp_output + ";"
				print >>fo,"\t\t\t\telse{"
				print >>fo, "\t\t\t\t\tif("+agg_buffer+"[" + str(i) + "] > " + tmp_output + ")"
				print >>fo, "\t\t\t\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)" + tmp_output + ";"  
				print >>fo, "\t\t\t\t}" 

	print >>fo, "\t\t\t\t" + line_counter + "++;"
	
	print >>fo, "\t\t\t}\n"

	print >>fo, "\t\t\tString[] " + line_buffer + " = tmp.split(\"\\\|\");"
	

	for i in range(0,len(tree.select_list.tmp_exp_list)):
		exp = tree.select_list.tmp_exp_list[i]
		if isinstance(exp,ystree.YFuncExp):
			tmp_name = __groupby_func_name__(exp)
			if tmp_name == "AVG":
					print >>fo, "\t\t\t"+agg_buffer+"[" + str(i) + "] = "+agg_buffer+"[" + str(i) + "] /" + line_counter+ ";" 

			elif tmp_name == "COUNT":
				print >>fo, "\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)"+ line_counter + ";" 

			elif tmp_name == "COUNT_DISTINCT":
				print >>fo, "\t\t\t"+agg_buffer+ "[" + str(i) + "] = (double)"+d_count_buffer+"["+ str(i) +"].size();"  
	
	for i in range(0,len(tree.select_list.tmp_exp_list)):
		exp = tree.select_list.tmp_exp_list[i]
		if not isinstance(exp,ystree.YRawColExp):
			break

	col_list = []
	if tree.having_clause is not None:
		ystree.__get_gb_list__(tree.having_clause.where_condition_exp,col_list)

	having_len = len(col_list)

	if i==0:

		reduce_value = ""

		for j in range(0,len(tree.select_list.tmp_exp_list)-having_len):
		#for j in range(1,len(tree.select_list.tmp_exp_list)):
			exp = tree.select_list.tmp_exp_list[j]
			if isinstance(exp,ystree.YFuncExp):
				reduce_value += agg_buffer+"[" + str(j) + "]"
				if reduce_value_type == "Text":
					reduce_value += " + \"|\""
				reduce_value += "+"

			elif isinstance(exp,ystree.YRawColExp): 
				reduce_value += __para_to_java__(exp.column_type,exp.column_name,line_buffer)
				if reduce_value_type == "Text":
					reduce_value += " + \"|\""
				reduce_value += "+"

			else:
				reduce_value += __para_to_java__(exp.cons_type,exp.cons_value,line_buffer)
				if reduce_value_type == "Text":
					reduce_value += " + \"|\""
				reduce_value += "+"

		reduce_value = reduce_value[:-1]


	else:
		buf_dict = {}
		for x in tree.table_list:
			buf_dict[x] = line_buffer

		reduce_value = ""

		for j in range(0,len(tree.select_list.tmp_exp_list)-having_len):
		#for j in range(i,len(tree.select_list.tmp_exp_list)):
			exp = tree.select_list.tmp_exp_list[j]
			if isinstance(exp,ystree.YFuncExp):
				reduce_value += agg_buffer+"[" + str(j) + "]"
				if reduce_value_type == "Text":
					reduce_value += " + \"|\""
				reduce_value += "+"

			elif isinstance(exp,ystree.YRawColExp): 
				reduce_value += __para_to_java__(exp.column_type,exp.column_name,line_buffer)
				if reduce_value_type == "Text":
					reduce_value += " + \"|\""
				reduce_value += "+"

			else:
				reduce_value += __para_to_java__(exp.cons_type,exp.cons_value,line_buffer)
				if reduce_value_type == "Text":
					reduce_value += " + \"|\""
				reduce_value += "+"

		reduce_value = reduce_value[:-1]

	if reduce_value == "":
		reduce_value = "\" \""

	print >>fo, "\t\t\tNullWritable key_op = NullWritable.get();"
	
#########fix me here: how to handle groupby's where condition
######## right now, the where condition is not translated.
######## here it doesn't affect the correctness of the groupby result. 

	if tree.where_condition is not None:
		buf_dict = {}
		buf_dict["AGG"] = agg_buffer
		for x in tree.table_list:
			buf_dict[x] = line_buffer

		tmp_output = "\t\t\tif("+ __where_convert_to_java__(tree.where_condition.where_condition_exp,buf_dict) + "){\n"
		tmp_output += "\t\t\t\toutput.collect(key_op"
		tmp_output += ","
		tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
		tmp_output += ");"

		tmp_output += "\t\t\t}\n"


	else:
		#tmp_output = "\t\t\toutput.collect(new "+ reduce_key_type + "("+ reduce_key + ")" 
		tmp_output = "\t\t\toutput.collect(key_op" 
		tmp_output += ","
		tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
		tmp_output += ");"

	print >>fo, tmp_output

	
	print >>fo,"\t\t}\n"   ### end of reduce func

	print >>fo,"\t}\n"

#### generating the main func
	__gen_main__(tree,fo,map_key_type,map_value_type,reduce_key_type,reduce_value_type,True)


def __get_join_key__(exp,col_list,table):
	
	if exp is None or not isinstance(exp,ystree.YFuncExp):
		return

	if len(exp.parameter_list ) ==2:
		para1 = exp.parameter_list[0]
		para2 = exp.parameter_list[1]
		tmp_bool = True
		if not isinstance(para1,ystree.YRawColExp):
			tmp_bool = False
		if not isinstance(para2,ystree.YRawColExp):
			tmp_bool = False

		if tmp_bool == True and para1.table_name != para2.table_name:
			if para1.table_name == table:
				col_list.append(para1)
			else:
				col_list.append(para2)

			return
	
	for x in exp.parameter_list:
		if isinstance(x,ystree.YFuncExp):
			__get_join_key__(x,col_list,table)


### replace the exp with NULL if its table name is not the specified one.

def __gen_func_exp__(exp,table_name):

	ret_exp = None
	
	if not isinstance(exp,ystree.YFuncExp):
		return None

	new_list = []

	for x in exp.parameter_list:
		if isinstance(x,ystree.YRawColExp):
			if x.table_name != table_name:
				tmp_exp = ystree.YConsExp("\"NULL\"","TEXT")
				new_list.append(tmp_exp)
			else:
				new_list.append(x)
		elif isinstance(x,ystree.YFuncExp):
			tmp_exp = __gen_func_exp__(x,table_name)
			if tmp_exp is None:
				print 1/0

			new_list.append(tmp_exp)
		else:
			new_list.append(x)

	ret_exp = ystree.YFuncExp(exp.func_name,new_list)
	
	return ret_exp

##generate a new list ,which contains the exps with the specified table name.

def __gen_join_list__(cur_list,new_list,table_name):

	count = 0
	
	for exp in cur_list:
		if isinstance(exp,ystree.YRawColExp):
			if exp.table_name != table_name:
				count = count +1

			else:
				new_list.append(exp)

		elif isinstance(exp,ystree.YFuncExp):
			tmp_exp = __gen_func_exp__(exp,table_name)
			new_list.append(tmp_exp)

	tmp_exp = ystree.YConsExp("\"NULL\"","TEXT")
	for x in range(0,count):
		new_list.append(tmp_exp)

def __gen_join_where__(cur_exp,table_name):

	ret_exp = None
	
	if not isinstance(cur_exp,ystree.YFuncExp):
		return None

	if cur_exp.func_name in bool_func_dict.keys():
		for x in cur_exp.parameter_list:
			if not isinstance(x,ystree.YFuncExp):
				print 1/0

			tmp_exp = __gen_join_where__(x,table_name)

			if ret_exp == None:
				ret_exp = tmp_exp
			else:
				para_list = []
				para_list.append(ret_exp)
				para_list.append(tmp_exp)
				ret_exp = ystree.YFuncExp(cur_exp.func_name,para_list)

		return ret_exp
	else:


###fix me here: how to handle the first para if the func is IS 
		if cur_exp.func_name == "IS":
			tmp_bool = True

			para1 = cur_exp.parameter_list[0]
			if isinstance(para1,ystree.YRawColExp):
				if para1.table_name != table_name:
					tmp_bool = False			

			if tmp_bool == True:
				ret_exp = copy.deepcopy(cur_exp)
			else:
				ret_exp = ystree.YConsExp("FALSE","BOOLEAN")

		else:
	
			tmp_bool = True
			para1 = cur_exp.parameter_list[0]
			para2 = cur_exp.parameter_list[1]

			if isinstance(para1,ystree.YRawColExp):
				if para1.table_name != table_name:
					tmp_bool = False

			if isinstance(para2,ystree.YRawColExp):
				if para2.table_name != table_name:
					tmp_bool = False

			if tmp_bool == True:
				ret_exp = copy.deepcopy(cur_exp)
			else:
				ret_exp = ystree.YConsExp("FALSE","BOOLEAN") 

		return  ret_exp

###### whether it is a self join

def __self_join__(tree):

	if not isinstance(tree.left_child,ystree.TableNode):
		return False

	if not isinstance(tree.right_child,ystree.TableNode):
		return False

	if len(tree.table_alias_dict.values()) !=2:
		return False

	t_name1 = tree.table_alias_dict.values()[0]

	t_name2 = tree.table_alias_dict.values()[1]

	if t_name1 != t_name2:
		return False

	else:
		return True


def __join_gen_mr__(tree,left_name,fo):

###
###	This is the map part
###

	line_buffer = "line_buf"

	if tree.select_list is None:
		print "Error when generating code for join node"
		print 1/0

	self_join_bool = False

	self_join_bool = __self_join__(tree)


### get map output key

	left_key_list = []
	right_key_list = []

	if tree.join_explicit is True:
		__get_join_key__(tree.join_condition.on_condition_exp,left_key_list,"LEFT")
		__get_join_key__(tree.join_condition.on_condition_exp,right_key_list,"RIGHT")
	elif tree.join_condition is not None:
		__get_join_key__(tree.join_condition.where_condition_exp,left_key_list,"LEFT")
		__get_join_key__(tree.join_condition.where_condition_exp,right_key_list,"RIGHT")

	if len(left_key_list)  == 0:
		new_exp = ystree.YConsExp(1,"INTEGER")
		left_key_list.append(new_exp)

	if len(right_key_list)  == 0:
		new_exp = ystree.YConsExp(1,"INTEGER")
		right_key_list.append(new_exp)

	left_key_type = __get_key_value_type__(left_key_list)
	right_key_type = __get_key_value_type__(right_key_list)


## left_key_type and right_key_type should be the same
	if left_key_type != right_key_type:
		print 1/0

	map_key_type = left_key_type 
	map_value_type = "Text"  ## we need to add tag to differentiate the data from left table and right table
	
	print >>fo,"\tpublic static class Map extends MapReduceBase implements Mapper<Object, Text,"+map_key_type+","+map_value_type+">{\n"
	print >>fo, "\t\tprivate int left = 0;"
	print >>fo, "\t\tpublic void configure(JobConf job){\n"
	print >>fo, "\t\t\tint last_index = -1, start_index = -1;"
	print >>fo, "\t\t\tString path = job.get(\"map.input.file\");"
	print >>fo, "\t\t\tlast_index = path.lastIndexOf(\'/\');"
	print >>fo,"\t\t\tlast_index = last_index - 1;"
	print >>fo, "\t\t\tstart_index = path.lastIndexOf(\'/\',last_index);"
	print >>fo, "\t\t\tString f_name = path.substring(start_index+1,last_index+1);"
	print >>fo, "\t\t\tif(f_name.compareTo(\"" + left_name + "\") == 0 )"
	print >>fo, "\t\t\t\tleft = 1;"
	print >>fo,"\t\t}" ### end of configure

	print >>fo,"\t\tpublic void map(Object key, Text value,OutputCollector<"+map_key_type+","+map_value_type+"> output, Reporter reporter) throws IOException{\n"
	
	print >>fo,"\t\t\tString line = value.toString();"
        
	print >>fo, "\t\t\tint prev=0,i=0,n=0;"

	if self_join_bool is False:
		print >>fo,"\t\t\tif(this.left == 1){\n"


	else:
		if isinstance(tree.left_child,ystree.TableNode):
			exp_list = list(tree.left_child.select_list.tmp_exp_list)
			if tree.left_child.where_condition is not None:
				exp_list.append(tree.left_child.where_condition.where_condition_exp)
			tmp1 = __get_max_index__(exp_list)
		else:
			tmp1 = len(tree.left_child.select_list.tmp_exp_list)

		if isinstance(tree.right_child,ystree.TableNode):
			exp_list = list(tree.right_child.select_list.tmp_exp_list)
			if tree.right_child.where_condition is not None:
				exp_list.append(tree.right_child.where_condition.where_condition_exp)
			tmp2 = __get_max_index__(exp_list)
		else:
			tmp2 = len(tree.right_child.select_list.tmp_exp_list)

		if tmp1>tmp2:
			max_index = tmp1
		else:
			max_index = tmp2

        	print >>fo,"\t\t\t\tString[] "+ line_buffer +" = new String["+ str(max_index)+"];"
		print >>fo, "\t\t\t\tfor(i=0,n=0,prev=0;i<line.length();i++){\n"
		print >>fo, "\t\t\t\t\tif (line.charAt(i) == \'|\'){"
		print >>fo, "\t\t\t\t\t\t" + line_buffer + "[n] = line.substring(prev,i);"
		print >>fo, "\t\t\t\t\t\tn = n+1;"
		print >>fo, "\t\t\t\t\t\tprev = i+1;"
		print >>fo, "\t\t\t\t\t}"
		print >>fo, "\t\t\t\t\tif(n == "+str(max_index)+")"
		print >>fo, "\t\t\t\t\t\tbreak;"
		print >>fo,"\t\t\t\t}\n"


	buf_dict = {}
	buf_dict["LEFT"] = line_buffer
	left_key = __gen_mr_value__(left_key_list,left_key_type,buf_dict)

	buf_dict = {}
	for x in tree.left_child.table_list:
		if x not in buf_dict.keys():
			buf_dict[x] = line_buffer

	left_value_type = map_value_type
	right_value_type = map_value_type


### scan the input of the left child
	
	if tree.left_child.select_list is not None:

		
		if isinstance(tree.left_child,ystree.TableNode):
			left_value = __gen_mr_value__(tree.left_child.select_list.tmp_exp_list,left_value_type,buf_dict)
			exp_list = list(tree.left_child.select_list.tmp_exp_list)
			if tree.left_child.where_condition is not None:
				exp_list.append(tree.left_child.where_condition.where_condition_exp)
			max_index = __get_max_index__(exp_list)
		else:
			left_value = ""
			for i in range(0,len(tree.left_child.select_list.tmp_exp_list)):
				left_value += line_buffer + "[" + str(i) + "]"
				left_value += "+ \"|\"+"
			left_value = left_value[:-1]
			max_index = len(tree.left_child.select_list.tmp_exp_list)
		
		if self_join_bool is False:
			print >>fo,"\t\t\t\tString[] "+ line_buffer +" = new String["+ str(max_index)+"];"
			print >>fo, "\t\t\t\tfor(i=0,n=0,prev=0;i<line.length();i++){\n"
			print >>fo, "\t\t\t\t\tif (line.charAt(i) == \'|\'){"
			print >>fo, "\t\t\t\t\t\t" + line_buffer + "[n] = line.substring(prev,i);"
			print >>fo, "\t\t\t\t\t\tn = n+1;"
			print >>fo, "\t\t\t\t\t\tprev = i+1;"
			print >>fo, "\t\t\t\t\t}"
			print >>fo, "\t\t\t\t\tif(n == "+str(max_index)+")"
			print >>fo, "\t\t\t\t\t\tbreak;"
			print >>fo,"\t\t\t\t}\n"

		if not isinstance(tree.left_child,ystree.TableNode) or tree.left_child.where_condition is None:
			tmp_output = "\t\t\t\toutput.collect(new " + left_key_type + "(" + left_key + ")"
			tmp_output += ", "
			tmp_output += "new " + left_value_type + "(\"L\"+\"|\" +"+ left_value +")"
			tmp_output += ");"

			print >>fo,tmp_output

		else:
			where_str = "\t\t\t\tif("
			where_str +=__where_convert_to_java__(tree.left_child.where_condition.where_condition_exp,buf_dict)
			where_str += "){\n"
			print >>fo,where_str

			tmp_output = "\t\t\t\t\toutput.collect(new " + left_key_type + "(" + left_key + ")"
			tmp_output += ", "
			tmp_output += "new " + left_value_type + "(\"L\"+\"|\"+"+ left_value +")"
			tmp_output += ");"

			print >>fo,tmp_output

			print >>fo,"\t\t\t\t}" # end of if

	if self_join_bool is False:
		print >>fo,"\t\t\t}else{\n" ##end of left child

### scan the input of the right child
	buf_dict = {}
	buf_dict["RIGHT"] = line_buffer
	right_key = __gen_mr_value__(right_key_list,right_key_type,buf_dict)

	buf_dict = {}
	for x in tree.right_child.table_list:
		if x not in buf_dict.keys():
			buf_dict[x] = line_buffer

	if tree.right_child.select_list is not None:

		if isinstance(tree.right_child,ystree.TableNode):
			right_value = __gen_mr_value__(tree.right_child.select_list.tmp_exp_list,right_value_type,buf_dict)
			exp_list = tree.right_child.select_list.tmp_exp_list
			if tree.right_child.where_condition is not None:
				exp_list.append(tree.right_child.where_condition.where_condition_exp)
			max_index = __get_max_index__(exp_list)
		else:
			right_value = ""
			for i in range(0,len(tree.right_child.select_list.tmp_exp_list)):
				right_value += line_buffer + "[" + str(i) + "]"
				right_value += "+ \"|\"+"
			right_value  = right_value[:-1]

			max_index = len(tree.right_child.select_list.tmp_exp_list)

		if self_join_bool is False:
			print >>fo,"\t\t\t\tString[] "+ line_buffer +" = new String["+ str(max_index)+"];"
			print >>fo, "\t\t\t\tfor(i=0,n=0,prev=0;i<line.length();i++){\n"
			print >>fo, "\t\t\t\t\tif (line.charAt(i) == \'|\'){"
			print >>fo, "\t\t\t\t\t\t" + line_buffer + "[n] = line.substring(prev,i);"
			print >>fo, "\t\t\t\t\t\tn = n+1;"
			print >>fo, "\t\t\t\t\t\tprev = i+1;"
			print >>fo, "\t\t\t\t\t}"
			print >>fo, "\t\t\t\t\tif(n == "+str(max_index)+")"
			print >>fo, "\t\t\t\t\t\tbreak;"
			print >>fo,"\t\t\t\t}\n"
			
		if not isinstance(tree.right_child,ystree.TableNode) or tree.right_child.where_condition is  None:
			tmp_output = "\t\t\t\toutput.collect(new " + right_key_type + "(" + right_key + ")"
			tmp_output += ", "
			tmp_output += "new " + right_value_type + "(\"R\"+\"|\" +"+ right_value +")"
			tmp_output += ");"

			print >>fo, tmp_output
			
		else:
			where_str = "\t\t\t\tif("
			where_str +=__where_convert_to_java__(tree.right_child.where_condition.where_condition_exp,buf_dict)
			where_str += "){\n"
			print >>fo,where_str

			tmp_output = "\t\t\t\t\toutput.collect(new " + right_key_type + "(" + right_key + ")"
			tmp_output += ", "
			tmp_output += "new " + right_value_type + "(\"R\"+\"|\" +"+ right_value +")"
			tmp_output += ");"

			print >>fo, tmp_output

			print >>fo,"\t\t\t\t}" # end of if

	if self_join_bool is False:
		print >>fo,"\t\t\t}\n"

	print >>fo,"\t\t}\n" ### end of map func

	print >>fo,"\t}\n"  ## end of map class

###
### This is the reduce part
###

	left_array = "al_left"
	right_array = "al_right"

	#reduce_key_type = __get_key_value_type__(tree.select_list.tmp_exp_list[:1])
	#reduce_value_type = __get_key_value_type__(tree.select_list.tmp_exp_list[1:])
	reduce_key_type = "NullWritable"
	reduce_value_type = "Text"

	print >>fo,"\tpublic static class Reduce extends MapReduceBase implements Reducer<"+ map_key_type+","+map_value_type+","+reduce_key_type+","+reduce_value_type+">{\n"
	print >>fo, "\t\tpublic void reduce("+map_key_type+" key, Iterator<"+map_value_type+"> values, OutputCollector<"+reduce_key_type+","+reduce_value_type+"> output, Reporter reporter) throws IOException{\n"

	print >>fo,"\t\t\tArrayList "+ left_array +" = new ArrayList();"
	print >>fo,"\t\t\tArrayList "+ right_array +" = new ArrayList();"

	print >>fo,"\t\t\twhile(values.hasNext()){\n"
	print >>fo,"\t\t\t\tString tmp = values.next().toString();"
	print >>fo,"\t\t\t\tif(tmp.charAt(0) == \'L\'){\n"
	
	print >>fo,"\t\t\t\t\t"+ left_array + ".add(tmp.substring(2));"
	
	print >>fo,"\t\t\t\t}else{\n"

	print >>fo,"\t\t\t\t\t" + right_array +".add(tmp.substring(2));"

	print >>fo,"\t\t\t\t}\n"
	print >>fo,"\t\t\t}\n" ### end of while


	print >>fo,"\t\t\tNullWritable key_op = NullWritable.get();"

	buf_dict = {}
	left_line_buffer = "left_buf"
	right_line_buffer = "right_buf"


	buf_dict["LEFT"] = "left_buf"
	buf_dict["RIGHT"] = "right_buf"

	if tree.join_explicit is True:
		join_type = tree.join_type.upper()

		if join_type == "LEFT":
			reduce_value = __gen_mr_value__(tree.select_list.tmp_exp_list,reduce_value_type,buf_dict)
			print >>fo,"\t\t\tfor(int i=0;i<" + left_array + ".size();i++){\n"
			print >>fo,"\t\t\t\tString[] " + left_line_buffer + " = ((String)" + left_array + ".get(i)).split(\"\\\|\");"

			print >>fo, "\t\t\t\tif(" + right_array + ".size()>0){\n"

			print >>fo,"\t\t\t\t\tfor(int j=0;j<" +right_array + ".size();j++){\n"
			print >>fo,"\t\t\t\t\t\tString[] " + right_line_buffer + " = ((String)" + right_array + ".get(j)).split(\"\\\|\");"
			if tree.where_condition is not None:
				exp = tree.where_condition.where_condition_exp
				
				print >>fo,"\t\t\t\t\t\tif(" + __where_convert_to_java__(exp,buf_dict) + "){\n" 


				tmp_output = "output.collect("

				#tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
				tmp_output += "key_op"
				tmp_output += ", "
				tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
				tmp_output += ");"

				print >>fo, "\t\t\t\t\t\t\t",tmp_output

				print >>fo,"\t\t\t\t\t\t}\n"  #### end of where condtion

			else:
				if tree.select_list is None:
					print 1/0

				tmp_output = "output.collect("

				#tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
				tmp_output += "key_op"
				tmp_output += ", "
				tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
				tmp_output += ");"

				print >>fo, "\t\t\t\t\t\t",tmp_output

			print >>fo, "\t\t\t\t\t}\n"

			print >>fo, "\t\t\t\t}else{\n"

##### generate new select_list and where_condition.
			new_list = []

			__gen_join_list__(tree.select_list.tmp_exp_list,new_list,"LEFT")

			reduce_value = __gen_mr_value__(new_list,reduce_value_type,buf_dict)

			if tree.where_condition is not None:
				new_where = None
				new_where = __gen_join_where__(tree.where_condition.where_condition_exp,"LEFT")
				
				if new_where is None:
					print 1/0

				print >>fo,"\t\t\t\t\tif(" + __where_convert_to_java__(new_where,buf_dict) + "){\n" 

				tmp_output = "output.collect("

				#tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
				tmp_output += "key_op"
				tmp_output += ", "
				tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
				tmp_output += ");"

				print >>fo,"\t\t\t\t\t\t",tmp_output

				print >>fo, "\t\t\t\t\t}"

				
			else:
				tmp_output = "output.collect("
				tmp_output += "key_op"
				tmp_output += ","
				tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
				tmp_output += ");"

				print >>fo,"\t\t\t\t\t",tmp_output

			print >>fo, "\t\t\t\t}\n" ### end of else

			print >>fo, "\t\t\t}\n" ## end of for

		elif join_type == "RIGHT":

			print >>fo,"\t\t\tfor(int j=0;j<" +right_array + ".size();j++){\n"

			print >>fo, "\t\t\t}\n" ## end of for

		else:
			pass

	else:
		print >>fo,"\t\t\tfor(int i=0;i<" + left_array + ".size();i++){\n"
		print >>fo,"\t\t\t\tString[] " + left_line_buffer + " = ((String)" + left_array + ".get(i)).split(\"\\\|\");"
		
		print >>fo,"\t\t\t\tfor(int j=0;j<" +right_array + ".size();j++){\n"

		print >>fo,"\t\t\t\t\tString[] " + right_line_buffer + " = ((String)" + right_array + ".get(j)).split(\"\\\|\");"

		reduce_key = __gen_mr_value__(tree.select_list.tmp_exp_list[:1],reduce_key_type,buf_dict)
		reduce_value = __gen_mr_value__(tree.select_list.tmp_exp_list,reduce_value_type,buf_dict)

		if tree.where_condition is not None:
			exp = tree.where_condition.where_condition_exp
			
			print >>fo,"\t\t\t\t\tif(" + __where_convert_to_java__(exp,buf_dict) + "){\n" 


			tmp_output = "output.collect("

			#tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
			tmp_output += "key_op"
			tmp_output += ", "
			tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
			tmp_output += ");"

			print >>fo, "\t\t\t\t\t\t",tmp_output

			print >>fo,"\t\t\t\t\t}"


		else:
			if tree.select_list is None:
				print 1/0

			tmp_output = "output.collect("

			#tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
			tmp_output += "key_op"
			tmp_output += ", "
			tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
			tmp_output += ");"

			print >>fo, "\t\t\t\t\t",tmp_output
			

		print >>fo,"\t\t\t\t}\n"

		print >>fo,"\t\t\t}\n"


	print >>fo,"\t\t}\n" #### end of  reduce func

	print >>fo,"\t}\n" ##### end of reduce class

	__gen_main__(tree,fo,map_key_type,map_value_type,reduce_key_type,reduce_value_type,True)
	

def __gen_main__(tree,fo,map_key_type,map_value_type,reduce_key_type,reduce_value_type,reduce_bool):
	print >>fo,"\tpublic static void main(String[] args) throws Exception{\n"
	jobname = fo.name.split(".java")[0]
	io_path = ""

	print >>fo,"\t\tJobConf conf = new JobConf("+jobname+".class);"
	print >>fo,"\t\tconf.setJobName(\""+jobname+"\");"
	print >>fo,"\t\tconf.setMapOutputKeyClass(" + map_key_type+".class);"
	print >>fo,"\t\tconf.setMapOutputValueClass(" + map_value_type+ ".class);"
	print >>fo,"\t\tconf.setOutputKeyClass("+reduce_key_type+".class);"
	print >>fo,"\t\tconf.setOutputValueClass("+reduce_value_type+".class);"
	print >>fo,"\t\tconf.setMapperClass(Map.class);"
	if reduce_bool is True:
		print >>fo,"\t\tconf.setReducerClass(Reduce.class);"
	if isinstance(tree,ystree.TwoJoinNode):
		print>>fo, "\t\tFileInputFormat.addInputPath(conf,new Path(args[0]));"
		print>>fo, "\t\tFileInputFormat.addInputPath(conf,new Path(args[1]));"
		io_path = "args[2]"
	else:
		io_path = "args[1]"
		print >>fo,"\t\tFileInputFormat.addInputPath(conf, new Path(args[0]));"
	print >>fo,"\t\tFileOutputFormat.setOutputPath(conf, new Path("+io_path+"));"
	print >>fo, "\t\tJobClient.runJob(conf);"

	print >>fo,"\t}\n"

def __tablenode_code_gen__(tree,fo):
	__gen_des__(fo)
	__gen_header__(fo)

	print >>fo,"public class "+fo.name.split(".java")[0]+"{\n"

	__tablenode_gen_mr__(tree,fo)

	print >>fo,"}\n"

def __orderby_code_gen__(tree,fo):
	__gen_des__(fo)
	__gen_header__(fo)

	print >>fo,"public class " +fo.name.split(".java")[0] + "{\n"

	__orderby_gen_mr__(tree,fo)

	print >>fo,"}\n"


def __groupby_code_gen__(tree,fo):
	__gen_des__(fo)
	__gen_header__(fo)

	print >>fo,"public class "+fo.name.split(".java")[0]+"{\n"

	__groupby_gen_mr__(tree,fo)

	print >>fo, "}\n"


def __join_code_gen__(tree,left_name,fo):
	__gen_des__(fo)
	__gen_header__(fo)
	print >>fo,"public class "+fo.name.split(".java")[0]+"{\n"

	__join_gen_mr__(tree,left_name,fo)
	print >>fo, "}\n"


def generate_code(tree,filename):

	op_name = filename + ".java"

	fo = open(op_name,"w")
	

	if isinstance(tree,ystree.TableNode):
		__tablenode_code_gen__(tree,fo)

	elif isinstance(tree,ystree.OrderByNode):
		__orderby_code_gen__(tree,fo)
		if not isinstance(tree.child,ystree.TableNode):
			filename = filename[:-1] + str(int(filename[-1])+1)
			generate_code(tree.child,filename)

	elif isinstance(tree,ystree.SelectProjectNode):
		generate_code(tree.child,filename)

	elif isinstance(tree,ystree.GroupByNode):
		__groupby_code_gen__(tree,fo)
		if not isinstance(tree.child,ystree.TableNode):
			filename = filename[:-1] + str(int(filename[-1])+1) 
			generate_code(tree.child,filename)

	elif isinstance(tree,ystree.TwoJoinNode):

		if not isinstance(tree.left_child,ystree.TableNode):
			new_name = filename[:-1] + "LEFT" +str(int(filename[-1])+1)
			__join_code_gen__(tree,new_name,fo)
			generate_code(tree.left_child,new_name)

		else:
			__join_code_gen__(tree,tree.left_child.table_name,fo)

		if not isinstance(tree.right_child,ystree.TableNode):
			new_name = filename[:-1] + "RIGHT" + str(int(filename[-1])+1)
			generate_code(tree.right_child,new_name)

	fo.close()

def compile_class(tree,codedir,package_path,filename):

	cmd = "javac -classpath $HADOOP_HOME//hadoop-common-0.21.0.jar:$HADOOP_HOME/hadoop-hdfs-0.21.0.jar:$HADOOP_HOME/hadoop-mapred-0.21.0.jar " 
	cmd += codedir + "/" + filename + ".java -d ." 
	os.system(cmd)


	if isinstance(tree,ystree.TableNode):
		return
	
	elif isinstance(tree,ystree.OrderByNode):
		if not isinstance(tree.child,ystree.TableNode):
			filename = filename[:-1] + str(int(filename[-1])+1) 
			compile_class(tree.child,codedir,package_path,filename)

	elif isinstance(tree,ystree.SelectProjectNode):
		compile_class(tree.child,codedir,package_path,filename)

	elif isinstance(tree,ystree.GroupByNode):
		if not isinstance(tree.child,ystree.TableNode):
			filename = filename[:-1] + str(int(filename[-1])+1) 
			compile_class(tree.child,codedir,package_path,filename)

	elif isinstance(tree,ystree.TwoJoinNode):
		if not isinstance(tree.left_child,ystree.TableNode):
			new_name = filename[:-1] + "LEFT" +str(int(filename[-1])+1)
			compile_class(tree.left_child,codedir,package_path,new_name)

		if not isinstance(tree.right_child,ystree.TableNode):
			new_name = filename[:-1] + "RIGHT" + str(int(filename[-1])+1)
			compile_class(tree.right_child,codedir,package_path,new_name)

def generate_jar(jardir,path,filename):
	cmd = "jar -cf " +jardir + "/"+ filename + ".jar " + path
	os.system(cmd)
	


def execute_jar(tree,jardir,jarname,classname,input_path,output_path):
	
	if isinstance(tree,ystree.TableNode):
		cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath + classname + " "  + input_path + "/" + tree.table_name + "/" 
		cmd += " " + output_path + "/" + tree.table_name + "/" 
		print cmd
		os.system(cmd)

	elif isinstance(tree,ystree.OrderByNode):
		if not isinstance(tree.child,ystree.TableNode):
			new_name = classname[:-1] + str(int(classname[-1])+1)
			execute_jar(tree.child,jardir,jarname,new_name,input_path,output_path)
			cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + output_path + "/" + new_name
			cmd += " " + output_path + "/" + classname + "/"
		else:
			cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + input_path + "/" + tree.child.table_name + "/"
			cmd += " " + output_path + "/" + classname + "/"
		print cmd
		os.system(cmd)

	elif isinstance(tree,ystree.SelectProjectNode):
		execute_jar(tree.child,jardir,jarname,classname,input_path,output_path)

	elif isinstance(tree,ystree.GroupByNode):
		if not isinstance(tree.child,ystree.TableNode):
			new_name = classname[:-1] + str(int(classname[-1])+1)
			execute_jar(tree.child,jardir,jarname,new_name,input_path,output_path)
			cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath + classname + " " + output_path + "/" + new_name
			cmd += " " + output_path + "/" + classname + "/"
		else:
			cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath + classname + " " + input_path + "/" + tree.child.table_name + "/" 
			cmd += " " + output_path + "/" + classname + "/"
		print cmd
		os.system(cmd)

	elif isinstance(tree,ystree.TwoJoinNode):
		cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + input_path + "/"
		if not isinstance(tree.left_child,ystree.TableNode):
			new_name = classname[:-1] + "LEFT" +str(int(classname[-1])+1)
			execute_jar(tree.left_child,jardir,jarname,new_name,input_path,output_path)
			cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + output_path + "/"
			cmd += new_name + "/"
		else:
			cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + input_path + "/"
			cmd += tree.left_child.table_name + "/"

		if not isinstance(tree.right_child,ystree.TableNode):
			new_name = classname[:-1] + "RIGHT" + str(int(classname[-1])+1)
			execute_jar(tree.right_child,jardir,jarname,new_name,input_path,output_path)
			cmd += " " + output_path + "/"
			cmd += new_name + "/"
		else:
			cmd += " " + input_path + "/"
			cmd += tree.right_child.table_name + "/"

		cmd += " " + output_path + "/" + classname + "/"
		print cmd
		os.system(cmd)


if __name__ == '__main__':

	pwd = os.getcwd()
	codedir = "./YSmartCode"
	jardir = "./YSmartJar"

        if len(sys.argv) !=4:
                print "Usage: " +sys.argv[0] + " schema xml " + "output_file"
                exit(-1)

	packagepath += sys.argv[3] + "/"
	packagename += "." + sys.argv[3]
	
	tree_node = ystree.ysmart_tree_gen(sys.argv[1],sys.argv[2])
	
	if tree_node is None:
		exit(-1)

	if os.path.exists(codedir) or os.path.exists(jardir):
		print "please remove dir " +codedir + " and " + jardir + " in the current diretory."
		exit(-1)

	os.makedirs(codedir)
	os.makedirs(jardir)
	os.makedirs(packagepath)
	filename = sys.argv[3] + "1"

	os.chdir(codedir)	
	
	generate_code(tree_node,filename)

	os.chdir(pwd)

	compile_class(tree_node,codedir,packagepath,filename)

	generate_jar(jardir,packagepath,filename)

	execute_jar(tree_node,jardir,filename,filename,"/user/yuanyuan/input/","/user/yuanyuan/output/")



