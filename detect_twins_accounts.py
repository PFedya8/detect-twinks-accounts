"""This Python script is designed to detect potential "twin" accounts based on the analysis of user messages. The
script processes input data in the JSONL format and uses word frequency analysis and common message comparison to
determine account similarity. The result is a list of "twin" account pairs that may be related to each other.

Main functions of the script:
1. Load data from a JSONL file.
2. Create a dictionary of identical messages with a list of authors.
3. Find identical messages with more than one author.
4. Find all possible combinations of authors in identical messages.
5. Create a frequency dictionary for each author without trivial phrases.
6. Analyze frequency dictionaries and identify suspicious accounts.
7. Combine results and output a list of "twin" account pairs.
"""

import collections
import itertools
import json
import string
import argparse

def load_data(path):
    """
    Loads data from jsonl file
    :param1 path: path to jsonl file
    """
    with open(path, 'r') as f:
        data = [json.loads(line) for line in f]
    return data


def find_suspicious(dictionary, coefficient):
    suspicious = []
    count_common = 10
    for account1, account2 in itertools.combinations(dictionary.keys(), 2):
        # print(account1, account2)
        # check if we already checked this pair
        if (account1, account2) in suspicious or (account2, account1) in suspicious:
            continue
        # check count of all words
        if sum(dictionary[account1].values()) < 10 or sum(dictionary[account2].values()) < 10:
            continue
        top_words1 = [word1 for word1, count in dictionary[account1].most_common(count_common)]
        top_words2 = [word1 for word1, count in dictionary[account2].most_common(count_common)]
        common_word = len(set(top_words1) & set(top_words2))
        max_len = max(len(top_words1), len(top_words2))
        if common_word / max_len >= coefficient:
            suspicious.append((account1, account2))
    return suspicious


def create_dict(message_dat, words_more_than=1):
    """
    Create dictionary
    :param message_dat: data
    :param words_more_than: count of words in message more than will be included into dictionary
    :return: a dictionary of same messages with list of authors
    """
    groups = collections.defaultdict(list)
    for line in message_dat:
        message = line['message'].lower()
        if line['author_id'] not in groups[message] and len(message.split()) > words_more_than:
            groups[message].append(line['author_id'])
    return groups


# now we need to find only same messages with more than 1 author
def find_same_messages(same_messages):
    """
    Sort dictionary next way: if there are more than 1 author have same comment
    :param same_messages: data
    :return: list of authors_ids
    """
    more_one_author = []
    for accounts in same_messages.values():
        if len(accounts) > 1 and accounts not in more_one_author:
            more_one_author.append(accounts)
    return more_one_author


# find all possible combinations of authors in same messages
def find_all_combinations(large):
    all_comb = []
    for accounts in large:
        all_comb.extend(list(itertools.combinations(accounts, 2)))
    return all_comb


# create frequency dictionary for each author without trivial phrases
def crete_freq_dict(data, common):
    """
    Create frequency dictionary
    :param data: main data
    :param common: common words that we don't have to add to dictionary
    :return: frequency dictionary for each author
    """
    freq = {}
    for line in data:
        if line['author_id'] not in freq:
            freq[line['author_id']] = collections.Counter()
        message = line['message'].translate(str.maketrans('', '', string.punctuation))
        for word in message.lower().split():
            if word == '':
                continue
            if word not in common:
                freq[line['author_id']].update([word])
    return freq


def analyse_frequency_dicts(data_dict, top_k=10, threshold=0.5, min_words=2):
    """
    Analyse frequency dictionaries and find suspicious accounts
    :param data_dict: frequency dictionary
    :param top_k: top k words to compare
    :param threshold: threshold for suspicious accounts
    :param min_words: if less than min_words words in account, we have to adjust threshold
    :return: list of suspicious accounts
    """
    suspicious = []
    for account1, account2 in itertools.combinations(data_dict.keys(), 2):
        top_words1 = set([word for word, count in data_dict[account1].most_common(top_k)])
        top_words2 = set([word for word, count in data_dict[account2].most_common(top_k)])
        common_words = top_words1.intersection(top_words2)
        words1_count = sum(data_dict[account1].values())
        words2_count = sum(data_dict[account2].values())

        if len(common_words) == 0:
            continue
        # if one of the accounts has less than min_words words, we have to adjust threshold
        adjusted_threshold = threshold
        if words1_count < min_words or words2_count < min_words:
            adjusted_threshold = threshold * (1 - (min_words - min(words1_count, words2_count)) / min_words)
            # adjusted_threshold = threshold - 0.05
        if len(common_words) / top_k >= adjusted_threshold:
            suspicious.append((account1, account2))
    return suspicious


def combine_results(suspicious_ac, all_comb):
    """
    Combine results of suspicious accounts and repeated messages
    :param suspicious_ac:  list of suspicious accounts
    :param all_comb: list of same messages
    :return: list of suspicious accounts
    """
    set_suspicious = {tuple(sorted(i)) for i in suspicious_ac}
    set_comb = {tuple(sorted(i)) for i in all_comb}
    comb = set_suspicious.intersection(set_comb)
    return list(comb)


# print sorted results
def print_results(twins_accounts):
    print("Twins accounts:")
    print("Possibly was detected", len(twins_accounts), "pairs of twins accounts")
    print("---------------")

    for pair in sorted(twins_accounts):
        print(pair[0], pair[1])


def find_twins_accounts():
    # load data
    parser = argparse.ArgumentParser(description='Load some data from file')
    parser.add_argument('file_name', help='the path to data file')
    args = parser.parse_args()
    data_mes = load_data(args.filr_name)
    # common words
    common_words = ['+1', 'done', 'thanks', 'hi', 'thank', ':-)', 'ok', 'please',
                    'looks', 'good', 'nice', 'sure']

    # dictionary of same messages with list of authors
    same_mes = create_dict(data_mes, 2)
    # we need to save data for frequency dictionary
    data_for_freq = data_mes

    # find same messages with more than 1 author
    large_same_mes = find_same_messages(same_mes)

    # find all possible combinations of authors in same messages
    all_combinations = find_all_combinations(large_same_mes)
    print("Same messages is finding...")

    # frequency dictionary for each author without trivial phrases
    freq_dict = crete_freq_dict(data_for_freq, common_words)
    suspicious_accounts = analyse_frequency_dicts(freq_dict, 10, 0.7, 3)
    print("Frequency dictionary is creating...\n")

    # combine results
    twins_result = combine_results(suspicious_accounts, all_combinations)
    print_results(twins_result)


if __name__ == '__main__':
    find_twins_accounts()
