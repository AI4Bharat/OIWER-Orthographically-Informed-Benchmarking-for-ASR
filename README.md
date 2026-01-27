
# 📝 Orthographically-Informed Benchmarking for ASR

This repository presents a framework for generating **orthographically-informed benchmarks** that comprehensively capture possible variations of words in a dataset.

By leveraging **Large Language Models (LLMs)**, we automate the generation of diverse word variants—significantly reducing the need for manual compilation. We also introduce a novel metric:

### 📊 Orthographically-Informed Word Error Rate (OIWER)

**OIWER** improves the evaluation of ASR (Automatic Speech Recognition) systems by accounting for legitimate word-level spelling variations.

---

## 📁 Repository Structure

| File                                | Description                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|
| `generate_variations_with_itn.py`   | Generates word variations using LLMs and outputs a manifest file.           |
| `calculate_oiwer.py`                | Calculates the OIWER by considering the generated variations.               |
| `prompt.py`                         | Contains the prompt used to generate spelling variations via LLM.           |
| `create_variations.sh`              | Bash script to run generate_variations_with_itn.py for all langugaes        |

---

## ⚙️ How to Calculate OIWER

### 1. Generate Word Variations

Use `generate_variations_with_itn.py` to generate orthographic variations for words in the ASR benchmark manifest.

#### Arguments:
- `input_file`: Path to the input JSON Lines file.
- `output_file`: Path to save the output file containing variations.
- `language`: The language to process (e.g., Hindi, English).
- `--max_workers`: *(Optional)* Number of threads to use for parallel processing.(default-6)
- `--batch_size` : *(Optional)* Batch size specification for processing.(default-100)
- `--batch_retry` : *(Optional)* Retry count for failed batches. (default-2)
- `--temperature` : *(Optional)* Temperature given to the llm for generating variations.default-0)

#### Example usage:

python3 agent.py "path/to/input/benchmark/manifest.json" \
                 "path/to/file/withVariation/manifest_var.jsonl" \
                 Hindi

You can use the bash script `create_variations.sh`to run it for all avaiable languages.

#### Prompts:

The prompt used for generation is saved in prompt.py for different languages.

### 2. Save The Predictions

Save the predicted text from the model under consideration with an additional key `"pred_text"` in the `manifest_var.jsonl` file.

### 3. Calculate OIWER
Use `calculate_oiwer.py` to compute the Orthographically-Informed Word Error Rate for each line in json.
Oiwer calculation logic is available in `oiwer_core.py`

#### Arguments:
- `"file"`: Path to the JSON Lines file.
- `"output_file"`: Path to the CSV file to save the OIWER result.
- `"language"`: Name of the language in lowercase.
- `"model_name"`: Name of the model.
- `"dataset_name"`: Name of the dataset.

#### Example:

python3 calculate_oiwer.py "path/to/input/benchmark/manifest.json" "path/to/output.csv" hindi "$model" "$data"



Notes before execution: 
1. Add your gcp credentials in the generate_variations_with_itn.py script(Line 20-21)
2. Add your project name and location in line 51 and 52
