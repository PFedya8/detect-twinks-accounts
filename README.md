# detect-twinks-accounts

This Python script is designed to detect potential "twin" accounts based on the analysis of user messages. The script takes input data in the JSONL format and uses word frequency analysis and common message comparison to determine account similarity. The result is a list of "twin" account pairs that may be related to each other.

Main functions of the script:
1. Load data from a JSONL file.
2. Create a dictionary of identical messages with a list of authors.
3. Find identical messages with more than one author.
4. Find all possible combinations of authors in identical messages.
5. Create a frequency dictionary for each author without trivial phrases.
6. Analyze frequency dictionaries and identify suspicious accounts.
7. Combine results and output a list of "twin" account pairs.

To use this script, run it with an argument specifying the data file in JSONL format. Example usage:
`python detect_twins_accounts input_data.jsonl`