import sys
import os
from collections import defaultdict
import time


def read_csv(filepath):
	'''Read transactions from csv_file specified by filepath
	Args:
		filepath (str): the path to the file to be read

	Returns:
		list: a list of frozensets, where each component frozenset is a list of string representing a transaction

	'''

	transactions = []
	with open(filepath, 'r') as f:
		lines = f.readlines()
		for line in lines:
			transactions.append(frozenset(line.strip().split(',')[:-1]))
	return transactions


# To be implemented
def generate_frequent_itemset(transactions, minsup):
	'''Generate the frequent itemsets from transactions
	Args:
		transactions (list): a list of lists, where each component list is a list of string representing a transaction
		minsup (float): specifies the minsup for mining

	Returns:
		list: a list of frequent itemsets and each itemset is represented as a list string

	Example:
		Output: [['margarine'], ['ready soups'], ['citrus fruit','semi-finished bread'], ['tropical fruit','yogurt','coffee'], ['whole milk']]
		The meaning of the output is as follows: itemset {margarine}, {ready soups}, {citrus fruit, semi-finished bread}, {tropical fruit, yogurt, coffee}, {whole milk} are all frequent itemset

	'''
	minsup_count = minsup * len(transactions)
	frequent_items_output, frequent_items = generate_initial_frequent_items(transactions, minsup_count)
	size = 2

	while len(frequent_items) > 0:
		# update size
		size = size + 1
		# update result set
		frequent_items_output.extend(frequent_items)
		# candidate generation
		candidates = candidate_generation(frequent_items, size)
		# candidate pruning
		pruned_candidates = candidate_prune(frequent_items, candidates)
		# candidate elimination
		frequent_items = candidate_elimination(transactions, pruned_candidates, minsup_count)
	return frequent_items_output


def candidate_elimination(transactions, candidates, minsup_count):
	'''
	eliminate all candidates whose support count is less than minsup
	:param transactions(list of frozenset)
	:param candidates(list of frozenset)
	:param minsup(float)
	:return: list of frozenset
	'''
	candidate_counts = get_support_count_for_candidate(transactions, candidates)
	return [k for k, v in candidate_counts.items() if v >= minsup_count]


def get_support_count_for_candidate(transactions, candidates):
	'''
	calculate support for the candidate
	:param transactions(list of frozenset)
	:param candidate(list of frozenset)
	:return: candidate_counts(dict(frozenset, int))
	'''
	candidate_counts = defaultdict(int)
	for transaction in transactions:
		buckets = [candidate for candidate in candidates if candidate <= transaction]
		for bucket in buckets:
			candidate_counts[bucket] += 1
	return candidate_counts


def candidate_prune(frequent_items, candidates):
	'''
	remove itemset from candidate whose has infrequent subset
	:param frequent_items(list of frozenset)
	:param candidate(frozenset)
	:return: pruned_candidates(list of frozenset)
	'''
	pruned_candidates = []
	for candidate in candidates:
		if not is_prune_candidate(frequent_items, candidate):
			pruned_candidates.append(candidate)
	return pruned_candidates


def is_prune_candidate(frequent_items, candidate):
	'''
	:param frequent_items(list of frozenset)
	:param candidate(frozenset)
	:return: true if any subset of candidate is not among frequent items
	'''
	for item in candidate:
		subset = candidate - frozenset([item])
		if subset not in frequent_items:
			return True
	return False


def candidate_generation(frequent_items, size):
	'''
	generate k+1 itemsets from k frequent itemsets
	:param frequent_items(list of frozenset)
	:return: next_frequent_items(set)
	'''
	next_frequent_items = set()
	for a in frequent_items:
		for b in frequent_items:
			c = a | b
			if a != b and len(c) == size:
				next_frequent_items.add(c)
	return next_frequent_items


def generate_two_itemset(transaction):
	'''
	:param transaction(frozenset)
	:return: two_itemset(list of frozenset)
	'''
	two_itemset = []
	i = 1
	tran = list(transaction)
	for a in tran:
		for b in tran[i:]:
			two_itemset.append(frozenset([a, b]))
		i += 1
	return two_itemset


