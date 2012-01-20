#! /usr/bin/python
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


import sys
import commands
import os.path
import copy
import ystree
import correlation
import config

##input exp should be YFuncExp

math_func_dict = {"PLUS":" + ","MINUS":" - ","DIVIDE":" / ","MULTIPLY":" * "}

agg_func_list = ["SUM","AVG","COUNT","MAX","MIN","COUNT_DISTINCT"]

bool_func_dict = {"AND":" && ","OR":" || "}

rel_func_dict = {"EQ":" == ","GTH":" > ", "LTH":" < ","NOT_EQ":" != ","GEQ":" >= ","LEQ":" <= "}

packagepath = "edu/osu/cse/ysmart/"
packagename = "edu.osu.cse.ysmart"


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
            print >>sys.stderr,"Internal Error:__select_func_convert_to_java__ "
            exit(29)

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
        print >>sys.stderr,"Internal Error:__select_func_convert_to_java__"
        exit(29)
        
    return return_str

##### the difference between __gb_exp_to_java__ and __select_func_convert_to_java__ is how they handle the agg exp

def __gb_exp_to_java__(exp,gb_exp_list,buf_dict,hash_key):
    return_str = ""
    if not isinstance(exp,ystree.YFuncExp):
        print >>sys.stderr,"Internal Error:__gb_exp_to_java__"
        exit(29)

    if exp.func_name in agg_func_list:
        for x in gb_exp_list:
            if x.compare(exp) is True:
                return_str += "("
                if hash_key is None:
                    return_str += buf_dict["AGG"] +"[" + str(gb_exp_list.index(x)) + "]"
                else:
                    return_str += buf_dict["AGG"] + "[" + str(gb_exp_list.index(x)) + "].get("+hash_key+")"
                return_str += ")"
                break

    elif exp.func_name in math_func_dict.keys():
        para1 = exp.parameter_list[0]
        para2 = exp.parameter_list[1]
        
        if isinstance(para1,ystree.YRawColExp):
            return_str += "("
            return_str += __para_to_java__(para1.column_type,para1.column_name,buf_dict[para1.table_name])

        elif isinstance(para1,ystree.YFuncExp):
            return_str += "("
            return_str += __gb_exp_to_java__(para1,gb_exp_list,buf_dict,hash_key)

        else:
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
            return_str += __gb_exp_to_java__(para2,gb_exp_list,buf_dict,hash_key)
            return_str += ")"

        else:
            return_str += para2.cons_value
            return_str += ")"

    else:
        print >>sys.stderr,"Internal Error:__gb_exp_to_java__"
        exit(29)

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
            print >>sys.stderr,"Internal Error:__para_to_java__"
            exit(29)

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
            print >>sys.stderr,"Internal Error:__para_to_java__"
            exit(29)
        

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
            print >>sys.stderr,"Internal Error:__operator_to_java__"
            exit(29)

        elif op_type == "DATE":
            print >>sys.stderr,"Internal Error:__operator_to_java__"
            exit(29)

    elif op_name in bool_func_dict.keys():
        count = 0
        for tmp in op_list:
            count = count +1
            if count != len(op_list):
                res_str = res_str + tmp + bool_func_dict[op_name]
            else:
                res_str = res_str + tmp
    else:
        print >>sys.stderr,"Internal Error:__operator_to_java__"
        exit(29)

    return res_str



#### translate the where exp to java. 

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
                print >>sys.stderr,"Internal Error:__where_convert_to_java__"
                exit(29)

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
                    print >>sys.stderr,"Internal Error:__where_convert_to_java__"
                    exit(29)

                return_str +=  ".compareTo(\""

                if isinstance(para2,ystree.YConsExp):
                    return_str += str(para2.cons_value)
                    return_str += "\") == 0"
                else:
                    print >>sys.stderr,"Internal Error:__where_convert_to_java__"
                    exit(29)

                return_str += ")"
                

    elif isinstance(exp, ystree.YConsExp):
        if exp.cons_type == "BOOLEAN":
            if exp.cons_value == "FALSE":
                return "false"
            else:
                return "true"


    return return_str

sql_type_to_java = {"INTEGER":"IntWritable","DECIMAL":"DoubleWritable","TEXT":"Text","DATE":"Text"}
java_type_to_hash = {"IntWritable":"Integer","DoubleWritable":"Double","Text":"String","Date":"String"}

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
        The following code is automatically generated by YSmart 12.01.\n\
        Author: Rubao Lee, Yuan Yuan    \n\
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
    print >>fo,"import org.apache.hadoop.util.Tool;"
    print >>fo,"import org.apache.hadoop.util.ToolRunner;"
    print >>fo, "import org.apache.hadoop.mapreduce.Job;"
    print >>fo, "import org.apache.hadoop.mapreduce.Mapper;"
    print >>fo, "import org.apache.hadoop.mapreduce.Reducer;"
    print >>fo, "import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;"
    print >>fo, "import org.apache.hadoop.mapreduce.lib.input.FileSplit;"
    print >>fo, "import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;"
    print >>fo, "import org.apache.hadoop.mapreduce.lib.partition.*;"
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

def __get_gb_exp__(exp,tmp_list):
    if not isinstance(exp,ystree.YFuncExp):
        return

    if exp.func_name in agg_func_list:
        tmp_list.append(exp)
    else:
        for x in exp.parameter_list:
            __get_gb_exp__(x,tmp_list)

def __get_gbexp_list__(exp_list,gb_exp_list):
    for exp in exp_list:
        if not isinstance(exp,ystree.YFuncExp):
            continue
        tmp_list = []
        __get_gb_exp__(exp,tmp_list)
        for tmp in tmp_list:
            tmp_bool = False
            for gb_exp in gb_exp_list:
                if tmp.compare(gb_exp) is True:
                    tmp_bool = True
                    break
            if tmp_bool is False:
                gb_exp_list.append(tmp)



def __tablenode_gen_mr__(tree,fo):

    line_buffer = "line_buf"
    if tree.select_list is None:
        print >>sys.stderr,"Internal Error:__tablenode_gen_mr__"
        exit(29)

    buf_dict = {}

    buf_dict[tree.table_name] = line_buffer
    buf_dict[tree.table_alias] = line_buffer
    
    map_key_type = "NullWritable"
    map_value_type = __get_key_value_type__(tree.select_list.tmp_exp_list)  
    map_value = __gen_mr_value__(tree.select_list.tmp_exp_list,map_value_type,buf_dict)

    max_index = __get_max_index__(tree.select_list.tmp_exp_list) 


    print >>fo,"\tpublic static class Map extends Mapper<Object, Text,"+map_key_type+","+map_value_type+">{\n"

    print >>fo,"\t\tpublic void map(Object key, Text value, Context context) throws IOException,InterruptedException{\n"
    
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
    print >>fo,"\t\t\tif(n<" + str(max_index) + ")"
    print >>fo,"\t\t\t\t"+line_buffer+ "[n] = line.substring(prev,i);"

    if tree.where_condition is None:
        print >>fo,"\t\t\tNullWritable key_op = NullWritable.get();"
        tmp_output =  "\t\t\tcontext.write(" 
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
        tmp_output =  "\t\t\t\tcontext.write(" 
        #tmp_output += "new " + map_key_type + "(" + map_key + ")" 
        tmp_output += "key_op"
        tmp_output += " , "
        tmp_output += "new " + map_value_type + "(" + map_value + ")" 
        tmp_output += ");"

        print >>fo, tmp_output
        
        print >>fo,"\t\t\t}" # end of if
        

    print >>fo,"\t\t}\n"

    print >>fo,"\t}\n"

    __gen_main__(tree,fo,map_key_type,map_value_type,map_key_type,map_value_type,False)

def __orderby_gen_mr__(tree,fo):

    line_buffer = "line_buf"

    buf_dict = {}
    for x in tree.table_list:
        buf_dict[x] = line_buffer
    
    od_len = len(tree.order_by_clause.orderby_exp_list)

    if isinstance(tree.child,ystree.TableNode):
        map_key_type = __get_key_value_type__(tree.order_by_clause.orderby_exp_list)
        map_value_type = __get_key_value_type__(tree.child.select_list.tmp_exp_list)
        map_value = __gen_mr_value__(tree.child.select_list.tmp_exp_list,map_value_type,buf_dict)
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


    print >>fo,"\tpublic static class Map extends  Mapper<Object, Text,"+map_key_type+","+map_value_type+">{\n"

    print >>fo,"\t\tpublic void map(Object key, Text value, Context context) throws IOException,InterruptedException{\n"
    
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
    print >>fo,"\t\t\tif(n<" + str(max_index) + ")"
    print >>fo,"\t\t\t\t"+line_buffer+ "[n] = line.substring(prev,i);"

    if not isinstance(tree.child,ystree.TableNode) or tree.child.where_condition is None:
            tmp_output = "\t\t\tcontext.write("
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

            tmp_output =  "\t\t\t\tcontext.write( "
            tmp_output += "new " + map_key_type + "(" + map_key +")"
            tmp_output += ","
            tmp_output += "new " + map_value_type + "(" + map_value + ")"
            tmp_output += ");"

            print >>fo, tmp_output

            print >>fo,"\t\t\t}" # end of if

    print >>fo,"\t\t}\n"
    print >>fo,"\t}\n"


###### orderby reduce part

    reduce_key_type = "NullWritable"
    reduce_value_type = "Text"

    print >>fo,"\tpublic static class Reduce extends  Reducer<"+ map_key_type+","+map_value_type+","+reduce_key_type+","+reduce_value_type+">{\n"

    print >>fo,"\t\tpublic void reduce("+map_key_type+" key, Iterable<"+map_value_type+"> v, Context context) throws IOException,InterruptedException{\n"

    print >>fo, "\t\t\tIterator values = v.iterator();"

    print >>fo, "\t\t\tNullWritable key_op = NullWritable.get();"

    print >>fo,"\t\t\twhile(values.hasNext()){\n"
    
    print >>fo, "\t\t\t\tString tmp = values.next().toString();"

    print >>fo, "\t\t\t\tcontext.write(key_op,new Text(tmp));" 

    print >>fo, "\t\t\t}\n"

    print >>fo,"\t\t}\n"

    print >>fo,"\t}\n"

#### orderby  main  

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

    print >>fo,"\tpublic int run(String[] args) throws Exception{\n"
    job_name = fo.name.split(".java")[0]
    print >>fo, "\t\tConfiguration conf = new Configuration();"
    print >>fo, "\t\tconf.set(\"mapreduce.partition.keycomparator.options\",\"" + key_spec + "\");"
    print >>fo, "\t\tconf.set(\"mapreduce.map.output.key.field.separator\", \"|\");"
    print >>fo, "\t\tJob job = new Job(conf, \"" + job_name + "\");"
    print >>fo, "\t\tjob.setJarByClass(" + job_name  + ".class" + ");"
    print >>fo, "\t\tjob.setSortComparatorClass(KeyFieldBasedComparator.class);"
    print >>fo, "\t\tjob.setPartitionerClass(KeyFieldBasedPartitioner.class);"
    print >>fo,"\t\tjob.setMapOutputKeyClass(" + map_key_type+".class);"
    print >>fo,"\t\tjob.setMapOutputValueClass(" + map_value_type+ ".class);"
    print >>fo,"\t\tjob.setOutputKeyClass("+reduce_key_type+".class);"
    print >>fo,"\t\tjob.setOutputValueClass("+reduce_value_type+".class);"
    print >>fo,"\t\tjob.setMapperClass(Map.class);"
    print >>fo,"\t\tjob.setReducerClass(Reduce.class);"
    print >>fo, "\t\tjob.setNumReduceTasks(1);"
    print >>fo,"\t\tFileInputFormat.addInputPath(job, new Path(args[0]));"
    print >>fo,"\t\tFileOutputFormat.setOutputPath(job, new Path(args[1]));"
    print >>fo, "\t\treturn (job.waitForCompletion(true) ? 0 : 1);"

    print >>fo,"\t}\n"

    print >>fo, "\tpublic static void main(String[] args) throws Exception {\n "
    print >>fo, "\t\tint res = ToolRunner.run(new Configuration(), new "+job_name + "(),args);"
    print >>fo,"\t\tSystem.exit(res);"
    print >>fo,"\t}\n"


def __groupby_gen_mr__(tree,fo):

