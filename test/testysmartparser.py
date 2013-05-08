'''
Created on May 7, 2013

@author: fathi
'''
import unittest
import antlr3
from YSmartPythonishLexer import YSmartPythonishLexer
from YSmartPythonishLexer import *  # import all the tokens 

from antlr3.tokens import CommonToken


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testYsmartLexer(self):
        query = "SELECT a FROM b".upper()
        cStream = antlr3.StringStream(query)
        lexer = YSmartPythonishLexer(cStream)
        
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

    def testSbbQuery1_1Lexer(self):
        with open("ssb_test/q1_1.sql") as f:
            query = f.read().upper()
            cStream = antlr3.StringStream(query)
            lexer = YSmartPythonishLexer(cStream)
            for t in lexer:
                print "Token %s" % t.text
                
            pass

    def testTpch1Lexer(self):
        with open("tpch_test/1.sql") as f:
            query = f.read().upper()
            cStream = antlr3.StringStream(query)
            lexer = YSmartPythonishLexer(cStream)
            for t in lexer:
                print "Token %s" % t.text
                
            pass
        self.fail("Lets fail")

    def testBasicParser(self):
        pass
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testParser']
    unittest.main()
