#!/usr/bin/env python

"""
   Copyright (c) 2013 The Ohio State University.

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

'''
Testcases for YSmart front end
Created on May 7, 2013

@author: fathi
'''
import sys
sys.path.append("..")
sys.path.append("../SQL2XML")
 
from YSmartLexer import *  # import all the tokens
from YSmartParser import *
from antlr3.tokens import CommonToken

import antlr3
import unittest
from sql2xml import toXml

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testYsmartLexer(self):
        query = "SELECT a FROM b".upper()
        cStream = antlr3.StringStream(query)
        lexer = YSmartLexer(cStream)
        
        token = lexer.next();
        self.assertEqual(token.text, "SELECT", "Token text do not match")

        token = lexer.next();
        self.assertEqual(token.text, " ", "Token text do not match")

        token = lexer.next();
        self.assertEqual(token.text, "A", "Token text do not match")

        token = lexer.next();
        self.assertEqual(token.text, " ", "Token text do not match")

        token = lexer.next();
        self.assertEqual(token.text, "FROM", "Token text do not match")

        token = lexer.next();
        self.assertEqual(token.text, " ", "Token text do not match")

        token = lexer.next();
        self.assertEqual(token.text, "B", "Token text do not match")

        pass

    def testTpch1Parser(self):
        self.sql2XmlTestScaffold("tpch_test/1.sql") 

    def testTpch10Parser(self):
        self.sql2XmlTestScaffold("tpch_test/10.sql") 

    def testTpch17Parser(self):
        self.sql2XmlTestScaffold("tpch_test/17.sql") 

    def testTpch18Parser(self):
        self.sql2XmlTestScaffold("tpch_test/18.sql") 

    def testTpch21Parser(self):
        self.sql2XmlTestScaffold("tpch_test/21.sql") 

    def testTpch3Parser(self):
        self.sql2XmlTestScaffold("tpch_test/3.sql") 

    def testTpch5Parser(self):
        self.sql2XmlTestScaffold("tpch_test/5.sql") 

    def testTpch6Parser(self):
        self.sql2XmlTestScaffold("tpch_test/6.sql") 

    def testSSb1_1Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q1_1.sql") 

    def testSSb1_2Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q1_2.sql") 

    def testSSb1_3Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q1_3.sql") 

    def testSSb2_1Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q2_1.sql") 

    def testSSb2_2Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q2_2.sql") 

    def testSSb2_3Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q2_3.sql") 

    def testSSb3_1Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q3_1.sql") 

    def testSSb3_2Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q3_2.sql") 

    def testSSb3_3Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q3_3.sql") 

    def testSSb4_4Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q3_4.sql") 

    def testSSb4_1Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q4_1.sql") 

    def testSSb4_2Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q4_2.sql") 

    def testSSb4_3Parser(self):
        self.sql2XmlTestScaffold("ssb_test/q4_3.sql") 


    def sql2XmlTestScaffold(self, inputFileName):
        '''
        Parses the given SQL file and compares the parse tree with the expected parse tree
        '''
        errorMsg = """Expected output and produced output do not match for %s:
                         Expected output: %s
                         ---------------------------------------------------------------
                         Produced output: %s
                         ==============================================================="""
        producedXml = toXml(open(inputFileName)).upper()
        
        expectedXml = open(inputFileName + ".xml").read().upper()
        self.assertEqual(expectedXml, producedXml, errorMsg % (inputFileName, expectedXml, producedXml))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testParser']
    unittest.main()
