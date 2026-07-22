from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv
import os

load_dotenv()

# Works locally via .env AND on Streamlit Cloud via st.secrets
def get_groq_key():
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")


model = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=get_groq_key()
)


# ---- Output schema ----
class FoodVerdict(BaseModel):
    food_name: str = Field(description="Name of the food item analyzed")
    is_valid: bool = Field(
        description="False if the input is not an edible food item (e.g. a random object, place, or gibberish). True otherwise."
    )
    is_healthy: Optional[bool] = Field(
        default=None,
        description="True if the food is healthy, False otherwise. Null if is_valid is False."
    )
    reasoning: str = Field(description="Short explanation of why it is healthy/unhealthy")
    recommendation: Optional[str] = Field(
        default=None,
        description="If unhealthy: how to make it healthier OR what to avoid it for. Null if already healthy."
    )
    healthier_alternatives: Optional[List[str]] = Field(
        default=None,
        description="List of healthier alternative foods, only if unhealthy"
    )


# ---- Parser ----
parser = PydanticOutputParser(pydantic_object=FoodVerdict)

# ---- Prompt template (format instructions injected here) ----
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a nutrition expert. Given a food item, decide if it is healthy or unhealthy. "
     "If unhealthy, give a practical recommendation to make it healthier or suggest what "
     "to avoid it in favor of. Be concise and factual.\n\n"
     "Rules:\n"
     "1. First check if the input is actually an edible food or drink item. If it is NOT edible "
     "(e.g. a random object, place, animal, brand name unrelated to food, or gibberish), set "
     "is_valid to false, explain briefly in reasoning that the input must be an edible item, and "
     "leave is_healthy, recommendation, and healthier_alternatives as null. Do not analyze it further.\n"
     "2. Never suggest or reference beef in any recommendation or healthier alternative. When "
     "suggesting a non-vegetarian alternative or recommendation, use chicken instead of beef.\n\n"
     "Respond ONLY with valid JSON matching this format, no extra text before or after:\n"
     "{format_instructions}"),
    ("human", "Food item: {food_name}")
]).partial(format_instructions=parser.get_format_instructions())
 
# ---- Chain: prompt -> model -> parser ----
chain = prompt | model | parser


def check_food(food_name: str) -> FoodVerdict:
    result = chain.invoke({"food_name": food_name})
    return result


if __name__ == "__main__":
    print(check_food("Maggi"))