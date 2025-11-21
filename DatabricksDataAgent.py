from DatabricksLLMClient import DatabricksLLMClient

class DatabricksDataAgent:
    def __init__(self):
        self.client = DatabricksLLMClient(env_path=r".env")

    def fetch_query(self,prompt):
        sql_query = self.client.generate_sql(prompt)
        # print("Generated SQL Query:", sql_query)
        return sql_query

    def fetch_data(self,query):
        results = self.client.execute_sql(query)
        return results


if __name__ == "__main__":
    cli = DatabricksDataAgent()
    prompt = "Write a SQL query to get me the cricketers names whose age should be greaterthan 20 and number of centuries they made and their date of birth don't use limit and their name starting with anyone one of these letters 'S','B','R' and centuries made greater than 15"
    query = cli.fetch_query(prompt)
    res = cli.fetch_data(query)
    print(res)