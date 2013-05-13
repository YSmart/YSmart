'''
The frontend of YSmart. Takes an SQL query file and generates an XML representation of it.
Created on May 6, 2013

@author: Meisam
'''

import sys
import antlr3
import antlr3.tree
from YSmartPythonishLexer import *
from YSmartPythonishParser import *


def toXml(sqlFile):
    '''
    parses the contents of the given file and returns a string that represents the AST in xml format 
    '''
    with sqlFile:
        # TODO Meisam: Make the grammar case insensitive?
        query = sqlFile.read().upper()
        stringStream = antlr3.StringStream(query)
        lexer = YSmartPythonishLexer(stringStream)
        
        tokenStream = antlr3.CommonTokenStream(lexer)
        
        parser = YSmartPythonishParser(tokenStream)
        
        parseTree = parser.start_rule()
        
        return traverseTree(parseTree.tree)
    
def traverseTree(tree):
    '''
    traverses the given tree to create an XML string  
    '''
    isRoot = False

    xmlStr = ""
    if tree is None:
        return  xmlStr
    
    elif tree.token is None: # this is the root node of the SQL query
        xmlStr += '<query>\n'
        # TODO Meisam: change this to a method parameter?
        isRoot = True
    
    for child in tree.children:
        token = child.token
        type = token.getType()
        name = YSmartPythonishParser.tokenNames[type]
        line = child.getLine()
        position = child.getCharPositionInLine()
        childCount = len(child.children)
        
        xmlStr = xmlStr + ('<node tokentype="%d" tokenname="%s" line="%d" positioninline="%d" childcount="%d">\n' % (type, name, line, position, childCount))
        
        content = str(child)
        
        xmlStr += ('<content>%s</content>\n' % escapeXmlCharacters(content));
                
        xmlStr += traverseTree(child)
        xmlStr += '</node>'
    
    if isRoot:
        xmlStr += '</query>\n'
        
    return xmlStr

#TODO Meisam: This should be escaped to XML characters
def escapeXmlCharacters(rawString):
    return rawString.replace(">", "?").replace("<", "?")

if __name__ == '__main__':
    pass