##### groupby map part 
    line_buffer = "line_buf"
    
    if tree.select_list is None or tree.child.select_list is None:
        print >>sys.stderr,"Internal Error:__groupby_gen_mr__"
        exit(29)

    buf_dict = {}
    for x in tree.child.table_list:
        buf_dict[x] = line_buffer

    if tree.group_by_clause is None:
        print >>sys.stderr,"Internal Error:__groupby_gen_mr__"
        exit(29)
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

    gb_exp_list = []
    __get_gbexp_list__(tree.select_list.tmp_exp_list,gb_exp_list)
    for exp in gb_exp_list:
        if ystree.__groupby_func_name__(exp) == "COUNT_DISTINCT":
            config.advanced_agg = False
            break

    if config.advanced_agg is True:
        for exp in gb_exp_list:
            if ystree.__groupby_func_name__(exp) == "AVG":
                map_value_type = "Text"

    print >>fo,"\tpublic static class Map extends Mapper<Object, Text,"+ map_key_type+","+map_value_type+">{\n"

    adv_gb_output = "adv_gb_output"
    adv_count_output = "adv_count_output"
    adv_dc_output = "adv_dc_output"

    hash_type = java_type_to_hash[map_key_type]

    if config.advanced_agg is True:
        print >>fo,"\t\tHashtable<"+hash_type+",Double>[] "+adv_gb_output+"=new Hashtable[" + str(len(gb_exp_list)) + "];"
        print >>fo,"\t\tHashtable<"+hash_type+",Integer> "+adv_count_output+"=new Hashtable<"+hash_type+",Integer>();"
        print >>fo,"\t\tpublic void setup(Context context) throws IOException, InterruptedException {\n"
        print >>fo,"\t\t\tfor(int i =0;i<"+str(len(gb_exp_list)) + ";i++){"
        print >>fo,"\t\t\t\t" + adv_gb_output + "[i] = new Hashtable<"+hash_type+",Double>();"
        print >>fo,"\t\t\t}"
        print >>fo,"\t\t}\n"
        
        print >>fo,"\t\tpublic void cleanup(Context context) throws IOException, InterruptedException {\n"
        print >>fo,"\t\t\tfor("+hash_type+" tmp_key:"+adv_count_output+".keySet()){"
        print >>fo,"\t\t\t\tDouble count = (double) "+adv_count_output+".get(tmp_key);"
        map_value = ""
        for i in range(0,len(gb_exp_list)):
            exp = gb_exp_list[i]
            func_name = ystree.__groupby_func_name__(exp)
            if func_name == "AVG":
                print >>fo,"\t\t\t\tDouble avg_"+str(i)+" = "+adv_gb_output+"["+str(i) + "].get(tmp_key);"
                map_value += "avg_"+str(i)+" + \"&\"+count+\"|\"+"

            elif func_name == "COUNT":
                print >>fo,"\t\t\t\t"+adv_gb_output +"["+str(i)+"].put(tmp_key.toString(),count);"
                if map_value_type == "Text":
                    map_value += "count + \"&\"+\"|\"+"
                else:
                    map_value += "count"

            else:
                print >>fo,"\t\t\t\tDouble tmp_"+str(i)+" = "+adv_gb_output+"["+str(i)+"].get(tmp_key);"
                if map_value_type == "Text":
                    map_value += "tmp_"+str(i)+" + \"&\"+\"|\"+"
                else:
                    map_value += "tmp_" + str(i)

        if map_key_type == "Text":
            if map_value_type == "Text":
                map_value = map_value[:-1]
            print >>fo,"\t\t\t\tcontext.write(new Text(tmp_key.toString()),new "+map_value_type+"("+map_value+"));"
        else:
            if map_value_type == "Text":
                map_value = map_value[:-1]
            print >>fo,"\t\t\t\tcontext.write(new "+map_key_type+"(tmp_key),new "+map_value_type+"("+map_value+"));"

        print >>fo,"\t\t\t}"
        print >>fo,"\t\t}"

    print >>fo,"\t\tpublic void map(Object key, Text value, Context context) throws IOException,InterruptedException{\n"
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
    print >>fo,"\t\t\tif(n<" + str(max_index) + ")"
    print >>fo,"\t\t\t\t"+line_buffer+ "[n] = line.substring(prev,i);"


    if config.advanced_agg is True:
### map part agg
        hash_key = ""
        buf_dict = {}
        for x in tree.child.table_list:
            buf_dict[x] = line_buffer
        if isinstance(tree.child,ystree.TableNode):
            hash_key = __gen_mr_key__(tree.child.select_list.tmp_exp_list[:gb_len],map_key_type,buf_dict)
        else:
            for i in range(0,gb_len):
                hash_key += line_buffer + "[" + str(i) + "]+"
                hash_key += "\"|\"+"
            hash_key = hash_key[:-1]

        print >>fo,"\t\t\t"+hash_type+" hash_key = "+hash_key + ";"

        if isinstance(tree.child,ystree.TableNode) and tree.child.where_condition is not None:
            where_str = "\t\t\tif("
            where_str +=__where_convert_to_java__(tree.child.where_condition.where_condition_exp,buf_dict)
            where_str += "){\n"
            print >>fo,where_str

        buf_dict = {}
        for tn in tree.table_list:
            buf_dict[tn] = line_buffer

        print >>fo,"\t\t\tif(" + adv_count_output +".containsKey(hash_key)){"
        print >>fo,"\t\t\t\tInteger count = "+adv_count_output+".get(hash_key)+1;"
        print >>fo,"\t\t\t\t"+adv_count_output+".put(hash_key,count);"
        print >>fo,"\t\t\t}else{"
        print >>fo,"\t\t\t\t"+adv_count_output+".put(hash_key,1);"
        print >>fo,"\t\t\t}"
        for i in range(0,len(gb_exp_list)):
            exp = gb_exp_list[i]
            func_name = ystree.__groupby_func_name__(exp)
            tmp = ""
            if isinstance(tree.child,ystree.TableNode):
                tmp_exp = copy.deepcopy(exp)
                col_list = []
                ystree.__get_func_para__(tmp_exp,col_list)
                for x in col_list:
                    x.column_name = tree.child.select_list.tmp_exp_list[x.column_name].column_name

                tmp = __select_func_convert_to_java__(tmp_exp,buf_dict)
            else:
                tmp = __select_func_convert_to_java__(exp,buf_dict)

            if func_name == "MAX":
                print >>fo,"\t\t\tif(" + adv_gb_output + "["+str(i)+"].containsKey(hash_key)){"
                print >>fo,"\t\t\t\tDouble max_tmp = (double)" + tmp  + ";"
                print >>fo,"\t\t\t\tif(max_tmp > "+adv_gb_output+"["+str(i)+"].get(hash_key))"
                print >>fo,"\t\t\t\t\t"+adv_gb_output+"["+str(i)+"].put(hash_key,max_tmp);"
                print >>fo,"\t\t\t}else{"
                print >>fo,"\t\t\t\t" + adv_gb_output+"["+str(i)+"].put(hash_key,(double)" + tmp + ");"
                print >>fo,"\t\t\t}"
            elif func_name == "MIN":
                print >>fo,"\t\t\tif(" + adv_gb_output + "["+str(i)+"].containsKey(hash_key)){"
                print >>fo,"\t\t\t\tDouble min_tmp = (double)"+tmp +";"
                print >>fo,"\t\t\t\tif(min_tmp < "+adv_gb_output+"["+str(i)+"].get(hash_key))"
                print >>fo,"\t\t\t\t\t"+adv_gb_output+"["+str(i)+"].put(hash_key,min_tmp);"
                print >>fo,"\t\t\t}else{"
                print >>fo,"\t\t\t\t" + adv_gb_output+"["+str(i)+"].put(hash_key,(double)"+tmp + ");"
                print >>fo,"\t\t\t}"
            elif func_name == "SUM" or func_name == "AVG":
                print >>fo,"\t\t\tif(" + adv_gb_output + "["+str(i)+"].containsKey(hash_key)){"
                print >>fo,"\t\t\t\tDouble sum_tmp = (double)"+tmp+";"
                print >>fo,"\t\t\t\tsum_tmp += " +adv_gb_output+"[" +str(i)+"].get(hash_key);"
                print >>fo,"\t\t\t\t"+adv_gb_output+"["+str(i)+"].put(hash_key, sum_tmp);"
                print >>fo,"\t\t\t}else{"
                print >>fo,"\t\t\t\t" + adv_gb_output+"["+str(i)+"].put(hash_key,(double)"+tmp+");"
                print >>fo,"\t\t\t}"

        if isinstance(tree.child,ystree.TableNode) and tree.child.where_condition is not None:
            print >>fo,"\t\t\t}\n"### end where condition
            
    else:

#### no map part agg

        if not isinstance(tree.child,ystree.TableNode) or tree.child.where_condition is None: 
            tmp_output = "\t\t\tcontext.write("
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

            tmp_output =  "\t\t\t\tcontext.write( "
            tmp_output += "new " + map_key_type + "(" + map_key +")"
            tmp_output += ","
            tmp_output += "new " + map_value_type + "(" + map_value + ")"
            tmp_output += ");"
            
            print >>fo, tmp_output
            
            print >>fo,"\t\t\t}" # end of if

    print >>fo,"\t\t}\n"    

    print >>fo,"\t}\n"

###### groupby reduce part

    line_counter = "al_line"
    agg_buffer = "result"
    d_count_buffer = "d_count_buf"

    buf_dict = {}
    for x in tree.table_list:
        buf_dict[x] = line_buffer

    reduce_key_type = "NullWritable"
    reduce_value_type = "Text"

    print >>fo,"\tpublic static class Reduce extends Reducer<"+ map_key_type+","+map_value_type+","+reduce_key_type+","+reduce_value_type+">{\n"
    
    print >>fo,"\t\tpublic void reduce("+map_key_type+" key, Iterable<"+map_value_type+"> v, Context context) throws IOException,InterruptedException{\n"
    print >>fo, "\t\t\tIterator values = v.iterator();"
    print >>fo, "\t\t\tDouble[] "+agg_buffer+" = new Double[" + str(len(gb_exp_list)) + "];"  

    print >>fo, "\t\t\tArrayList[] "+d_count_buffer+" = new ArrayList[" + str(len(gb_exp_list)) + "];"
    print >>fo, "\t\t\tString tmp = \"\";"

    print >>fo, "\t\t\tfor(int i=0;i<"+str(len(gb_exp_list))+";i++){\n"
    print >>fo, "\t\t\t\t"+agg_buffer+"[i] = 0.0;"
    print >>fo, "\t\t\t\t" + d_count_buffer + "[i] = new ArrayList();"
    print >>fo, "\t\t\t}\n"

    if config.advanced_agg is False:

### no map agg

        print >>fo, "\t\t\tint " + line_counter + " = 0;"
        print >>fo,"\t\t\twhile(values.hasNext()){\n"
        print >>fo, "\t\t\t\ttmp = values.next().toString();"
        if map_key_type == "Text":
            print >>fo, "\t\t\t\ttmp = key.toString().concat(tmp);"
        else:
            print >>fo, "\t\t\t\ttmp = key.toString().concat(\"|\" + tmp);"
        print >>fo, "\t\t\t\tString[] " + line_buffer + " = tmp.split(\"\\\|\");"

        for i in range(0,len(gb_exp_list)):
            exp = gb_exp_list[i]

            tmp_output = __select_func_convert_to_java__(exp,buf_dict)
            tmp_name = ystree.__groupby_func_name__(exp)
            if tmp_name == "SUM" or tmp_name == "AVG":
                print >>fo, "\t\t\t\t"+agg_buffer+"[" + str(i) + "] = "+agg_buffer+"[" +str(i) + "] + " + tmp_output + ";" 

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
                print >>fo,"\t\t\t\tif("+line_counter+"==0)"
                print >>fo,"\t\t\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)" + tmp_output + ";"
                print >>fo,"\t\t\t\telse{"
                print >>fo, "\t\t\t\t\tif("+agg_buffer+"[" + str(i) + "] > " + tmp_output + ")"
                print >>fo, "\t\t\t\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)" + tmp_output + ";"  
                print >>fo, "\t\t\t\t}" 

        print >>fo, "\t\t\t\t" + line_counter + "++;"
        print >>fo, "\t\t\t}\n" ### end of while

    else:

