import getpass
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
import argparse
import json
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

import warnings
warnings.simplefilter("ignore", FutureWarning)

import prompts

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


#Add the model credentials here
if not os.environ.get("LLM_KEY"):
    os.environ["LLM_KEY"] = getpass.getpass("Enter llm key: ")

model = AzureChatOpenAI(
    azure_endpoint="https://add-your-endpoint-here/",
    deployment_name="gpt4o-data-gen",
    model_name="gpt-4",
    openai_api_version="2024-10-01-preview",
    temperature=0.7,
)

class Variations(BaseModel):
    variations: List[List[str]] = Field(description="orthographic variations for the given input sentence")

def generate_orthographic_variations(text, language):
    """
    Generate orthographic variations for the given text.

    Args:
        text (str): Input text to process.
        language (str): Language of the input text.

    Returns:
        List[List[str]]: Processed variations.
    """
    try:
        system_template = (
            prompts.TASK_OVERVIEW_PROMPT
            # + prompts.GUIDELINES_PROMPT[language]
            + prompts.TASK_INSTRUCTION_PROMPT
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "Sentence: {text}")]
        )
        prompt = prompt_template.invoke(
            {"language": language, "text": text}
        )
        structured_model = model.with_structured_output(Variations)
        response = structured_model.invoke(prompt)
        # generated_variations=response.variations
        # for variation in generated_variations:
        #     if len(variation) == 0:
        #         raise ValueError("Length of Variations is 0.")     
        return response.variations

    except Exception as e:
        # Handle Azure content filtering errors specifically
        if "content management policy" in str(e):
            logging.error(
                "Content filtering error for input: '%s'. Error: %s", text, str(e)
            )
            raise AssertionError(f"Content filtering error: {str(e)}")
        else:
            logging.error("Unexpected error: %s", str(e))
            raise

def remove_duplicates_from_variations(variations):
    """
    Remove duplicate items and empty strings in the lists inside the list.

    Args:
        variations (List[List[str]]): Nested list of variations.

    Returns:
        List[List[str]]: Nested list with duplicates and empty strings removed.
    """
    return [list(set(filter(None, inner_list))) for inner_list in variations]

def process_line(line, language):
    try:
        # Parse the JSON line
        record = json.loads(line)

        # Ensure 'text' field exists
        if "text" not in record:
            logging.warning(
                "Skipping line without 'text' field: %s", line.strip()
            )
            return None

        # Process the 'text' field
        for attempt in range(5):
            try:
                variations = generate_orthographic_variations(record["text"], language)
                variations = remove_duplicates_from_variations(variations)
                record['variations'] = variations
                # print("Record is", record)
                return record
            except (ValueError, AssertionError) as e:
                if attempt < 4:
                    logging.warning("Retrying due to error: %s", str(e))
                else:
                    logging.error("Skipping line due to repeated errors: %s", str(e))
                    return None
    except json.JSONDecodeError as e:
        logging.error(
            "Failed to parse JSON line: %s. Error: %s", line.strip(), str(e)
        )
    return None

def process_manifest(input_file, output_file, language, max_workers=None):
    """
    Process the 'text' field in a NeMo manifest JSON Lines file.

    Args:
        input_file (str): Path to the input JSON Lines file.
        output_file (str): Path to save the processed JSON Lines file.
        language (str): Language to process.
        max_workers (int, optional): Number of threads to use for parallel processing.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as infile, open(
            output_file, "w", encoding="utf-8"
        ) as outfile:
            lines = infile.readlines()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(tqdm(executor.map(lambda line: process_line(line, language), lines), total=len(lines), desc="Processing lines"))
                for result in results:
                    if result is not None:
                        outfile.write(json.dumps(result, ensure_ascii=False) + '\n')
    except FileNotFoundError as e:
        logging.error("File not found: %s", str(e))
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e))

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Process the 'text' field in a NeMo manifest JSON Lines file."
    )
    parser.add_argument(
        "input_file", type=str, help="Path to the input JSON Lines file."
    )
    parser.add_argument(
        "output_file", type=str, help="Path to save the outputs."
    )
    parser.add_argument(
        "language", type=str, help="The language to work on"
    )
    parser.add_argument(
        "--max_workers", type=int, default=6, help="Number of threads to use for parallel processing."
    )

    args = parser.parse_args()

    # Process the manifest file
    process_manifest(args.input_file, args.output_file, args.language, max_workers=args.max_workers)
