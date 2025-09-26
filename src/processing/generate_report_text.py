from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

def generate_final_report(
    final_prompt: str,
    llm: ChatAnthropic
) -> str:
    """
    Generate the final SRAG report using a provided string prompt
    and an Anthropic LLM.

    Args:
        final_prompt (str): The fully formatted prompt containing metrics,
                            news, and instructions for the report.
        llm (ChatAnthropic): Initialized Anthropic chat LLM instance.

    Returns:
        str: The generated report text from the LLM.
    """

    # Build the chain
    generate_report_chain = llm | StrOutputParser()

    # Invoke the chain with the final_prompt string
    return generate_report_chain.invoke(final_prompt)