## map part agg

        print >>fo, "\t\t\tint[] " + line_counter + " = new int["+str(len(gb_exp_list)) + "];"
        print >>fo,"\t\t\tfor(int i=0;i<"+str(len(gb_exp_list)) + ";i++){"
        print >>fo,"\t\t\t\t"+line_counter+"["+str(i)+"] = 0;"
        print >>fo,"\t\t\t}"
        print >>fo,"\t\t\tint tmp_count = 0;"
        print >>fo,"\t\t\twhile(values.hasNext()){\n"
        print >>fo,"\t\t\t\tString[] tmp_buf = values.next().toString().split(\"\\\|\");"
        print >>fo,"\t\t\t\ttmp = key.toString();"
        print >>fo,"\t\t\t\tString[] agg_tmp;"
        for i in range(0,len(gb_exp_list)):
            exp = gb_exp_list[i]
            func_name = ystree.__groupby_func_name__(exp)
            print >>fo,"\t\t\t\tagg_tmp = tmp_buf["+str(i)+"].split(\"&\");"
            if func_name == "SUM":
                print >>fo, "\t\t\t\t"+agg_buffer+"[" + str(i) + "] += Double.parseDouble(agg_tmp[0]);" 
            elif func_name == "MIN":
                print >>fo,"\t\t\t\tif(tmp_count==0)"
                print >>fo,"\t\t\t\t\t"+agg_buffer+"[" + str(i) + "]=  Double.parseDouble(agg_tmp[0]);"
                print >>fo,"\t\t\t\telse if("+agg_buffer+"["+str(i)+"]>Double.parseDouble(agg_tmp[0]))"
                print >>fo,"\t\t\t\t\t"+agg_buffer+"[" + str(i) + "]=  Double.parseDouble(agg_tmp[0]);"
                
            elif func_name == "MAX":
                print >>fo,"\t\t\t\tif(tmp_count==0)"
                print >>fo,"\t\t\t\t\t"+agg_buffer+"[" + str(i) + "]=  Double.parseDouble(agg_tmp[0]);"
                print >>fo,"\t\t\t\telse if("+agg_buffer+"["+str(i)+"]<Double.parseDouble(agg_tmp[0]))"
                print >>fo,"\t\t\t\t\t"+agg_buffer+"[" + str(i) + "]=  Double.parseDouble(agg_tmp[0]);"
            elif func_name == "COUNT":
                print >>fo, "\t\t\t\t"+line_counter+"["+str(i)+"]+= Double.parseDouble(agg_tmp[0]);"
            elif func_name == "AVG":
                print >>fo, "\t\t\t\t"+agg_buffer+"["+str(i)+"] += Double.parseDouble(agg_tmp[0]);" 
                print >>fo, "\t\t\t\t"+line_counter+"["+str(i)+"]+= Double.parseDouble(agg_tmp[1]);"

        print >>fo,"\t\t\t\ttmp_count++;"
        print >>fo,"\t\t\t}" #### end of while
    

    print >>fo, "\t\t\tString[] " + line_buffer + " = tmp.split(\"\\\|\");"

    if config.advanced_agg is True:
        for i in range(0,len(gb_exp_list)):
            exp = gb_exp_list[i]
            if not isinstance(exp,ystree.YFuncExp):
                print >>sys.stderr,"Internal Error:__groupby_gen_mr__"
                exit(29)

            tmp_name = ystree.__groupby_func_name__(exp)
            if tmp_name == "AVG":
                print >>fo, "\t\t\t"+agg_buffer+"[" + str(i) + "] = "+agg_buffer+"[" + str(i) + "] /"+line_counter+"["+str(i)+"];" 

            elif tmp_name == "COUNT":
                print >>fo, "\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)"+ line_counter + "["+str(i)+"];" 

    else:
        for i in range(0,len(gb_exp_list)):
            exp = gb_exp_list[i]
            if not isinstance(exp,ystree.YFuncExp):
                print >>sys.stderr,"Internal Error:__groupby_gen_mr__"
                exit(29)

            tmp_name = ystree.__groupby_func_name__(exp)
            if tmp_name == "AVG":
                print >>fo, "\t\t\t"+agg_buffer+"[" + str(i) + "] = "+agg_buffer+"[" + str(i) + "] /"+line_counter+";" 

            elif tmp_name == "COUNT":
                print >>fo, "\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)"+ line_counter+";" 

            elif tmp_name == "COUNT_DISTINCT":
                print >>fo, "\t\t\t"+agg_buffer+"[" + str(i) + "] = (double)"+d_count_buffer+"["+str(i)+"].size();"


    col_list = []
    if tree.having_clause is not None:
        ystree.__get_gb_list__(tree.having_clause.where_condition_exp,col_list)

    having_len = len(col_list)

    buf_dict = {}
    for x in tree.table_list:
        buf_dict[x] = line_buffer

    buf_dict["AGG"] = agg_buffer 

    reduce_value = ""

    for i in range(0,len(tree.select_list.tmp_exp_list)-having_len):
        exp = tree.select_list.tmp_exp_list[i]
        if isinstance(exp,ystree.YFuncExp):
            tmp_list = []
            __get_gb_exp__(exp,tmp_list)
            if len(tmp_list) >0:
                reduce_value += __gb_exp_to_java__(exp,gb_exp_list,buf_dict,None)
                if reduce_value_type == "Text":
                    reduce_value += " + \"|\""
                reduce_value += "+"
            else:
                reduce_value += __select_func_convert_to_java__(exp,buf_dict)
                if reduce_value_type == "Text":
                    reduce_value += " + \"|\""
                reduce_value += "+"

        elif isinstance(exp,ystree.YRawColExp): 
            reduce_value += __para_to_java__(exp.column_type,exp.column_name,line_buffer)
            if reduce_value_type == "Text":
                reduce_value += " + \"|\""
            reduce_value += "+"

        else:
            reduce_value += __para_to_java__(exp.cons_type,exp.cons_value,None)
            if reduce_value_type == "Text":
                reduce_value += " + \"|\""
            reduce_value += "+"

    reduce_value = reduce_value[:-1]

    if reduce_value == "":
        reduce_value = "\" \""

    print >>fo, "\t\t\tNullWritable key_op = NullWritable.get();"
    

    if tree.where_condition is not None:
        tmp_list = []
        __get_gb_exp__(tree.where_condition.where_condition_exp,tmp_list)
        for tmp in tmp_list:
            for exp in gb_exp_list:
                if tmp.compare(exp) is True:
                    func_obj = tmp.func_obj
                    exp_index = gb_exp_list.index(exp)
                    new_exp = ystree.YRawColExp("AGG",exp_index)
                    new_exp.column_name = int(new_exp.column_name)
                    new_exp.column_type = tmp.get_value_type()
                    func_obj.replace(tmp,new_exp)
                    break

        buf_dict = {}
        buf_dict["AGG"] = agg_buffer
        for x in tree.table_list:
            buf_dict[x] = line_buffer

        tmp_output = "\t\t\tif("+ __where_convert_to_java__(tree.where_condition.where_condition_exp,buf_dict) + "){\n"
        tmp_output += "\t\t\t\tcontext.write(key_op"
        tmp_output += ","
        tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
        tmp_output += ");"

        tmp_output += "\t\t\t}\n"


    else:
        tmp_output = "\t\t\tcontext.write(key_op" 
        tmp_output += ","
        tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
        tmp_output += ");"

    print >>fo, tmp_output

    
    print >>fo,"\t\t}\n"   ### end of reduce func

    print >>fo,"\t}\n"

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
                print >>sys.stderr,"Internal Error:__gen_func_exp__"
                exit(29)

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
                print >>sys.stderr,"Internal Error:__gen_join_where__"
                exit(29)

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

### join map part

    line_buffer = "line_buf"

    if tree.select_list is None:
        print >>sys.stderr,"Internal Error:__join_gen_mr__"
        exit(29)

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


    if left_key_type != right_key_type:
        print >>sys.stderr,"Internal Error:__join_gen_mr__"
        exit(29)

    map_key_type = left_key_type 
    map_value_type = "Text"  ## we need to add tag to differentiate the data from left table and right table
    
    print >>fo,"\tpublic static class Map extends  Mapper<Object, Text,"+map_key_type+","+map_value_type+">{\n"
    print >>fo, "\t\tprivate int left = 0;"
    print >>fo, "\t\tpublic void setup(Context context) throws IOException, InterruptedException {\n"
    print >>fo, "\t\t\tint last_index = -1, start_index = -1;"
    print >>fo, "\t\t\tString path = ((FileSplit)context.getInputSplit()).getPath().toString();"
    print >>fo, "\t\t\tlast_index = path.lastIndexOf(\'/\');"
    print >>fo,"\t\t\tlast_index = last_index - 1;"
    print >>fo, "\t\t\tstart_index = path.lastIndexOf(\'/\',last_index);"
    print >>fo, "\t\t\tString f_name = path.substring(start_index+1,last_index+1);"
    print >>fo, "\t\t\tif(f_name.compareTo(\"" + left_name + "\") == 0 )"
    print >>fo, "\t\t\t\tleft = 1;"
    print >>fo,"\t\t}" 

    print >>fo,"\t\tpublic void map(Object key, Text value,Context context) throws IOException,InterruptedException{\n"
    
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
        print >>fo,"\t\t\tif(n<" + str(max_index) + ")"
        print >>fo,"\t\t\t\t"+line_buffer+ "[n] = line.substring(prev,i);"


    buf_dict = {}
    buf_dict["LEFT"] = line_buffer
    left_key = __gen_mr_value__(left_key_list,left_key_type,buf_dict)

    buf_dict = {}
    for x in tree.left_child.table_list:
        if x not in buf_dict.keys():
            buf_dict[x] = line_buffer
    if isinstance(tree.left_child,ystree.TableNode):
        if tree.left_child.table_name not in buf_dict.keys():
            buf_dict[tree.left_child.table_name] = line_buffer

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
            print >>fo,"\t\t\tif(n<" + str(max_index) + ")"
            print >>fo,"\t\t\t\t"+line_buffer+ "[n] = line.substring(prev,i);"

        if not isinstance(tree.left_child,ystree.TableNode) or tree.left_child.where_condition is None:
            tmp_output = "\t\t\t\tcontext.write(new " + left_key_type + "(" + left_key + ")"
            tmp_output += ", "
            tmp_output += "new " + left_value_type + "(\"L\"+\"|\" +"+ left_value +")"
            tmp_output += ");"

            print >>fo,tmp_output

        else:
            where_str = "\t\t\t\tif("
            where_str +=__where_convert_to_java__(tree.left_child.where_condition.where_condition_exp,buf_dict)
            where_str += "){\n"
            print >>fo,where_str

            tmp_output = "\t\t\t\t\tcontext.write(new " + left_key_type + "(" + left_key + ")"
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
    if isinstance(tree.right_child,ystree.TableNode):
        if tree.right_child.table_name not in buf_dict.keys():
            buf_dict[tree.right_child.table_name] = line_buffer

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
            print >>fo,"\t\t\tif(n<" + str(max_index) + ")"
            print >>fo,"\t\t\t\t"+line_buffer+ "[n] = line.substring(prev,i);"
            
        if not isinstance(tree.right_child,ystree.TableNode) or tree.right_child.where_condition is  None:
            tmp_output = "\t\t\t\tcontext.write(new " + right_key_type + "(" + right_key + ")"
            tmp_output += ", "
            tmp_output += "new " + right_value_type + "(\"R\"+\"|\" +"+ right_value +")"
            tmp_output += ");"

            print >>fo, tmp_output
            
        else:
            where_str = "\t\t\t\tif("
            where_str +=__where_convert_to_java__(tree.right_child.where_condition.where_condition_exp,buf_dict)
            where_str += "){\n"
            print >>fo,where_str

            tmp_output = "\t\t\t\t\tcontext.write(new " + right_key_type + "(" + right_key + ")"
            tmp_output += ", "
            tmp_output += "new " + right_value_type + "(\"R\"+\"|\" +"+ right_value +")"
            tmp_output += ");"

            print >>fo, tmp_output

            print >>fo,"\t\t\t\t}" # end of if

    if self_join_bool is False:
        print >>fo,"\t\t\t}\n"

    print >>fo,"\t\t}\n" ### end of map func

    print >>fo,"\t}\n"  ## end of map class

