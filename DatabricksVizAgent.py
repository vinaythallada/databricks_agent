from DatabricksDataAgent import DatabricksDataAgent
from DataVisualizationAgent import DataVisualizationAgent
import pandas as pd
import re
import ast
import datetime

class DatabricksVizAgent:
    def __init__(self,prompt):
        self.client = DatabricksDataAgent()
        self.sql_query = self.client.fetch_query(prompt)
        self.results = self.client.fetch_data(self.sql_query)


    def normalize_results(self,results):
        """Convert string SQL output into real Python objects (handles datetime)."""

        if not isinstance(results, str):
            return results

        s = results.strip()

        # Replace datetime.date(Y, M, D) → 'YYYY-MM-DD' with zero-padded month/day
        def replace_date(match):
            year = match.group(1)
            month = int(match.group(2))
            day = int(match.group(3))
            return f"'{year}-{month:02d}-{day:02d}'"

        s = re.sub(
            r"datetime\.date\((\d+),\s*(\d+),\s*(\d+)\)",
            replace_date,
            s
        )

        # Safely convert string representation → Python list
        parsed = ast.literal_eval(s)

        # Convert date strings back to datetime.date
        final_rows = []
        for row in parsed:
            new_row = []
            for value in row:
                if isinstance(value, str) and re.match(r"\d{4}-\d{2}-\d{2}", value):
                    value = datetime.date.fromisoformat(value)
                new_row.append(value)
            final_rows.append(tuple(new_row))

        return final_rows

    def viz_func(self):
        results = self.results
        sql_query = self.sql_query
        results = self.normalize_results(results)
        y = sql_query.split("FROM")[0].replace("SELECT", "")
        l1 = []
        for i in y.split(","):
            k = i.split(".")
            l1.append(k[1].strip())
        df = pd.DataFrame(results, columns=l1)
        return  DataVisualizationAgent(df)

if __name__ == "__main__":
    prompt = "Write a SQL query to get me the cricketers names whose age should be greaterthan 20 and number of centuries they made and their date of birth don't use limit and their name starting with anyone one of these letters 'S','B','R' and centuries made greater than 15"
    cli = DatabricksVizAgent(prompt)
    viz = cli.viz_func()
    viz.visualize("plot centuries by name as a bar chart")

