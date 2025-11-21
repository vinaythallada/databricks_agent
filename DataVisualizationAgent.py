from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd


class DataVisualizationAgent:
    """Agent to visualize data using natural language queries."""

    def __init__(self, df: pd.DataFrame, model_name: str = "gpt-4o-mini"):
        load_dotenv()
        self.df = df
        self.model = "gemini-2.5-flash"
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            temperature=0.0,
            # LangChain automatically looks for GOOGLE_API_KEY in environment variables
        )
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            verbose=True,
            allow_dangerous_code=True  # allows plotting commands
        )

    def visualize(self, query: str):
        """Run user query to generate visualization."""
        print(f"🧠 Processing query: {query}")
        result = self.agent.run(query)
        plt.show(block=False)
        return result