### join reduce part

    left_array = "al_left"
    right_array = "al_right"

    reduce_key_type = "NullWritable"
    reduce_value_type = "Text"

    print >>fo,"\tpublic static class Reduce extends  Reducer<"+ map_key_type+","+map_value_type+","+reduce_key_type+","+reduce_value_type+">{\n"
    print >>fo, "\t\tpublic void reduce("+map_key_type+" key, Iterable<"+map_value_type+"> v, Context context) throws IOException,InterruptedException{\n"

    print >>fo, "\t\t\tIterator values = v.iterator();"
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


                tmp_output = "context.write("

                #tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
                tmp_output += "key_op"
                tmp_output += ", "
                tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
                tmp_output += ");"

                print >>fo, "\t\t\t\t\t\t\t",tmp_output

                print >>fo,"\t\t\t\t\t\t}\n"  #### end of where condtion

            else:
                if tree.select_list is None:
                    print >>sys.stderr,"Internal Error:__join_gen_mr__"
                    exit(29)

                tmp_output = "context.write("

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
                    print >>sys.stderr,"Internal Error:__join_gen_mr__"
                    exit(29)

                print >>fo,"\t\t\t\t\tif(" + __where_convert_to_java__(new_where,buf_dict) + "){\n" 

                tmp_output = "context.write("

                #tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
                tmp_output += "key_op"
                tmp_output += ", "
                tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
                tmp_output += ");"

                print >>fo,"\t\t\t\t\t\t",tmp_output

                print >>fo, "\t\t\t\t\t}"

                
            else:
                tmp_output = "context.write("
                tmp_output += "key_op"
                tmp_output += ","
                tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
                tmp_output += ");"

                print >>fo,"\t\t\t\t\t",tmp_output

            print >>fo, "\t\t\t\t}\n" ### end of else

            print >>fo, "\t\t\t}\n" ## end of for

        elif join_type == "RIGHT":


            reduce_value = __gen_mr_value__(tree.select_list.tmp_exp_list,reduce_value_type,buf_dict)
            print >>fo,"\t\t\tfor(int i=0;i<" +right_array + ".size();i++){\n"
            print >>fo,"\t\t\t\tString[] " + right_line_buffer + " = ((String)" + right_array + ".get(i)).split(\"\\\|\");"
            print >>fo, "\t\t\t\tif(" + left_array + ".size()>0){\n"
            
            print >>fo,"\t\t\t\t\tfor(int j=0;j<" +left_array + ".size();j++){\n"
            print >>fo,"\t\t\t\t\t\tString[] " + left_line_buffer + " = ((String)" + left_array + ".get(j)).split(\"\\\|\");"
            if tree.where_condition is not None:
                exp = tree.where_condition.where_condition_exp

                print >>fo,"\t\t\t\t\t\tif(" + __where_convert_to_java__(exp,buf_dict) + "){\n"


                tmp_output = "context.write("

                #tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
                tmp_output += "key_op"
                tmp_output += ", "
                tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
                tmp_output += ");"

                print >>fo, "\t\t\t\t\t\t\t",tmp_output

                print >>fo,"\t\t\t\t\t\t}\n"  #### end of where condtion

            else:
                if tree.select_list is None:
                    print >>sys.stderr,"Internal Error:__join_gen_mr__"
                    exit(29)

                tmp_output = "context.write("

                #tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
                tmp_output += "key_op"
                tmp_output += ", "
                tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
                tmp_output += ");"

                print >>fo, "\t\t\t\t\t\t",tmp_output

            print >>fo, "\t\t\t\t\t}\n"

            print >>fo, "\t\t\t\t}else{\n"

            new_list = []

            __gen_join_list__(tree.select_list.tmp_exp_list,new_list,"RIGHT")

            reduce_value = __gen_mr_value__(new_list,reduce_value_type,buf_dict)

            if tree.where_condition is not None:
                new_where = None
                new_where = __gen_join_where__(tree.where_condition.where_condition_exp,"RIGHT")

                if new_where is None:
                    print >>sys.stderr,"Internal Error:__join_gen_mr__"
                    exit(29)

                print >>fo,"\t\t\t\t\tif(" + __where_convert_to_java__(new_where,buf_dict) + "){\n"

                tmp_output = "context.write("

                #tmp_output += "new " + reduce_key_type + "(" + reduce_key + ")"
                tmp_output += "key_op"
                tmp_output += ", "
                tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
                tmp_output += ");"

                print >>fo,"\t\t\t\t\t\t",tmp_output

                print >>fo, "\t\t\t\t\t}"

            else:
                tmp_output = "context.write("
                tmp_output += "key_op"
                tmp_output += ","
                tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
                tmp_output += ");"

                print >>fo,"\t\t\t\t\t",tmp_output

            print >>fo, "\t\t\t\t}\n" ### end of else


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
            tmp_output = "context.write("
            tmp_output += "key_op"
            tmp_output += ", "
            tmp_output += "new " + reduce_value_type + "(" + reduce_value + ")"
            tmp_output += ");"

            print >>fo, "\t\t\t\t\t\t",tmp_output

            print >>fo,"\t\t\t\t\t}"

        else:
            if tree.select_list is None:
                print >>sys.stderr,"Internal Error:__join_gen_mr__"
                exit(29)

            tmp_output = "context.write("
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
    
def __composite_gen_mr__(tree,fo):

    line_buffer = "line_buf"
    map_key_type = ""

    tn_to_tag = {}
    i = 1
    index_to_name = {}

    filename = fo.name.split(".java")[0]

    for node in tree.child_list:
        index = tree.child_list.index(node)
        tn = filename[:-1] + str(int(filename[-1]) + index +1)
        index_to_name[index] = tn
        tree.pk_dict[tn] = copy.deepcopy(tree.pk_dict[index])
        del tree.pk_dict[index]
        for exp in tree.pk_dict[tn][0]:
            exp.table_name = tn
        exp_list = None
        if isinstance(node,ystree.CompositeNode):
            exp_list = node.jfc_node_list[-1].select_list.tmp_exp_list
        else:
            exp_list = node.select_list.tmp_exp_list
        tmp_exp_list = []
        for tmp in exp_list:
            tmp_in = exp_list.index(tmp)
            new_exp = ystree.YRawColExp(tn,tmp_in)
            new_exp.table_name = tn
            new_exp.column_name = int(new_exp.column_name)
            new_exp.column_type = tmp.column_type
            tmp_exp_list.append(new_exp)

        tree.mapoutput[tn] = tmp_exp_list
        
    buf_dict = {}
    for x in tree.mapoutput.keys():
        tn_to_tag[x] = i
        buf_dict[x] = line_buffer
        map_key_type = __get_key_value_type__(tree.pk_dict[x][0])
        i = i +1

    map_value_type = "Text"


    print >>fo,"\tpublic static class Map extends  Mapper<Object, Text,"+map_key_type+","+map_value_type+">{\n"
    print >>fo, "\t\tprivate String filename;"
    print >>fo, "\t\tprivate int filetag = -1;"
    print >>fo, "\t\tpublic void setup(Context context) throws IOException, InterruptedException {\n"
    print >>fo, "\t\t\tint last_index = -1, start_index = -1;"
    print >>fo, "\t\t\tString path = ((FileSplit)context.getInputSplit()).getPath().toString();"
    print >>fo, "\t\t\tlast_index = path.lastIndexOf(\'/\');"
    print >>fo,"\t\t\tlast_index = last_index - 1;"
    print >>fo, "\t\t\tstart_index = path.lastIndexOf(\'/\',last_index);"
    print >>fo, "\t\t\tfilename = path.substring(start_index+1,last_index+1);"
    for tn in tn_to_tag.keys():
        print >>fo, "\t\t\tif(filename.compareTo(\""+tn+"\")==0){"
        print >>fo, "\t\t\t\tfiletag = " + str(tn_to_tag[tn]) + ";"
        print >>fo, "\t\t\t}"
    print >>fo,"\t\t}\n" 

    print >>fo,"\t\tpublic void map(Object key, Text value,Context context) throws IOException,InterruptedException{\n"
    print >>fo,"\t\t\tString line = value.toString();"
    print >>fo,"\t\t\tString[] " + line_buffer + "= line.split(\"\\\|\");"
    print >>fo,"\t\t\tBitSet dispatch = new BitSet(32);"

    for table_name in tree.mapoutput.keys():

        map_key = __gen_mr_key__(tree.pk_dict[table_name][0],map_key_type,buf_dict)

        print >>fo,"\t\t\tif(filetag =="+str(tn_to_tag[table_name])+"){\n"
        map_value = __gen_mr_value__(tree.mapoutput[table_name],map_value_type,buf_dict)

#### generate map where_exp
        mapfilter = {}
        for x in tree.mapfilter.keys():
            where_exp = None
            for y in tree.mapfilter[x]:
                if where_exp is None:
                    where_exp = y
                else:
                    para_list = []
                    para_list.append(where_exp)
                    para_list.append(y)
                    where_exp = ystree.YFuncExp("OR",para_list)
            mapfilter[x] = where_exp

        if table_name in tree.mapfilter.keys():
            print >>fo, "\t\t\t\tif(" + __where_convert_to_java__(mapfilter[table_name],buf_dict) + "){\n"

#### dispatch #####

            for x in tree.it_node_list:
                if isinstance(x,ystree.GroupByNode):
                    if table_name in x.table_list and x.child.where_condition is not None:
                        where_exp = x.child.where_condition.where_condition_exp
                        print >>fo,"\t\t\t\t\tif(!("+__where_convert_to_java__(where_exp,buf_dict) + "))"
                        print >>fo,"\t\t\t\t\t\tdispatch.set(",tree.it_node_list.index(x),");"

                elif isinstance(x,ystree.TwoJoinNode):
                    self_join_bool = __self_join__(x)
                    if isinstance(x.left_child,ystree.TableNode):
                        if table_name == x.left_child.table_name and x.left_child.where_condition is not None:
                            where_exp = x.left_child.where_condition.where_condition_exp
                            print >>fo,"\t\t\t\t\tif(!("+__where_convert_to_java__(where_exp,buf_dict) + "))"
                            if self_join_bool is False:
                                print >>fo,"\t\t\t\t\t\tdispatch.set(",tree.it_node_list.index(x),");"
                            else:
                                print >>fo,"\t\t\t\t\t\tdispatch.set(",16+tree.it_node_list.index(x),");"

                    if isinstance(x.right_child,ystree.TableNode):
                        if table_name == x.right_child.table_name and x.right_child.where_condition is not None:
                            where_exp = x.right_child.where_condition.where_condition_exp
                            print >>fo,"\t\t\t\t\tif(!("+__where_convert_to_java__(where_exp,buf_dict) + "))"
                            if self_join_bool is False:
                                print >>fo,"\t\t\t\t\t\tdispatch.set(",tree.it_node_list.index(x),");"
                            else:
                                print >>fo,"\t\t\t\t\t\tdispatch.set(",17+tree.it_node_list.index(x),");"

            print >>fo,"\t\t\t\t\tif(dispatch.isEmpty())"
            output = "\t\t\t\t\t\tcontext.write("
            output += "new " + map_key_type + "(" + map_key + ")"
            output += ","
            output += "new " + map_value_type + "(" + str(tn_to_tag[table_name]) + "+\"||\"+" + map_value + ")"
            output += ");"

            print >>fo, output
            print >>fo,"\t\t\t\t\telse"
            output = "\t\t\t\t\t\tcontext.write("
            output += "new " + map_key_type + "(" + map_key + ")"
            output += ","
            output += "new " + map_value_type + "(" + str(tn_to_tag[table_name]) + "+\"|\"+dispatch.toString()+\"|\"+" + map_value + ")"
            output += ");"
            print >>fo,output
            print >>fo,"\t\t\t\t}"

        else: 
            output = "\t\t\t\tcontext.write("
            output += "new " + map_key_type + "(" + map_key + ")"
            output += ","
            output += "new " + map_value_type + "(" + str(tn_to_tag[table_name]) + "+\"||\"+" + map_value + ")"
            output += ");"
            print >>fo,output

        print >>fo, "\t\t\t}\n"

    print >>fo, "\t\t}\n"
    print >>fo,"\t}\n"

    reduce_key_type = "NullWritable"
    reduce_value_type = "Text"

    print >>fo,"\tpublic static class Reduce extends  Reducer<"+ map_key_type+","+map_value_type+","+reduce_key_type+","+reduce_value_type+">{\n"
    print >>fo, "\t\tpublic void reduce("+map_key_type+" key, Iterable<"+map_value_type+"> v, Context context) throws IOException,InterruptedException{\n"

##########reduce part variable declaration

    print >>fo,"\t\t\tIterator values = v.iterator();"
    print >>fo,"\t\t\tArrayList[] it_output = new ArrayList[" +str(len(tree.it_node_list)) + "];" 
    print >>fo,"\t\t\tfor(int i=0;i<"+str(len(tree.it_node_list))+";i++){"
    print >>fo,"\t\t\t\tit_output[i]=new ArrayList();"
    print >>fo,"\t\t\t}"

    agg_buffer = "result"
    d_count_buf = "d_count_buf"
    line_counter = "al_line"
    left_array = "al_left"
    right_array = "al_right"

    print >>fo,"\t\t\tString tmp = \"\";"
    for x in tree.it_node_list:
        if isinstance(x,ystree.GroupByNode):
            gb_exp_list = []
            __get_gbexp_list__(x.select_list.tmp_exp_list,gb_exp_list)

            tmp_agg_buffer = agg_buffer + "_" +str(tree.it_node_list.index(x)) 
            tmp_count_buf = d_count_buf + "_" +str(tree.it_node_list.index(x)) 
            tmp_line_counter = line_counter + "_"+str(tree.it_node_list.index(x)) 

            print >>fo,"\t\t\tDouble[] " + tmp_agg_buffer+"=new Double["+str(len(gb_exp_list))+"];"
            print >>fo,"\t\t\tArrayList[] " + tmp_count_buf+"=new ArrayList["+str(len(gb_exp_list)) + "];"
            print >>fo,"\t\t\tint "+tmp_line_counter + " = 0;"
            print >>fo,"\t\t\tfor(int i=0;i<"+str(len(gb_exp_list))+";i++){"
            print >>fo,"\t\t\t\t"+tmp_agg_buffer + "[i] = 0.0;"
            print >>fo,"\t\t\t\t"+tmp_count_buf+"[i] = new ArrayList();"
            print >>fo,"\t\t\t}\n"

        elif isinstance(x,ystree.TwoJoinNode):
            tmp_left_array = left_array + "_" + str(tree.it_node_list.index(x)) 
            tmp_right_array = right_array + "_" + str(tree.it_node_list.index(x)) 
            print >>fo,"\t\t\tArrayList " + tmp_left_array + "= new ArrayList();"
            print >>fo,"\t\t\tArrayList " + tmp_right_array + "= new ArrayList();"

