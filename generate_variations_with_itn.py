import argparse
import json
import logging
import os
import time
import traceback
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
# import prompts
import importlib
# from language_prompts.expert_verified import prompt_assamese as prompts  # your prompt file containing TASK_*, GUIDELINES_PROMPT
from google import genai
from google.genai import types

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Setup Gemini credentials
os.environ['GOOGLE_CLOUD_PROJECT'] = "add-your-cloud-project-name-here"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "add-your-json-creadentials-here"

def load_prompts(language):
    module_name = f"language_prompts.expert_verified.prompts_{language}"
    return importlib.import_module(module_name)

# --- Prompt Construction ---
def build_prompt(text: str, language: str) -> str:
    
    try:
        prompts=load_prompts(language.lower())
        language_guidelines = prompts.GUIDELINES_PROMPT.get(language.lower())
        if not language_guidelines:
            raise ValueError(f"No guidelines found for language: {language}")
        
        full_prompt = (
            prompts.TASK_OVERVIEW_PROMPT.format(language=language) + "\n\n" +
            prompts.TASK_INSTRUCTION_PROMPT.format(language=language) + "\n\n" +
            language_guidelines + "\n\n" +
            f"Sentence: {text}\nOutput:"
        )
        return full_prompt
    except Exception as e:
        logging.error(f"Error in prompt building: {e}")
        raise

# --- Call Gemini to generate variations ---
def call_gemini_variations(text: str, language: str, temperature: float) -> List[List[str]]:
    client = genai.Client(
        vertexai=True,
        project="add-your-project-name-here",
        location="add-your-location-here"
    )

    model = "gemini-2.5-pro"
    prompt = build_prompt(text, language)

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )
    ]

    config = types.GenerateContentConfig(
        temperature=temperature,
        maxOutputTokens=4096,
        response_mime_type="application/json"
    )

    try:
        full_response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,  # pass config here
        ):
            full_response += chunk.text or ""

        print("full reposnse:", full_response)
        response_data = json.loads(full_response)
        return response_data
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        traceback.print_exc()
        return []


# --- Clean duplicates ---
def clean_variations(variations):
    return [list(set(filter(None, group))) for group in variations if group]

# --- Process a single JSONL line ---
def process_line(line: str, language: str,  temperature:float, max_retries=1) -> dict:
    try:
        record = json.loads(line)
        if "text" not in record:
            return None

        text = record["text"]
        for attempt in range(max_retries):
            variations = call_gemini_variations(text, language, temperature)
            print("Variations generated:", variations)
            if variations:
                # record["variations"] = clean_variations(variations)
                record["variations"] = variations
                return record
            logging.warning(f"Attempt {attempt+1}/{max_retries} failed for text: {text}")
            time.sleep(5)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON line: {line.strip()}")
    except Exception as e:
        logging.error(f"Failed to process line: {e}", exc_info=True)
    return None

# --- Process a full file in batches with retries ---
def process_file(input_path, output_path, language, max_workers=6, batch_size=250, batch_retry=2, temperature=0):
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
        # lines = [next(infile) for _ in range(2)]


    total_lines = len(lines)
    batches = [lines[i:i + batch_size] for i in range(0, total_lines, batch_size)]

    failed_lines = []

    for batch_num, batch in enumerate(batches, start=1):
        logging.info(f"Processing batch {batch_num}/{len(batches)} with {len(batch)} lines")

        success = False
        retries_left = batch_retry

        while not success and retries_left >= 0:
            batch_results = []
            failed_sub_lines = []

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(process_line, line, language, temperature): line for line in batch}
                for future in tqdm(as_completed(futures), total=len(futures), desc=f"Batch {batch_num} (Retries left: {retries_left})"):
                    try:
                        result = future.result()
                        if result:
                            batch_results.append(result)
                        else:
                            failed_sub_lines.append(futures[future])
                    except Exception as e:
                        logging.error(f"Unhandled error in future: {e}")
                        failed_sub_lines.append(futures[future])

            # Save successful results
            with open(output_path, "a", encoding="utf-8") as outfile:
                for record in batch_results:
                    json.dump(record, outfile, ensure_ascii=False)
                    outfile.write("\n")

            if failed_sub_lines and retries_left > 0:
                logging.warning(f"{len(failed_sub_lines)} lines failed. Retrying...")
                batch = failed_sub_lines
                retries_left -= 1
                time.sleep(5)
            else:
                success = True
                if failed_sub_lines:
                    failed_lines.extend(failed_sub_lines)

    # Save all failed lines after all retries
    if failed_lines:
        failed_path = output_path.replace(".json", "_failed.json")
        with open(failed_path, "a", encoding="utf-8") as ffail:
            for line in failed_lines:
                ffail.write(line.strip() + "\n")
        logging.warning(f"{len(failed_lines)} lines failed permanently. Saved to: {failed_path}")

    logging.info(f"Finished processing {total_lines} lines. Output saved to: {output_path}")

# --- Entry point ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate orthographic variations using Gemini 2.5 Pro")
    parser.add_argument("input_file", type=str, help="Path to input JSONL file")
    parser.add_argument("output_file", type=str, help="Path to output JSONL file")
    parser.add_argument("language", type=str, help="Language for generating variations")
    parser.add_argument("--max_workers", type=int, default=6, help="Number of threads for parallel processing")
    parser.add_argument("--batch_size", type=int, default=100, help="Batch size for processing")
    parser.add_argument("--batch_retry", type=int, default=2, help="Retry count for failed batches")
    parser.add_argument("--temperature", type=float, default=0, help="temperature for generation")

    args = parser.parse_args()
    process_file(
        args.input_file,
        args.output_file,
        args.language,
        args.max_workers,
        args.batch_size,
        args.batch_retry,
        args.temperature
    )
