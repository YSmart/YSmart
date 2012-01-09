/*
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

/*************************************************************************/
// The program is used to convert an SQL file to an XML file.            //
//                                                                       //
// Usage: ./YSmartFront.exe input_sql_file > ouput_xml_file                   //
//                                                                       //
// Authors: Rubao Lee liru@cse.ohio-state.edu                            //
//          Yuan Yuan yuanyu@cse.ohio-state.edu                          //
//          Yin Huai  huai@cse.ohio-state.edu                            //
// Time: 11-30-2011                                                      //
/*************************************************************************/

/**************************************************************************/
//                                                                        //
// The program is based on an existing tree parser program.               //
// The original authors are cited as follows.                             //
//                                                                        //
/**************************************************************************/
// Example of a grammar for a trivial tree parser.
// Adapted from Java equivalent example, by Terence Parr
// Author: Jim Idle - April 2007
// Permission is granted to use this example code in any way you want, so long as
// all the original authors are cited.
/***************************************************************************/



#include "YSmartLexer.h"
#include "YSmartParser.h"


extern pANTLR3_UINT8  YSmartParserTokenNames[];


void xml_escape_string(char *oldstr, char* newstr)
{

	char c;

	while(c = *oldstr++){

		if (c == '<' || c == '>'){
			*newstr++ = '?';
		}
		else{
			*newstr++ = c;
		}

	}

}

void TreeWalkWorkerXML(pANTLR3_BASE_TREE p, int Level)
{

	ANTLR3_UINT32   n, c;

	int isNilNode = 0;
	
	if  (p->isNilNode(p) == ANTLR3_TRUE) {
		printf("<query>\n");
		isNilNode  = 1;
	}

	n = p->getChildCount(p);

	for  (c = 0; c<n ; c++) {
		pANTLR3_BASE_TREE   child;
		child = p->getChild(p, c);

		int ChildCount = child->getChildCount(child);
		pANTLR3_COMMON_TOKEN Token;
		if (child->getToken == NULL) {
			printf("// getToken null\n");
			Token = 0;
		} else {
			Token = child->getToken(child);
		}


		ANTLR3_UINT32 TokenType = child->getType(child);

		char *s = child->toString(child)->chars;

		printf("<node tokentype=\"%d\" tokenname=\"%s\" line=\"%d\" positioninline=\"%d\" childcount=\"%d\">\n",
		       TokenType,
		       YSmartParserTokenNames[TokenType],
		       child->getLine(child),
		       child->getCharPositionInLine(child),
		       child->getChildCount(child)
			);

		char* newstr = (char *)malloc(1024);
		memset(newstr, 0, 1024);
		xml_escape_string(child->toString(child)->chars, newstr);
		printf("<content>%s</content>\n", newstr);
		free(newstr);

		if (ChildCount > 0) {
			TreeWalkWorkerXML(child, Level+1);
		}
		printf("</node>");
	}


	if(isNilNode){
		printf("</query>\n");

	}


};

void TreeWalk(pANTLR3_BASE_TREE p)
{
	TreeWalkWorkerXML(p, 0);
};


int ANTLR3_CDECL main(int argc, char *argv[])
{
	int retval;
  
	pANTLR3_UINT8 fName;

	pANTLR3_INPUT_STREAM input;

	pYSmartLexer lxr;

	pANTLR3_COMMON_TOKEN_STREAM tstream;

	pYSmartParser psr;

	YSmartParser_start_rule_return langAST;

	pANTLR3_COMMON_TREE_NODE_STREAM	nodes;

	if (argc < 2)
	{
		fprintf(stderr, "You must give me the SQL file name!\n");
		exit(1);
	}
	else
	{
		fName	= (pANTLR3_UINT8)argv[1];
	}

	
	fprintf(stderr, "%s\n", (char *)fName);

	input	= antlr3AsciiFileStreamNew(fName);
	input->setUcaseLA(input, ANTLR3_TRUE); 

	if (input == NULL)
	{
		fprintf(stderr, "Unable to open file %s\n", (char *)fName);
		exit(ANTLR3_ERR_NOMEM);
	}

	lxr = YSmartLexerNew(input);	    
	lxr->pLexer->input->charPositionInLine = 0;

	if ( lxr == NULL )
	{
		fprintf(stderr, "Unable to create the lexer due to malloc() failure1\n");
		exit(ANTLR3_ERR_NOMEM);
	}

	tstream = antlr3CommonTokenStreamSourceNew(ANTLR3_SIZE_HINT, TOKENSOURCE(lxr));

	if (tstream == NULL)
	{
		fprintf(stderr, "Out of memory trying to allocate token stream\n");
		exit(ANTLR3_ERR_NOMEM);
	}


	psr = YSmartParserNew(tstream);

	if (psr == NULL)
	{
		fprintf(stderr, "Out of memory trying to allocate parser\n");
		exit(ANTLR3_ERR_NOMEM);
	}

	langAST = psr->start_rule(psr);

	if (psr->pParser->rec->state->errorCount > 0)
	{
		fprintf(stderr, "The parser returned %d errors, tree walking aborted.\n", psr->pParser->rec->state->errorCount);

	}
	else
	{
		nodes = antlr3CommonTreeNodeStreamNewTree(langAST.tree, ANTLR3_SIZE_HINT); 

		nodes->free  (nodes);	    
		nodes  = NULL;
	}


	TreeWalk(langAST.tree);	


	retval = psr->pParser->rec->state->errorCount;
	
	psr->free  (psr);		
	psr = NULL;
	tstream ->free  (tstream);	
	tstream	= NULL;
	lxr->free  (lxr);	    
	lxr = NULL;
	input->close (input);	
	input = NULL;

	return retval;
};