############## go through each value

    print >>fo,"\t\t\twhile(values.hasNext()){"
    print >>fo,"\t\t\t\tString line = values.next().toString();"
    print >>fo,"\t\t\t\tString dispatch = line.split(\"\\\|\")[1];"
    print >>fo,"\t\t\t\ttmp = line.substring(2+dispatch.length()+1);"
    print >>fo,"\t\t\t\tString[] "+line_buffer + "= tmp.split(\"\\\|\");"

    for x in tree.it_node_list:
        if isinstance(x,ystree.GroupByNode):
            tmp_agg_buffer = agg_buffer + "_" + str(tree.it_node_list.index(x)) 
            tmp_d_count_buf = d_count_buf + "_" +str(tree.it_node_list.index(x)) 
            tmp_line_counter = line_counter + "_"+str(tree.it_node_list.index(x))

            gb_exp_list = []
            __get_gbexp_list__(x.select_list.tmp_exp_list,gb_exp_list)

            tn = x.child.table_name
            index = tree.it_node_list.index(x)
            if_stat = "\t\t\t\tif(line.charAt(0) =='" + str(tn_to_tag[tn]) + "'"
            if_stat += "&& ("
            if_stat += "dispatch.length()==0 ||"
            if_stat += "dispatch.indexOf('" + str(index) + "')==-1"
            if_stat += ")){"
            print >>fo, if_stat
            for i in range(0,len(gb_exp_list)):
                exp = gb_exp_list[i]
                if not isinstance(exp,ystree.YFuncExp):
                    print >>sys.stderr,"Internal Error: gen_composite"
                    exit(29)
                tmp_output = __select_func_convert_to_java__(exp,buf_dict) 
                tmp_name = ystree.__groupby_func_name__(exp)
                if tmp_name == "SUM" or tmp_name == "AVG":
                    print >>fo,"\t\t\t\t\t"+tmp_agg_buffer+"["+str(i)+"] +="+tmp_output+";"
                elif tmp_name == "COUNT_DISTINCT":
                    print >>fo,"\t\t\t\t\tif("+tmp_d_count_buf+"["+str(i)+"].contains("+tmp_output+")==false)"
                    print >>fo,"\t\t\t\t\t\t"+tmp_d_count_buf+"["+str(i)+"].add("+tmp_output+");"
                elif tmp_name == "MAX":
                    print >>fo,"\t\t\t\t\tif("+tmp_line_counter+"==0)"
                    print >>fo,"\t\t\t\t\t\t"+tmp_agg_buffer+"["+str(i)+"]=(double) "+tmp_output + ";"
                    print >>fo,"\t\t\t\t\telse if("+tmp_agg_buffer+"["+str(i)+"]>"+tmp_output+")"
                    print >>fo,"\t\t\t\t\t\t"+tmp_agg_buffer+"["+str(i)+"]= (double) "+tmp_output+";"
                elif tmp_name == "MIN":
                    print >>fo,"\t\t\t\t\tif("+tmp-line_counter+"==0)"
                    print >>fo,"\t\t\t\t\t\t"+tmp_agg_buffer+"["+str(i)+"]=(double) "+tmp_output + ";"
                    print >>fo,"\t\t\t\t\telse if("+tmp_agg_buffer+"["+str(i)+"]<"+tmp_output+")"
                    print >>fo,"\t\t\t\t\t\t"+tmp_agg_buffer+"["+str(i)+"]= (double) "+tmp_output,+";"

            print >>fo, "\t\t\t\t\t" + tmp_line_counter+ "++;"
            print >>fo,"\t\t\t\t}"


        elif isinstance(x,ystree.TwoJoinNode):
            self_join_bool = __self_join__(x)
            index = tree.it_node_list.index(x)
            tmp_left_array = left_array + "_" + str(tree.it_node_list.index(x)) 
            tmp_right_array = right_array + "_" +str(tree.it_node_list.index(x)) 
            if isinstance(x.left_child,ystree.TableNode):
                left_tn = x.left_child.table_name
            else:
                if x.left_composite is not None:
                    left_tn = index_to_name[tree.child_list.index(x.left_composite)]
                else:
                    if x.left_child in tree.it_node_list or x.left_child in tree.jfc_node_list:
                        continue
                    else:
                        left_tn = index_to_name[tree.child_list.index(x.left_child)]

            if_stat = "\t\t\t\tif(line.charAt(0)=='" + str(tn_to_tag[left_tn]) + "'"
            if_stat += "&&("
            if_stat += "dispatch.length()==0 ||"
            if self_join_bool is False:
                if_stat += "dispatch.indexOf(\"" + str(index) + "\")==-1"
            else:
                if_stat += "dispatch.indexOf(\"" + str(16+index) + "\")==-1"
            if_stat += "))"
            print >>fo,if_stat
            print >>fo,"\t\t\t\t\t"+tmp_left_array + ".add(tmp);"

            if isinstance(x.right_child,ystree.TableNode):
                right_tn = x.right_child.table_name
            else:
                if x.right_composite is not None:
                    right_tn = index_to_name[tree.child_list.index(x.right_composite)]
                else:
                    if x.right_child in tree.it_node_list or x.right_child in tree.jfc_node_list:
                        continue
                    else:
                        right_tn = index_to_name[tree.child_list.index(x.right_child)]

            if_stat = "\t\t\t\tif(line.charAt(0)=='" + str(tn_to_tag[right_tn]) + "'"
            if_stat += "&&("
            if_stat += "dispatch.length()==0 ||"
            if self_join_bool is False:
                if_stat += "dispatch.indexOf(\"" + str(index) + "\")==-1"
            else:
                if_stat += "dispatch.indexOf(\"" + str(17+index) + "\")==-1"
            if_stat += "))"
            print >>fo,if_stat
            print >>fo,"\t\t\t\t\t"+tmp_right_array + ".add(tmp);"

    print >>fo,"\t\t\t}"  #######end of while(values.hasNext())


