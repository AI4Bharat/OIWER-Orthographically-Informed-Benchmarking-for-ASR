


# 📝 Orthographically-Informed Benchmarking for ASR

This repository presents a framework for generating **orthographically-informed benchmarks** that comprehensively capture all possible variations of words in a dataset.

By leveraging **Large Language Models (LLMs)**, we automate the generation of diverse word variants—significantly reducing the need for manual compilation. We also introduce a novel metric:

### 📊 Orthographically-Informed Word Error Rate (OIWER)

**OIWER** improves the evaluation of ASR (Automatic Speech Recognition) systems by accounting for legitimate word-level spelling variations.

---

## 📁 Repository Structure

| File                 | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `agent.py`           | Generates word variations using LLMs and outputs a manifest file.       |
| `calculate_oiwer.py` | Calculates the OIWER by considering the generated variations.      |
| `prompt.py`          | Contains the prompt used to generate spelling variations via LLM.           |

---

## ⚙️ How to Calculate OIWER

### 1. Generate Word Variations

Use `agent.py` to generate orthographic variations for words in the ASR benchmark manifest.

#### Arguments:
- `input_file`: Path to the input JSON Lines file.
- `output_file`: Path to save the output file containing variations.
- `language`: The language to process (e.g., Hindi, English).
- `--max_workers`: *(Optional)* Number of threads to use for parallel processing.

#### Example:

python3 agent.py "path/to/input/benchmark/manifest.json" \
                 "path/to/file/withVariation/manifest_var.jsonl" \
                 Hindi

### 2. Save The Predictions

Save the predicted text from the model under consideration with an additional key `"pred_text"` in the `manifest_var.jsonl` file.

### 3. Calculate OIWER
Use `calculate_oiwer.py` to compute the Orthographically-Informed Word Error Rate.

#### Arguments:
- `"file"`: Path to the JSON Lines file.
- `"output_file"`: Path to the CSV file to save the OIWER result.
- `"language"`: Name of the language in lowercase.
- `"model_name"`: Name of the model.
- `"dataset_name"`: Name of the dataset.

#### Example:

python3 calculate_oiwer.py "path/to/input/benchmark/manifest.json" "path/to/output.csv" hindi "$model" "$data"