def generate_initial_frequent_items(transactions, minsup):
	'''
	:param transactions: list of list
	:param minsup:
	:return: frequent_one_items(list of list),
			frequent_two_items(list of list),
			transaction_sets(list of frozenset)
	'''
	single_items = defaultdict(int)
	two_items = defaultdict(int)
	for transaction in transactions:
		for itemset in generate_two_itemset(transaction):
			two_items[itemset] += 1
		for item in transaction:
			single_items[item] += 1
	frequent_one_items = [[k] for k, v in single_items.items() if v >= minsup]
	frequent_two_items = [k for k, v in two_items.items() if v >= minsup]
	return frequent_one_items, frequent_two_items


# To be implemented
def generate_association_rules(transactions, minsup, minconf):
	'''Mine the association rules from transactions
	Args:
		transactions (list): a list of lists, where each component list is a list of string representing a transaction
		minsup (float): specifies the minsup for mining
		minconf (float): specifies the minconf for mining

	Returns:
		list: a list of association rule, each rule is represented as a list of string

	Example:
		Output: [['root vegetables', 'rolls/buns','=>', 'other vegetables'],['root vegetables', 'yogurt','=>','other vegetables']]
		The meaning of the output is as follows: {root vegetables, rolls/buns} => {other vegetables} and {root vegetables, yogurt} => {other vegetables} are the two associated rules found by the algorithm
	

	'''
	frequent_itemsets = generate_frequent_itemset(transactions, minsup)
	rules = []
	for frequent_itemset in frequent_itemsets:
		itemset_size = len(frequent_itemset)
		if itemset_size >= 2:
			h_size = 1
			H = set(frequent_itemset)
			H, output_rules = rule_prune(transactions, frequent_itemset, H, minconf)
			rules.extend(output_rules)
			while itemset_size > h_size + 1:
				H = candidate_generation(H, h_size + 1)
				H, output_rules = rule_prune(transactions, frequent_itemset, H, minconf)
				rules.extend(output_rules)
				h_size += 1

	return rules


def rule_prune(transactions, frequent_itemset, H, minconf):
	'''

	:param transactions:
	:param frequent_itemset: initial frequent itemset
	:param H: itemset of rule generation (x U y = h)
	:param minconf:
	:return:
	'''
	output_rules = []
	delete_itemsets = set()
	for h in H:
		set_h = set([h])
		itemset_x = frequent_itemset - set_h
		conf = calculate_conf(transactions, itemset_x, set_h)
		if conf >= minconf:
			rule = [x for x in itemset_x]
			rule.append('=>')
			rule.extend([h])
			output_rules.append(rule)
		else:
			delete_itemsets.add(h)
	return H - delete_itemsets, output_rules


def calculate_conf(transactions, itemset_x, itemset_y):
	'''
	return confidence of itemset_x => itemset_y
	:param transactions: list of list
	:param itemset_x:
	:param itemset_y:
	:return: confidence
	'''
	itemset_all = itemset_x | itemset_y
	support_counts = get_support_count_for_candidate(transactions, [itemset_all, itemset_x])
	return support_counts.get(itemset_all)/support_counts.get(itemset_x)


def main():

	if len(sys.argv) != 3 and len(sys.argv) != 4:
		print("Wrong command format, please follwoing the command format below:")
		print("python assoc-rule-miner-template.py csv_filepath minsup")
		print("python assoc-rule-miner-template.py csv_filepath minsup minconf")
		exit(0)

	
	if len(sys.argv) == 3:
		transactions = read_csv(sys.argv[1])
		result = generate_frequent_itemset(transactions, float(sys.argv[2]))

		# store frequent itemsets found by your algorithm for automatic marking
		with open('.'+os.sep+'Output'+os.sep+'frequent_itemset_result.txt', 'w') as f:
			for items in result:
				output_str = '{'
				for e in items:
					output_str += e
					output_str += ','

				output_str = output_str[:-1]
				output_str += '}\n'
				f.write(output_str)

	elif len(sys.argv) == 4:
		transactions = read_csv(sys.argv[1])
		minsup = float(sys.argv[2])
		minconf = float(sys.argv[3])
		result = generate_association_rules(transactions, minsup, minconf)

		# store associative rule found by your algorithm for automatic marking
		with open('.'+os.sep+'Output'+os.sep+'assoc-rule-result.txt', 'w') as f:
			for items in result:
				output_str = '{'
				for e in items:
					if e == '=>':
						output_str = output_str[:-1]
						output_str += '} => {'
					else:
						output_str += e
						output_str += ','

				output_str = output_str[:-1]
				output_str += '}\n'
				f.write(output_str)

starttime = time.time()
main()
print('time taken = {0}'.format(time.time() - starttime))