#### sum up the value

    print >>fo,"\t\t\tString[] "+line_buffer+" = tmp.split(\"\\\|\");"
    for x in tree.it_node_list:
        if isinstance(x,ystree.GroupByNode):
            tmp_agg_buffer = agg_buffer + "_"+str(tree.it_node_list.index(x)) 
            tmp_d_count_buf = d_count_buf + "_" +str(tree.it_node_list.index(x)) 
            tmp_line_counter = line_counter+"_"+str(tree.it_node_list.index(x))

            gb_exp_list = []
            __get_gbexp_list__(x.select_list.tmp_exp_list,gb_exp_list)

            for i in range(0,len(gb_exp_list)):
                exp = gb_exp_list[i]
                if not isinstance(exp,ystree.YFuncExp):
                    print >>sys.stderr,"Internal Error: gen_composite"
                    exit(29)

                tmp_name = ystree.__groupby_func_name__(exp)
                if tmp_name == "AVG":
                    print >>fo,"\t\t\t"+tmp_agg_buffer+"["+str(i)+"]="+tmp_agg_buffer+"["+str(i)+"]/"+tmp_line_counter+";"
                elif tmp_name == "COUNT":
                    print >>fo,"\t\t\t"+tmp_agg_buffer+"["+str(i)+"]=(double)" + tmp_line_counter+";"
                elif tmp_name == "COUNT_DISTINCT":
                    print >>fo,"\t\t\t",tmp_agg_buffer+"["+str(i) +"]=(double)"+tmp_d_count_buf+"["+str(i) + "].size();"

            col_list = []
            if x.having_clause is not None:
                ystree.__get_gb_list__(tree.having_clause.where_condition_exp,col_list)

            having_len = len(col_list)

            buf_dict = {}
            for tn in x.table_list:
                buf_dict[tn] = line_buffer

            buf_dict["AGG"] = tmp_agg_buffer
            reduce_value = ""
            for j in range(0,len(x.select_list.tmp_exp_list)-having_len):
                exp = x.select_list.tmp_exp_list[j]
                if isinstance(exp,ystree.YFuncExp):
                    tmp_list = []
                    __get_gb_exp__(exp,tmp_list)
                    if len(tmp_list) >0:
                        reduce_value += __gb_exp_to_java__(exp,gb_exp_list,buf_dict,None)
                        if reduce_value_type == "Text":
                            reduce_value += " + \"|\""
                        reduce_value += "+"
                    else:
                        reduce_value += __select_func_convert_to_java__(exp,buf_dict)
                        if reduce_value_type == "Text":
                            reduce_value += " + \"|\""
                        reduce_value += "+"

                elif isinstance(exp,ystree.YRawColExp):
                    reduce_value += __para_to_java__(exp.column_type,exp.column_name,line_buffer)
                    if reduce_value_type == "Text":
                        reduce_value += " + \"|\""
                    reduce_value += "+"
                else:
                    reduce_value += __para_to_java__(exp.cons_type,exp.cons_value,None)
                    if reduce_value_type == "Text":
                        reduce_value += " + \"|\""
                    reduce_value += "+"

            reduce_value = reduce_value[:-1]
            if reduce_value == "":
                reduce_value = "\" \""

            if x.where_condition is not None:
                buf_dict = {}
                buf_dict["AGG"] = tmp_agg_buffer
                for tn in x.table_list:
                    buf_dict[tn] = line_buffer

                tmp_list = []
                __get_gb_exp__(x.where_condition.where_condition_exp,tmp_list)
                for tmp in tmp_list:
                    for exp in gb_exp_list:
                        if tmp.compare(exp) is True:
                            func_obj = tmp.func_obj
                            exp_index = gb_exp_list.index(exp)
                            new_exp = ystree.YRawColExp("AGG",exp_index)
                            new_exp.column_name = int(new_exp.column_name)
                            new_exp.column_type = tmp.get_value_type()
                            func_obj.replace(tmp,new_exp)
                            break

                print >>fo,"\t\t\tif("+ __where_convert_to_java__(x.where_condition.where_condition_exp,buf_dict) + ")"
                print >>fo,"\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add(" + reduce_value + ");"
            else:
                print >>fo,"\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add(" + reduce_value + ");"

        elif isinstance(x,ystree.TwoJoinNode):
            if x.left_child in tree.it_node_list or x.right_child in tree.it_node_list: 
                if x.parent in tree.jfc_node_list:
                    index = tree.jfc_node_list.index(x.parent)
                    tree.jfc_node_list.insert(index,x)
                else:
                    tree.jfc_node_list.append(x)
                continue

            elif x.left_child in tree.jfc_node_list or x.right_child in tree.jfc_node_list: 
                if x.parent in tree.jfc_node_list:
                    index = tree.jfc_node_list.index(x.parent)
                    tree.jfc_node_list.insert(index,x)
                else:
                    tree.jfc_node_list.append(x)
                continue

            tmp_left_array = left_array+"_"+str(tree.it_node_list.index(x)) 
            tmp_right_array = right_array+"_"+str(tree.it_node_list.index(x)) 
            buf_dict = {}
            left_line_buffer = "left_buf_"+str(tree.it_node_list.index(x))
            right_line_buffer = "right_buf_"+str(tree.it_node_list.index(x))
            buf_dict["LEFT"] = left_line_buffer
            buf_dict["RIGHT"] = right_line_buffer
            reduce_value_type = "Text"

            if x.join_explicit is True:
                join_type = x.join_type.upper()
                if join_type == "LEFT":
                    reduce_value = __gen_mr_value__(x.select_list.tmp_exp_list,reduce_value_type,buf_dict)
                    print >>fo,"\t\t\tfor(int i=0;i<" + tmp_left_array + ".size();i++){"
                    print >>fo,"\t\t\t\tString[] "+left_line_buffer+"=((String)"+tmp_left_array+".get(i)).split(\"\\\|\");"
                    print >>fo,"\t\t\t\tif("+tmp_right_array+".size()>0){"
                    print >>fo,"\t\t\t\t\tfor(int j=0;j<"+tmp_right_array+".size();j++){"
                    print >>fo,"\t\t\t\t\t\tString[] "+right_line_buffer+" = ((String)"+tmp_right_array+".get(j)).split(\"\\\|\");"
                    if x.where_condition is not None:
                        exp = x.where_condition.where_condition_exp
                        print >>fo,"\t\t\t\t\t\tif("+__where_convert_to_java__(exp,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                    print >>fo,"\t\t\t\t\t}"
                    print >>fo,"\t\t\t\t}else{"
                    new_list = []
                    __gen_join_list__(x.select_list.tmp_exp_list,new_list,"LEFT")
                    reduce_value = __gen_mr_value__(new_list,reduce_value_type,buf_dict)
                    if x.where_condition is not None:
                        new_where = __gen_join_where__(x.where_condition.where_condition_exp,"LEFT")
                        print >>fo,"\t\t\t\t\t\tif("+__where_convert_to_java__(new_where,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"

                    print >>fo,"\t\t\t\t}"
                    print >>fo,"\t\t\t}"

                elif join_type == "RIGHT":
                    reduce_value = __gen_mr_value__(x.select_list.tmp_exp_list,reduce_value_type,buf_dict)
                    print >>fo,"\t\t\tfor(int i=0;i<" + tmp_right_array + ".size();i++){"
                    print >>fo,"\t\t\t\tString[] "+right_line_buffer+"=((String)"+tmp_right_array+".get(i)).split(\"\\\|\");"
                    print >>fo,"\t\t\t\tif("+tmp_left_array+".size()>0){"
                    print >>fo,"\t\t\t\t\tfor(int j=0;j<"+tmp_left_array+".size();j++){"
                    print >>fo,"\t\t\t\t\t\tString[] "+left_line_buffer+" = ((String)"+tmp_left_array+".get(j)).split(\"\\\|\");"
                    if x.where_condition is not None:
                        exp = x.where_condition.where_condition_exp
                        print >>fo,"\t\t\t\t\t\tif("+__where_convert_to_java__(exp,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                    print >>fo,"\t\t\t\t\t}"
                    print >>fo,"\t\t\t\t}else{"
                    new_list = []
                    __gen_join_list__(x.select_list.tmp_exp_list,new_list,"RIGHT")
                    reduce_value = __gen_mr_value__(new_list,reduce_value_type,buf_dict)
                    if x.where_condition is not None:
                        new_where = __gen_join_where__(x.where_condition.where_condition_exp,"RIGHT")
                        print >>fo,"\t\t\t\t\t\tif("+__where_convert_to_java__(new_where,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"

                    print >>fo,"\t\t\t\t}"
                    print >>fo,"\t\t\t}"

                else:
                    print >>sys.stderr,"Internal Error: gen_composite"
                    exit(29)
            else:
                print >>fo,"\t\t\tfor(int i=0;i<"+tmp_left_array+".size();i++){"
                print >>fo,"\t\t\t\tString[] "+left_line_buffer+"=((String)"+tmp_left_array+".get(i)).split(\"\\\|\");"
                print >>fo, "\t\t\t\tfor(int j=0;j<"+tmp_right_array+".size();j++){"
                print >>fo,"\t\t\t\t\tString[] "+right_line_buffer+"=((String)"+tmp_right_array+".get(j)).split(\"\\\|\");"
                reduce_value = __gen_mr_value__(x.select_list.tmp_exp_list,reduce_value_type,buf_dict)
                if x.where_condition is not None:
                    exp = x.where_condition.where_condition_exp
                    print >>fo,"\t\t\t\t\tif(" + __where_convert_to_java__(exp,buf_dict) + "){"
                    print >>fo,"\t\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                    print >>fo,"\t\t\t\t\t}"
                else:
                    print >>fo,"\t\t\t\t\tit_output["+str(tree.it_node_list.index(x)) + "].add("+reduce_value+");"
                
                print >>fo,"\t\t\t\t}"
                print >>fo,"\t\t\t}"

### handle jfc node

    print >>fo,"\t\t\tArrayList[] jfc_output = new ArrayList[" + str(len(tree.jfc_node_list)) + "];"
    print >>fo,"\t\t\tfor(int i=0;i<"+str(len(tree.jfc_node_list))+";i++){"
    print >>fo,"\t\t\t\tjfc_output[i]=new ArrayList();"
    print >>fo,"\t\t\t}"
    for x in tree.jfc_node_list:
        if isinstance(x,ystree.GroupByNode):
            tmp_gb_input = ""
            if x.child in tree.jfc_node_list:
                index = tree.jfc_node_list.index(x.child)
                tmp_gb_input = "jfc_output["+str(index) + "]"
            elif x.child in tree.it_node_list:
                index = tree.it_node_list.index(x.child)
                tmp_gb_input = "it_output[" + str(index) + "]"
            else:
                print >>sys.stderr,"Internal Error: gen_composite"
                exit(29)

            gb_exp_list = []
            __get_gbexp_list__(x.select_list.tmp_exp_list,gb_exp_list)

            key_len = len(x.group_by_clause.groupby_exp_list)
            tmp_output_len = len(gb_exp_list)
            tmp_gb_output = "jfc_gb_output_" + str(tree.jfc_node_list.index(x))
            tmp_dc_output = "jfc_dc_output_" + str(tree.jfc_node_list.index(x))
            tmp_count_output = "jfc_count_output_" + str(tree.jfc_node_list.index(x))
            print >>fo,"\t\t\tHashtable<String,Double>[] " +tmp_gb_output + "=new Hashtable["+str(tmp_output_len) + "];"
            print >>fo,"\t\t\tHashtable<String,ArrayList>[] " +tmp_dc_output + "=new Hashtable["+str(tmp_output_len) + "];"
            print >>fo,"\t\t\tHashtable<String,Integer>[] " +tmp_count_output + "=new Hashtable["+str(tmp_output_len) + "];"
            print >>fo,"\t\t\tfor(int i=0;i<"+str(tmp_output_len) + ";i++){"
            print >>fo,"\t\t\t\t"+tmp_gb_output+"[i]=new Hashtable<String,Double>();"
            print >>fo,"\t\t\t\t"+tmp_dc_output+"[i]=new Hashtable<String,ArrayList>();"
            print >>fo,"\t\t\t\t"+tmp_count_output+"[i]=new Hashtable<String,Integer>();"
            print >>fo,"\t\t\t}"
            print >>fo,"\t\t\tfor(int i=0;i<"+tmp_gb_input + ".size();i++){"
            print >>fo,"\t\t\t\tString[] tmp_buf = ((String)"+ tmp_gb_input + ".get(i)).split(\"\\\|\");"

            tmp_key = ""
            buf_dict={}
            for tn in x.table_list:
                buf_dict[tn] = "tmp_buf"

            for i in range(0,len(x.group_by_clause.groupby_exp_list)):
                tmp_key += "tmp_buf[" + str(i) + "]+"
                tmp_key += "\"|\"+"
            tmp_key = tmp_key[:-1]

            for i in range(0,len(gb_exp_list)):
                exp = gb_exp_list[i]

                func_name = ystree.__groupby_func_name__(exp)
                if func_name == "MAX":
                    tmp = __select_func_convert_to_java__(exp,buf_dict)
                    print >>fo,"\t\t\t\tif(" + tmp_gb_output + "["+str(i)+"].containsKey("+tmp_key + ")){"
                    print >>fo,"\t\t\t\t\tDouble max_tmp = (double)" + tmp  + ";"
                    print >>fo,"\t\t\t\t\tif(max_tmp > "+tmp_gb_output+"["+str(i)+"].get("+tmp_key+"))"
                    print >>fo,"\t\t\t\t\t\t"+tmp_gb_output+"["+str(i)+"].put("+tmp_key+",max_tmp);"
                    print >>fo,"\t\t\t\t}else{"
                    print >>fo,"\t\t\t\t\t" + tmp_gb_output+"["+str(i)+"].put("+tmp_key+",(double)" + tmp + ");"
                    print >>fo,"\t\t\t\t}"
                elif func_name == "MIN":
                    tmp = __select_func_convert_to_java__(exp,buf_dict)
                    print >>fo,"\t\t\t\tif(" + tmp_gb_output + "["+str(i)+"].containsKey("+tmp_key + ")){"
                    print >>fo,"\t\t\t\t\tDouble min_tmp = (double)"+tmp +";"
                    print >>fo,"\t\t\t\t\tif(min_tmp < "+tmp_gb_output+"["+str(i)+"].get("+tmp_key+"))"
                    print >>fo,"\t\t\t\t\t\t"+tmp_gb_output+"["+str(i)+"].put("+tmp_key+",min_tmp);"
                    print >>fo,"\t\t\t\t}else{"
                    print >>fo,"\t\t\t\t\t" + tmp_gb_output+"["+str(i)+"].put("+tmp_key+",(double)"+tmp + ");"
                    print >>fo,"\t\t\t\t}"
                elif func_name == "SUM": 
                    tmp = __select_func_convert_to_java__(exp,buf_dict)
                    print >>fo,"\t\t\t\tif(" + tmp_gb_output + "["+str(i)+"].containsKey("+tmp_key + ")){"
                    print >>fo,"\t\t\t\t\tDouble sum_tmp = (double)"+tmp+";"
                    print >>fo,"\t\t\t\t\t sum_tmp += " +tmp_gb_output+"[" +str(i)+"].get("+tmp_key+");"
                    print >>fo,"\t\t\t\t\t"+tmp_gb_output+"["+str(i)+"].put("+tmp_key+", sum_tmp);"
                    print >>fo,"\t\t\t\t}else{"
                    print >>fo,"\t\t\t\t\t" + tmp_gb_output+"["+str(i)+"].put("+tmp_key+",(double)"+tmp+");";
                    print >>fo,"\t\t\t\t}"
                elif func_name == "AVG":
                    tmp = __select_func_convert_to_java__(exp,buf_dict)
                    print >>fo,"\t\t\t\tif(" + tmp_gb_output + "["+str(i)+"].containsKey("+tmp_key + ")){"
                    print >>fo,"\t\t\t\t\tDouble sum_tmp = (double)"+tmp+";"
                    print >>fo,"\t\t\t\t\tsum_tmp += " +tmp_gb_output+"[" +str(i)+"].get("+tmp_key+");"
                    print >>fo,"\t\t\t\t\tInteger count = "+tmp_count_output+"["+str(i)+"].get("+tmp_key+")+1;"
                    print >>fo,"\t\t\t\t\t"+tmp_count_output+"["+str(i)+"].put("+tmp_key+",count);"
                    print >>fo,"\t\t\t\t\t"+tmp_gb_output+"["+str(i)+"].put("+tmp_key+", sum_tmp);"
                    print >>fo,"\t\t\t\t}else{"
                    print >>fo,"\t\t\t\t\t" + tmp_gb_output+"["+str(i)+"].put("+tmp_key+",(double)"+tmp+");"
                    print >>fo,"\t\t\t\t\t"+tmp_count_output+"["+str(i)+"].put("+tmp_key+",1);"
                    print >>fo,"\t\t\t\t}"
                    print >>fo,"\t\t\t\t\t"+tmp_count_output+"["+tmp_key+"] += 1;"
                    print >>fo,"\t\t\t\t\t"+tmp_count_output+"["+tmp_key+"] = 1;"
                elif func_name == "COUNT_DISTINCT":
                    tmp = __select_func_convert_to_java__(exp,buf_dict)
                    print >>fo,"\t\t\t\tif(" + tmp_dc_output +"["+str(i)+"].containsKey(" + tmp_key + ")){"
                    print >>fo,"\t\t\t\t\tif(!"+tmp_dc_output+"["+str(i)+"].get("+tmp_key+").contains("+tmp+")){"
                    print >>fo,"\t\t\t\t\t\tArrayList tmp_al = "+tmp_dc_output + "["+str(i)+"].get("+tmp_key+").add("+tmp+");"
                    print >>fo,"\t\t\t\t\t\t"+tmp_dc_output+"["+str(i)+"].put("+tmp_key+",tmp_al);"
                    print >>fo,"\t\t\t\t\t}"
                    print >>fo,"\t\t\t\t}else{"
                    print >>fo,"\t\t\t\t\t\t"+tmp_dc_output+"["+str(i)+"].put("+tmp_key+","+tmp + ");"
                    print >>fo,"\t\t\t\t}"
                elif func_name == "COUNT":
                    print >>fo,"\t\t\t\tif(" + tmp_count_output +"["+str(i)+ "].containsKey("+tmp_key + ")){"
                    print >>fo,"\t\t\t\t\tInteger count = "+tmp_count_output+"["+str(i)+"].get("+tmp_key+")+1;"
                    print >>fo,"\t\t\t\t\t"+tmp_count_output+"["+str(i)+"].put("+tmp_key+",count);"
                    print >>fo,"\t\t\t\t}else{"
                    print >>fo,"\t\t\t\t\t"+tmp_count_output+"["+str(i)+"].put("+tmp_key+",1);"
                    print >>fo,"\t\t\t\t}"

            print >>fo,"\t\t\t}" ########## end of for 

            for i in range(0,len(gb_exp_list)):
                exp = gb_exp_list[i]

                func_name = ystree.__groupby_func_name__(exp)
                if func_name == "AVG":
                    print >>fo,"\t\t\tfor(Object tmp_key:"+tmp_gb_output+"["+str(i) + "].keySet()){"
                    print >>fo,"\t\t\t\tDouble count = (double) "+tmp_count_output+"["+str(i)+"].get(tmp_key);"
                    print >>fo,"\t\t\t\tDouble avg = "+tmp_gb_output+"["+str(i) + "].get(tmp_key)/count;"
                    print >>fo,"\t\t\t\t"+tmp_gb_output+"["+str(i)+"].put(tmp_key.toString(),avg);"
                    print >>fo,"\t\t\t}"

                elif func_name == "COUNT_DISTINCT":
                    print >>fo,"\t\t\tfor(Object tmp_key:" + tmp_dc_output+"["+str(i) +"].keySet()){"
                    print >>fo,"\t\t\t\tDouble count = (double)"+tmp_dc_output+"["+str(i)+"].get(tmp_key).size();"
                    print >>fo,"\t\t\t\t"+tmp_gb_output +"["+str(i)+"].put(tmp_key.toString(),count);"
                    print >>fo,"\t\t\t}"
                elif func_name == "COUNT":
                    print >>fo,"\t\t\tfor(Object tmp_key:" + tmp_count_output+"["+str(i) +"].keySet()){"
                    print >>fo,"\t\t\t\tDouble count = (double)"+tmp_count_output+"["+str(i)+"].get(tmp_key);"
                    print >>fo,"\t\t\t\t"+tmp_gb_output +"["+str(i)+"].put(tmp_key.toString(),count);"
                    print >>fo,"\t\t\t}"

            print >>fo,"\t\t\tfor(Object tmp_key:"+tmp_gb_output+"[0].keySet()){"
            print >>fo,"\t\t\t\tString[] tmp_buf =((String) "+tmp_gb_input + ".get(0)).split(\"\\\|\");"
            print >>fo,"\t\t\t\tfor(int i=0;i<"+tmp_gb_input+".size();i++){"
            print >>fo,"\t\t\t\t\ttmp_buf =((String) "+tmp_gb_input + ".get(i)).split(\"\\\|\");"
            print >>fo,"\t\t\t\t\tif(((String)tmp_key).compareTo("+tmp_key+")==0)"
            print >>fo,"\t\t\t\t\t\tbreak;"
            print >>fo,"\t\t\t\t}"
            buf_dict={}
            for tn in x.table_list:
                buf_dict[tn] = "tmp_buf"
            print >>fo,"\t\t\t\tString tmp_result = \"\";"
            print >>fo,"\t\t\t\tString gb_key = (String)tmp_key;"

            col_list = []
            if x.having_clause is not None:
                ystree.__get_gb_list__(tree.having_clause.where_condition_exp,col_list)

            having_len = len(col_list)

            for i in range(0,len(x.select_list.tmp_exp_list)-having_len):
                exp = x.select_list.tmp_exp_list[i]
                if ystree.__groupby_func_name__(exp) not in agg_func_list:
                    if isinstance(exp,ystree.YRawColExp):
                        tmp_exp = "tmp_buf["+str(exp.column_name) + "]"
                    elif isinstance(exp,ystree.YFuncExp):
                        tmp_exp = __select_func_convert_to_java__(exp,buf_dict)
                        tmp_exp += ".toString()"
                    elif isinstance(exp,ystree.YConsExp):
                        tmp_exp = "\""
                        tmp_exp += __para_to_java__(exp.cons_type,exp.cons_value,None)
                        tmp_exp += "\""

                    print >>fo,"\t\t\t\ttmp_result = tmp_result.concat("+tmp_exp+");"
                    print >>fo,"\t\t\t\ttmp_result = tmp_result.concat(\"|\");"

                else :### groupby exp
                    buf_dict["AGG"] = tmp_gb_output
                    tmp_result = __gb_exp_to_java__(exp,gb_exp_list,buf_dict,"gb_key")
                    print >>fo,"\t\t\t\ttmp_result = tmp_result.concat("+tmp_result+"+\"\");"
                    print >>fo,"\t\t\t\ttmp_result = tmp_result.concat(\"|\");"

            if x.where_condition is not None:
                tmp_list = []
                __get_gb_exp__(x.where_condition.where_condition_exp,tmp_list)
                for tmp in tmp_list:
                    for exp in gb_exp_list:
                        if tmp.compare(exp) is True:
                            func_obj = tmp.func_obj
                            exp_index = gb_exp_list.index(exp)
                            new_exp = ystree.YRawColExp("AGG",exp_index)
                            new_exp.column_name = int(new_exp.column_name)
                            new_exp.column_type = tmp.get_value_type()
                            func_obj.replace(tmp,new_exp)
                            break

                buf_dict = {}
                buf_dict["AGG"] = tmp_gb_output
                for x in tree.table_list:
                    buf_dict[x] = "tmp_buf"

                print >>fo,"\t\t\t\t" + __where_convert_to_java__(x.where_condition.where_condition_exp,buf_dict)+ "){\n"
                print >>fo,"\t\t\t\tjfc_output[" + str(tree.jfc_node_list.index(x)) + "].add(tmp_result);"
                print >>fo,"\t\t\t\t}"
            else:
                print >>fo,"\t\t\t\tjfc_output[" + str(tree.jfc_node_list.index(x)) + "].add(tmp_result);"

            print >>fo,"\t\t\t}"

        elif isinstance(x,ystree.TwoJoinNode):
            jfc_left_buf = "jfc_left_buf"
            jfc_right_buf = "jfc_right_buf"
            tmp_left_buf = jfc_left_buf+"_"+str(tree.jfc_node_list.index(x)) 
            tmp_right_buf = jfc_right_buf+"_"+str(tree.jfc_node_list.index(x)) 
            buf_dict["LEFT"] = tmp_left_buf
            buf_dict["RIGHT"] = tmp_right_buf
            reduce_value_type = "Text"

            if x.left_child in tree.it_node_list:
                left_index = tree.it_node_list.index(x.left_child)
                left_input = "it_output[" + str(left_index) + "]"
            elif x.left_child in tree.jfc_node_list:
                left_index = tree.jfc_node_list.index(x.left_child)
                left_input = "jfc_output[" + str(left_index) + "]"
            elif isinstance(x.left_child,ystree.TableNode):
                left_index = tree.it_node_list.index(x)
                left_input = left_array + "_" + str(left_index)
            else:
                print >>sys.stderr,"Internal Error: gen_composite"
                exit(29)

            if x.right_child in tree.it_node_list:
                right_index = tree.it_node_list.index(x.right_child)
                right_input ="it_output[" + str(right_index) + "]"
            elif x.right_child in tree.jfc_node_list:
                right_index = tree.jfc_node_list.index(x.right_child)
                right_input ="jfc_output[" + str(right_index) + "]"
            elif isinstance(x.right_child,ystree.TableNode):
                right_index = tree.it_node_list.index(x)
                right_input = right_array + "_" + str(right_index)
            else:
                print >>sys.stderr,"Internal Error: gen_composite"
                exit(29)

            if x.join_explicit is True:
                join_type = x.join_type.upper()
                if join_type == "LEFT":
                    print >>fo,"\t\t\tfor(int i=0;i<"+left_input+".size();i++){"
                    print >>fo,"\t\t\t\tString[] "+tmp_left_buf+"=((String)"+left_input+".get(i)).split(\"\\\|\");"
                    print >>fo,"\t\t\t\tif("+right_input+".size()>0){"
                    print >>fo,"\t\t\t\t\tfor(int j=0;j<"+right_input+".size();j++){"
                    print >>fo,"\t\t\t\t\t\tString[] "+tmp_right_buf+"=((String)"+right_input+".get(j)).split(\"\\\|\");"
                    reduce_value = __gen_mr_value__(x.select_list.tmp_exp_list,reduce_value_type,buf_dict)
                    if x.where_condition is not None:
                        exp = x.where_condition.where_condition_exp
                        print >>fo,"\t\t\t\t\t\tif("+__where_convert_to_java__(exp,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t\t}"
                        print >>fo,"\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"
                    print >>fo,"\t\t\t\t}else{"
                    new_list = []
                    __gen_join_list__(x.select_list.tmp_exp_list,new_list,"LEFT")
                    reduce_value = __gen_mr_value__(new_list,reduce_value_type,buf_dict)
                    if x.where_condition is not None:
                        exp = x.where_condition.where_condition_exp
                        new_where = __gen_join_where__(exp,"LEFT")
                        print >>fo,"\t\t\t\t\tif("+__where_convert_to_java__(new_where,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"

                    print >>fo,"\t\t\t\t}"
                    print >>fo,"\t\t\t}"

                elif join_type == "RIGHT":
                    print >>fo,"\t\t\tfor(int i=0;i<"+right_input+".size();i++){"
                    print >>fo,"\t\t\t\tString[] "+tmp_right_buf+"=((String)"+right_input+".get(i)).split(\"\\\|\");"
                    print >>fo,"\t\t\t\tif("+left_input+".size()>0){"
                    print >>fo,"\t\t\t\t\tfor(int j=0;j<"+left_input+".size();j++){"
                    print >>fo,"\t\t\t\t\t\tString[] "+tmp_left_buf+"=((String)"+left_input+".get(j)).split(\"\\\|\");"
                    reduce_value = __gen_mr_value__(x.select_list.tmp_exp_list,reduce_value_type,buf_dict)
                    if x.where_condition is not None:
                        exp = x.where_condition.where_condition_exp
                        print >>fo,"\t\t\t\t\t\tif("+__where_convert_to_java__(exp,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t\t}"
                        print >>fo,"\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"
                    print >>fo,"\t\t\t\t}else{"
                    new_list = []
                    __gen_join_list__(x.select_list.tmp_exp_list,new_list,"RIGHT")
                    reduce_value = __gen_mr_value__(new_list,reduce_value_type,buf_dict)
                    if x.where_condition is not None:
                        exp = x.where_condition.where_condition_exp
                        new_where = __gen_join_where__(exp,"RIGHT")
                        print >>fo,"\t\t\t\t\tif("+__where_convert_to_java__(new_where,buf_dict)+"){"
                        print >>fo,"\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"
                        print >>fo,"\t\t\t\t\t}"
                    else:
                        print >>fo,"\t\t\t\t\t\tjfc_output["+str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"

                    print >>fo,"\t\t\t\t}"
                    print >>fo,"\t\t\t}"
                    
                else:
                    print >>sys.stderr,"Internal Error: gen_composite"
                    exit(29)
            else:
                reduce_value = __gen_mr_value__(x.select_list.tmp_exp_list,reduce_value_type,buf_dict)
                print >>fo,"\t\t\tfor(int i=0;i<"+left_input+".size();i++){"
                print >>fo,"\t\t\t\tString[] "+tmp_left_buf+" = ((String)"+left_input+".get(i)).split(\"\\\|\");"
                print >>fo,"\t\t\t\tfor(int j=0;j<"+right_input+".size();j++){"
                print >>fo,"\t\t\t\t\tString[] "+tmp_right_buf+" = ((String)"+right_input+".get(j)).split(\"\\\|\");"
                if x.where_condition is not None:
                    exp = x.where_condition.where_condition_exp
                    print >>fo,"\t\t\t\t\tif(" +__where_convert_to_java__(exp,buf_dict) + "){"
                    print >>fo,"\t\t\t\t\t\tjfc_output[" +str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"
                    print >>fo,"\t\t\t\t\t}"
                else:
                    print >>fo,"\t\t\t\t\tjfc_output[" +str(tree.jfc_node_list.index(x))+"].add("+reduce_value+");"

                print >>fo,"\t\t\t\t}"
                print >>fo,"\t\t\t}"

### generate final output

    print >>fo,"\t\t\tNullWritable key_op=NullWritable.get();"
    for x in tree.jfc_node_list:

#####fix me here: right now only one output is supported here

        if x.parent not in tree.jfc_node_list:
            print >>fo,"\t\t\tfor(int i=0;i<jfc_output["+str(tree.jfc_node_list.index(x))+"].size();i++){"
            print >>fo,"\t\t\t\tString jfc_result = (String)jfc_output["+str(tree.jfc_node_list.index(x))+"].get(i);"
            print >>fo,"\t\t\t\tcontext.write(key_op, new Text(jfc_result));"
            print >>fo,"\t\t\t}"

    print >>fo, "\t\t}\n"
    print >>fo, "\t}\n"

    __gen_main__(tree,fo,map_key_type,map_value_type,reduce_key_type,reduce_value_type,False)

    

def __gen_main__(tree,fo,map_key_type,map_value_type,reduce_key_type,reduce_value_type,reduce_bool):
    print >>fo,"\tpublic int run(String[] args) throws Exception{\n"
    jobname = fo.name.split(".java")[0]

    print >>fo, "\t\tConfiguration conf = new Configuration();"
    print >>fo, "\t\tJob job = new Job(conf,\"" + jobname + "\");"
    print >>fo, "\t\tjob.setJarByClass("+jobname + ".class);"
    print >>fo,"\t\tjob.setMapOutputKeyClass(" + map_key_type+".class);"
    print >>fo,"\t\tjob.setMapOutputValueClass(" + map_value_type+ ".class);"
    print >>fo,"\t\tjob.setOutputKeyClass("+reduce_key_type+".class);"
    print >>fo,"\t\tjob.setOutputValueClass("+reduce_value_type+".class);"
    print >>fo,"\t\tjob.setMapperClass(Map.class);"
    print >>fo,"\t\tjob.setReducerClass(Reduce.class);"
    if reduce_bool is True:
        print >>fo,"\t\tjob.setReducerClass(Reduce.class);"
    if isinstance(tree,ystree.TwoJoinNode):
        print >>fo, "\t\tFileInputFormat.addInputPath(job,new Path(args[0]));"
        print >>fo, "\t\tFileInputFormat.addInputPath(job,new Path(args[1]));"
        print >>fo,"\t\tFileOutputFormat.setOutputPath(job, new Path(args[2]));"
    elif isinstance(tree,ystree.CompositeNode):
        in_len = len(tree.mapoutput.keys())
        for i in range(0,in_len):
            print >>fo,"\t\tFileInputFormat.addInputPath(job,new Path(args["+str(i)+"]));"
        print >>fo,"\t\tFileOutputFormat.setOutputPath(job, new Path(args[" + str(in_len) + "]));";
    else:
        print >>fo,"\t\tFileInputFormat.addInputPath(job, new Path(args[0]));"
        print >>fo,"\t\tFileOutputFormat.setOutputPath(job, new Path(args[1]));"
    print >>fo,"\t\treturn (job.waitForCompletion(true) ? 0 : 1);"

    print >>fo,"\t}\n"

    print >>fo, "\tpublic static void main(String[] args) throws Exception {\n"
    print >>fo, "\t\t\tint res = ToolRunner.run(new Configuration(), new " + jobname + "(), args);"
    print >>fo, "\t\t\tSystem.exit(res);"
    print >>fo, "\t}\n"

def __tablenode_code_gen__(tree,fo):
    __gen_des__(fo)
    __gen_header__(fo)

    print >>fo,"public class "+fo.name.split(".java")[0]+" extends Configured implements Tool{\n"

    __tablenode_gen_mr__(tree,fo)

    print >>fo,"}\n"

def __orderby_code_gen__(tree,fo):
    __gen_des__(fo)
    __gen_header__(fo)

    print >>fo,"public class " +fo.name.split(".java")[0] + " extends Configured implements Tool{\n"

    __orderby_gen_mr__(tree,fo)

    print >>fo,"}\n"


def __groupby_code_gen__(tree,fo):
    __gen_des__(fo)
    __gen_header__(fo)

    print >>fo,"public class "+fo.name.split(".java")[0]+" extends Configured implements Tool{\n"

    __groupby_gen_mr__(tree,fo)

    print >>fo, "}\n"


def __join_code_gen__(tree,left_name,fo):
    __gen_des__(fo)
    __gen_header__(fo)
    print >>fo,"public class "+fo.name.split(".java")[0]+" extends Configured implements Tool{\n"

    __join_gen_mr__(tree,left_name,fo)
    print >>fo, "}\n"

def __composite_code_gen__(tree,fo):
    __gen_des__(fo)
    __gen_header__(fo)
    print >>fo,"public class "+fo.name.split(".java")[0]+" extends Configured implements Tool{\n"

    __composite_gen_mr__(tree,fo)
    print >>fo, "}\n"


def generate_code(tree,filename):

    op_name = filename + ".java"

    fo = open(op_name,"w")

    ret_name = filename
    

    if isinstance(tree,ystree.TableNode):
        __tablenode_code_gen__(tree,fo)
        return ret_name

    elif isinstance(tree,ystree.OrderByNode):
        __orderby_code_gen__(tree,fo)
        if tree.composite is None:
            if not isinstance(tree.child,ystree.TableNode):
                filename = filename[:-1] + str(int(filename[-1])+1)
                ret_name = generate_code(tree.child,filename)
        else:
            filename = filename[:-1] + str(int(filename[-1])+1)
            ret_name = generate_code(tree.composite,filename)

        return ret_name

    elif isinstance(tree,ystree.SelectProjectNode):
        ret_name = generate_code(tree.child,filename)
        return ret_name

    elif isinstance(tree,ystree.GroupByNode):
        __groupby_code_gen__(tree,fo)
        if tree.composite is None:
            if not isinstance(tree.child,ystree.TableNode):
                filename = filename[:-1] + str(int(filename[-1])+1) 
                ret_name =  generate_code(tree.child,filename)
        else:
            filename = filename[:-1] + str(int(filename[-1])+1)
            ret_name = generate_code(tree.composite,filename)

        return ret_name

    elif isinstance(tree,ystree.TwoJoinNode):
        if tree.left_composite is not None and tree.right_composite is not None:
            new_name = filename[:-1] + str(int(filename[-1])+1)
            __join_code_gen__(tree,new_name,fo)
            new_name = generate_code(tree.left_composite,new_name)

            new_name = new_name[:-1] +str(int(new_name[-1])+1)
            ret_name = generate_code(tree.right_composite,new_name)

        elif tree.left_composite is not None:
            new_name = filename[:-1]  +str(int(filename[-1])+1)
            __join_code_gen__(tree,new_name,fo)
            new_name = generate_code(tree.left_composite,new_name)
            ret_name = new_name

            if not isinstance(tree.right_child,ystree.TableNode):
                new_name = new_name[:-1]  + str(int(new_name[-1])+1)
                ret_name = generate_code(tree.right_child,new_name)

        elif tree.right_composite is not None:
            if not isinstance(tree.left_child,ystree.TableNode):
                new_name = filename[:-1] +str(int(filename[-1])+1)
                __join_code_gen__(tree,new_name,fo)
                new_name = generate_code(tree.left_child,new_name)
            else:
                new_name = filename

            new_name = new_name[:-1]  +str(int(new_name[-1])+1)
            ret_name = generate_code(tree.right_composite,new_name)

        else:
            if not isinstance(tree.left_child,ystree.TableNode):
                new_name = filename[:-1]  +str(int(filename[-1])+1)
                __join_code_gen__(tree,new_name,fo)
                ret_name = generate_code(tree.left_child,new_name)

            else:
                ret_name = filename
                __join_code_gen__(tree,tree.left_child.table_name,fo)

            if not isinstance(tree.right_child,ystree.TableNode):
                new_name = ret_name[:-1] + str(int(ret_name[-1])+1)
                ret_name = generate_code(tree.right_child,new_name)

        return ret_name

    elif isinstance(tree,ystree.CompositeNode):
        __composite_code_gen__(tree,fo)

        if len(tree.child_list) > 0:
            i=int(filename[-1]) +1
            for x in tree.child_list:
                if isinstance(x,ystree.TableNode):
                    continue
                new_name = filename[:-1]+str(i)
                new_name = generate_code(x,new_name)
                ret_name = new_name
                i = i+1

        return ret_name

    fo.close()

def compile_class(tree,codedir,package_path,filename,fo):

    version = "0.21.0"
    if "HADOOP_HOME" in os.environ:
        version = commands.getoutput("$HADOOP_HOME/bin/hadoop version").split("\n")[0].split(" ")[1]

    cmd = "javac -classpath $HADOOP_HOME/hadoop-common-"+version+".jar:$HADOOP_HOME/hadoop-hdfs-"+version+".jar:$HADOOP_HOME/hadoop-mapred-"+version+".jar " 
    cmd += codedir + "/*.java -d ." 
    print >>fo,cmd
    if config.compile_jar is True:
        os.system(cmd)

def generate_jar(jardir,path,filename,fo):
    cmd = "jar -cf " +jardir + "/"+ filename + ".jar " + path
    print >>fo,cmd
    if config.compile_jar is True:
        os.system(cmd)


def execute_jar(tree,jardir,jarname,classname,input_path,output_path,fo):

    ret_name = classname
    
    if isinstance(tree,ystree.TableNode):
        cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath + classname + " "  + input_path + "/" + tree.table_name + "/" 
        cmd += " " + output_path + "/" + tree.table_name + "/" 
        print >>fo, cmd
        if config.compile_jar is True and config.exec_jar is True:
            os.system(cmd)

    elif isinstance(tree,ystree.OrderByNode):
        if not isinstance(tree.child,ystree.TableNode):
            new_name = classname[:-1] + str(int(classname[-1])+1)
            if tree.composite is not None:
                ret_name = execute_jar(tree.composite,jardir,jarname,new_name,input_path,output_path,fo)
            else:
                ret_name = execute_jar(tree.child,jardir,jarname,new_name,input_path,output_path,fo)
            cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + output_path + "/" + new_name
            cmd += " " + output_path + "/" + classname + "/"
        else:
            cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + input_path + "/" + tree.child.table_name + "/"
            cmd += " " + output_path + "/" + classname + "/"

        print >>fo,cmd
        if config.compile_jar is True and config.exec_jar is True:
            os.system(cmd)

    elif isinstance(tree,ystree.SelectProjectNode):
        ret_name = execute_jar(tree.child,jardir,jarname,classname,input_path,output_path,fo)

    elif isinstance(tree,ystree.GroupByNode):
        if not isinstance(tree.child,ystree.TableNode):
            new_name = classname[:-1] + str(int(classname[-1])+1)
            if tree.composite is not None:
                ret_name = execute_jar(tree.composite,jardir,jarname,new_name,input_path,output_path,fo)
            else:
                ret_name = execute_jar(tree.child,jardir,jarname,new_name,input_path,output_path,fo)
            cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath + classname + " " + output_path + "/" + new_name
            cmd += " " + output_path + "/" + classname + "/"
        else:
            cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath + classname + " " + input_path + "/" + tree.child.table_name + "/" 
            cmd += " " + output_path + "/" + classname + "/"
        print >>fo,cmd
        if config.compile_jar is True and config.exec_jar is True:
            os.system(cmd)

    elif isinstance(tree,ystree.TwoJoinNode):
        cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + input_path + "/"
        if not isinstance(tree.left_child,ystree.TableNode):
            new_name = classname[:-1] + str(int(classname[-1])+1)
            if tree.left_composite is not None:
                ret_name = execute_jar(tree.left_composite,jardir,jarname,new_name,input_path,output_path,fo)
            else:
                ret_name = execute_jar(tree.left_child,jardir,jarname,new_name,input_path,output_path,fo)
            cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + output_path + "/"
            cmd += new_name + "/"
        else:
            cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath +classname + " " + input_path + "/"
            cmd += tree.left_child.table_name + "/"
            ret_name = classname

        if not isinstance(tree.right_child,ystree.TableNode):
            new_name = ret_name[:-1]  + str(int(ret_name[-1])+1)
            if tree.right_composite is not None:
                ret_name = execute_jar(tree.right_composite,jardir,jarname,new_name,input_path,output_path,fo)
            else:
                ret_name = execute_jar(tree.right_child,jardir,jarname,new_name,input_path,output_path,fo)
            cmd += " " + output_path + "/"
            cmd += new_name + "/"
        else:
            cmd += " " + input_path + "/"
            cmd += tree.right_child.table_name + "/"

        cmd += " " + output_path + "/" + classname + "/"
        print >>fo,cmd
        if config.compile_jar is True and config.exec_jar is True:
            os.system(cmd)

    elif isinstance(tree,ystree.CompositeNode):
        child_list = []
        new_name = classname[:-1] + str(int(classname[-1])+1)
        child_list.append(new_name)
        cmd = "$HADOOP_HOME/bin/hadoop jar " + jardir + "/" + jarname + ".jar " + packagepath + classname + " " 
        for node in tree.child_list:
            ret_name = execute_jar(node,jardir,jarname,new_name,input_path,output_path,fo)
            new_name = ret_name[:-1] + str(int(new_name[-1])+1)
            child_list.append(new_name)

        for tn in tree.mapoutput.keys():
            if tn in child_list:
                cmd += output_path + "/" + tn + " "
            else:
                cmd += input_path + "/" + tn + " "

        cmd += output_path + "/" + classname

        print >>fo,cmd
        if config.compile_jar is True and config.exec_jar is True:
            os.system(cmd)

    return ret_name


def ysmart_code_gen(argv,input_path,output_path):
    pwd = os.getcwd()
    resultdir = "./result"
    codedir = "./YSmartCode"
    jardir = "./YSmartJar"

    global packagepath
    global packagename

    
    tree_node = ystree.ysmart_tree_gen(argv[1],argv[2])

    if config.turn_on_correlation is True:
        tree_node = correlation.ysmart_correlation(tree_node)
    
    if tree_node is None:
        exit(-1)

    if os.path.exists(resultdir) is False:
        os.makedirs(resultdir)

    os.chdir(resultdir)
    if os.path.exists(codedir) or os.path.exists(jardir):
        pass

    else:
        os.makedirs(codedir)
        os.makedirs(jardir)

    packagepath += config.queryname + "/"
    packagename += "." + config.queryname
    config.queryname += "1"
        

    os.chdir(codedir)   
    
    generate_code(tree_node,config.queryname)

    os.chdir(pwd)

    os.chdir(resultdir)

    fo = open(config.scriptname,'w')
    compile_class(tree_node,codedir,packagepath,config.queryname,fo)
    generate_jar(jardir,packagepath,config.queryname,fo)

    execute_jar(tree_node,jardir,config.queryname,config.queryname,input_path,output_path,fo)

    os.chdir(pwd)


