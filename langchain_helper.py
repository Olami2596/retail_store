from langchain_groq import ChatGroq 
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import SemanticSimilarityExampleSelector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import FewShotPromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain.prompts.prompt import PromptTemplate

from few_shots import few_shots

import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.error(f"Error loading environment variables: {str(e)}")
    raise

def get_few_shot_db_chain():
    """
    Create and return a few-shot learning database chain with proper error handling.
    """
    try:
        # Database connection parameters
        db_user = "root"
        db_password = "MTeejay_2596"
        db_host = "localhost"
        db_name = "atliq_tshirts"
        
        # Connect to the database
        try:
            db = SQLDatabase.from_uri(
                f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
                sample_rows_in_table_info=3
            )
            logger.info("Successfully connected to the database")
        except Exception as db_error:
            logger.error(f"Database connection error: {str(db_error)}")
            raise Exception(f"Failed to connect to database: {str(db_error)}")
        
        # Initialize the LLM
        try:
            llm = ChatGroq(
                model_name="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=500
            )
            logger.info("LLM initialized successfully")
        except Exception as llm_error:
            logger.error(f"LLM initialization error: {str(llm_error)}")
            raise Exception(f"Failed to initialize LLM: {str(llm_error)}")
        
        # Create embeddings and vectorstore
        try:
            embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
            to_vectorize = [" ".join(example.values()) for example in few_shots]
            vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=few_shots)
            logger.info("Embeddings and vectorstore created successfully")
        except Exception as embed_error:
            logger.error(f"Embeddings/vectorstore error: {str(embed_error)}")
            raise Exception(f"Failed to create embeddings or vectorstore: {str(embed_error)}")
        
        # Set up example selector and prompts
        try:
            example_selector = SemanticSimilarityExampleSelector(
                vectorstore=vectorstore,
                k=2,
            )
            
            mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer to the input question.
            Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL. You can order the results to return the most informative data in the database.
            Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
            Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
            Pay attention to use CURDATE() function to get the current date, if the question involves "today".
            
            Use the following format:
            
            Question: Question here
            SQLQuery: Query to run with no pre-amble
            SQLResult: Result of the SQLQuery
            Answer: Final answer here
            
            No pre-amble.
            """

            example_prompt = PromptTemplate(
                input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
                template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
            )

            few_shot_prompt = FewShotPromptTemplate(
                example_selector=example_selector,
                example_prompt=example_prompt,
                prefix=mysql_prompt,
                suffix=PROMPT_SUFFIX,
                input_variables=["input", "table_info", "top_k"],
            )
            logger.info("Prompt templates created successfully")
        except Exception as prompt_error:
            logger.error(f"Prompt template error: {str(prompt_error)}")
            raise Exception(f"Failed to create prompt templates: {str(prompt_error)}")
        
        # Create and return the chain
        try:
            chain = SQLDatabaseChain.from_llm(
                llm, 
                db, 
                verbose=True,
                return_direct=True, 
                prompt=few_shot_prompt
            )
            logger.info("Database chain created successfully")
            return chain
        except Exception as chain_error:
            logger.error(f"Chain creation error: {str(chain_error)}")
            raise Exception(f"Failed to create database chain: {str(chain_error)}")
            
    except Exception as e:
        logger.error(f"Unexpected error in get_few_shot_db_chain: {str(e)}")
        raise