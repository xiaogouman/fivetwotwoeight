import sys
import os


def read_csv(filepath):
	'''Read transactions from csv_file specified by filepath
	Args:
		filepath (str): the path to the file to be read

	Returns:
		list: a list of lists, where each component list is a list of string representing a transaction

	'''

	transactions = []
	with open(filepath, 'r') as f:
		lines = f.readlines()
		for line in lines:
			transactions.append(line.strip().split(',')[:-1])
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

	frequent_items = generate_initial_frequent_items(transactions, minsup)
	frequent_items_output = []
	print (frequent_items)

	while len(frequent_items) > 0:
		frequent_items_output.extend(frequent_items)
		# candidate generation
		candidates = candidate_generation(frequent_items)
		# candidate pruning
		pruned_candidates = candidate_prune(frequent_items, candidates)
		# candidate elimination
		frequent_items = candidate_elimination(transactions, pruned_candidates, minsup)
	return frequent_items_output

def candidate_elimination(transactions, candidates, minsup):
	'''
	eliminate all candidates whose support count is less than minsup
	:param transactions: list of list
	:param candidates: list of list
	:param minsup: float
	:return: candidates that support > minsup
	'''
	result_candidates = []
	for candidate in candidates:
		support = get_support_for_candidate(transactions, candidate)
		if support >= minsup:
			result_candidates.append(candidate)
	return result_candidates

def get_support_for_candidate(transactions, candidate):
	'''
	calculate support for the candidate
	:param transactions: list of list
	:param candidate: list
	:return: support of the candidate
	'''
	support_count = 0
	for transaction in transactions:
		if is_contains_candidate(transaction, candidate):
			support_count += 1
	return support_count/len(transactions)


def is_contains_candidate(transaction, candidate):
	'''
	return true if candidate is in the trasactions
	:param transaction: list of list
	:param candidate: list
	:return:
	'''
	for item in candidate:
		if item not in transaction:
			return False
	return True


def candidate_prune(frequent_items, candidates):
	'''

	:param frequent_items: Fk frequent items
	:param candidate:  Lk+1
	:return: remove itemset from candidate whose has infrequent subset
	'''
	if (len(frequent_items[0]) == 1):
		return candidates

	pruned_candidates = []
	for candidate in candidates:
		if not is_prune_candidate(frequent_items, candidate):
			pruned_candidates.append(candidate)
	return pruned_candidates

def is_prune_candidate(frequent_items, candidate):
	'''
	return true if any subset of candidate is not among frequent items
	:param frequent_items: list of list
	:param candidate: list
	:return:
	'''
	subsets = []
	for i in reversed(range(len(candidate))):
		candidate_copy = candidate[:]
		candidate_copy.pop(i)
		subsets.append(candidate_copy)
	for subset in subsets:
		if subset not in frequent_items:
			return True
	return False


def candidate_generation(frequent_items):
	'''
	generate k+1 itemsets from k frequent itemsets
	:param frequent_items:
	:return:
	'''
	next_frequent_items = []
	length = len(frequent_items)
	for i in range(length-1):
		for j in range(i+1, length):
			next_item_set = merge(frequent_items[i], frequent_items[j])
			if next_item_set is not None:
				next_frequent_items.append(next_item_set)
	return next_frequent_items


def merge(itemset1, itemset2):
	'''
	merge two itemsets when they have same items in len 1~k-1
	:param itemset1: list
	:param itemset2: list
	:return: list or None
	'''
	length = len(itemset1)
	if length == 1:
		merged_set = itemset1[:]
		merged_set.append(itemset2[0])
		return merged_set
	for i in range(length):
		if i < length-1 and itemset1[i] != itemset2[i]:
			return None
		elif i == length-1:
			merged_set = itemset1[:]
			merged_set.append(itemset2[i])
			return merged_set
		else:
			continue

def generate_initial_frequent_items(transactions, minsup):
	'''
	generate frequent itemsets of length 1
	:param transactions: list of list
	:param minsup:
	:return: list of list(length 1)
	'''
	items = {}
	for transaction in transactions:
		for item in transaction:
			if items.get(item) is None:
				items[item] = 1
			else:
				items[item] += 1
	num_trans = len(transactions)
	frequent_items = {k: v / num_trans for k, v in items.items() if v / num_trans >= minsup }
	return [[x] for x in frequent_items.keys()]


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
			H = [[x] for x in frequent_itemset]
			H, output_rules = rule_prune(transactions, frequent_itemset, H, minconf)
			rules.extend(output_rules)
			while itemset_size > h_size + 1:
				H = candidate_generation(H)
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
	delete_itemsets = []
	for h in H:
		itemset_x = minus_subset(frequent_itemset, h)
		conf = calculate_conf(transactions, itemset_x, h)
		if conf >= minconf:
			rule = itemset_x[:]
			rule.append('=>')
			rule.extend(h)
			output_rules.append(rule)
		else:
			delete_itemsets.append(h)
	return minus_subset(H, delete_itemsets), output_rules


def minus_subset(itemset1, itemset2):
	'''
	:param itemset1:
	:param itemset2:
	:return: itemset1 - itemset2
	'''
	result_set = []
	for item in itemset1:
		if item not in itemset2:
			result_set.append(item)
	return result_set


def calculate_conf(transactions, itemset_x, itemset_y):
	'''
	return confidence of itemset_x => itemset_y
	:param transactions: list of list
	:param itemset_x:
	:param itemset_y:
	:return: confidence
	'''
	itemset_all = itemset_x[:]
	itemset_all.extend(itemset_y)
	support_all = get_support_for_candidate(transactions, itemset_all)
	support_x = get_support_for_candidate(transactions, itemset_x)
	return support_all/support_x


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


main()