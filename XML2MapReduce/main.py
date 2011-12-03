#!/usr/bin/python

import sys
import code_gen
import config

if __name__ == '__main__':

    if len(sys.argv) !=6: 
        exit(-1)

    config.queryname = sys.argv[3]
    config.scriptname = config.queryname + ".script"
    config.input_path = sys.argv[4]
    config.output_path = sys.argv[5]

    code_gen.ysmart_code_gen(sys.argv,config.input_path,config.output_path)

