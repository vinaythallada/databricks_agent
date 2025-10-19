import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# LangChain and its components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain

class SQLQueryOutput(BaseModel):
    """Structured model for SQL query output from LLM."""
    sql_query: str = Field(
        description="A clean SQL query string without extra formatting, using catalog.schema.table_name.")

    @field_validator("sql_query")
    def remove_trailing_semicolon(cls, v: str) -> str:
        # Pydantic validation: Cleans up the query string
        return v.rstrip().rstrip(';').rstrip()


class DatabricksLLMClient:
    # -------------------------------------------------------------------------
    # Initialization and Setup
    # -------------------------------------------------------------------------
    def __init__(self, env_path: str):
        """Initialize the Databricks LLM Client by loading environment variables."""
        load_dotenv(dotenv_path=Path(env_path))

        # Load Databricks credentials
        self.host = os.getenv("DATABRICKS_SERVER_HOSTNAME").strip("https://")
        self.token = os.getenv("DATABRICKS_ACCESS_TOKEN")
        self.catalog = os.getenv("DATABRICKS_CATALOG")
        self.schema = os.getenv("DATABRICKS_SCHEMA")
        self.warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")

        # Initialize LangChain's ChatGoogleGenerativeAI
        self.model = "gemini-2.5-flash"
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            temperature=0.0,
            # LangChain automatically looks for GOOGLE_API_KEY in environment variables
        )

        self.db = SQLDatabase.from_uri(f"databricks://token:{self.token}@{self.host}?http_path=/sql/1.0/warehouses/{self.warehouse_id}&catalog={self.catalog}&schema={self.schema}")
        self.structured_llm = self.llm.with_structured_output(SQLQueryOutput)
        self.sql_query_chain = create_sql_query_chain(self.llm, self.db)

    def generate_sql(self,question: str):
        """Generate a clean SQL query from LLM given a natural language prompt."""
        x = self.sql_query_chain.invoke({"question": question})
        response = self.structured_llm.invoke(x)
        return response.sql_query

    def execute_sql(self, sql_query: str):
        """Generate SQL and run it against the database."""
        # sql = self.generate_sql(question)
        print(f"Generated SQL:\n{sql_query}\n")
        return self.db.run(sql_query)


if __name__ == "__main__":
    try:
        # Assuming '.env' contains DATABRICKS_* and GOOGLE_API_KEY
        client = DatabricksLLMClient(env_path=r".env")

        # The natural language prompt is now the 'prompt' key for the invoke method
        prompt = "Write a SQL query to get me the cricketers names whose age should be greaterthan 20 and number of centuries they made and their date of birth don't use limit and their name starting with anyone one of these letters 'S','V','R'"
        sql_query = client.generate_sql(prompt)

        print("Generated SQL Query:", sql_query)

        # Execute the query
        results = client.execute_sql(sql_query)
        print(results)

    except Exception as e:
        print(f"An error occurred during execution: {e}")