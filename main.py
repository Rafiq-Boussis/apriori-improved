import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import math

item_list = list(df.columns)
item_dict = dict()

for i, item in enumerate(item_list):
    item_dict[item] = i + 1

item_dict

transactions = list()

for i, row in df.iterrows():
    transaction = set()
    
    for item in item_dict:
        if row[item] == 't':
            transaction.add(item_dict[item])
    transactions.append(transaction)
    
transactions

def get_support(transactions, item_set):
    match_count = 0
    for transaction in transactions:
        if item_set.issubset(transaction):
            match_count += 1
            
    return float(match_count/len(transactions))

def optimized_get_support(transactions, item_set, min_item, dict_TID):
    match_count = 0
    min_item_transactions = dict_TID[min_item]
    print(min_item_transactions)
    for transaction in min_item_transactions:
        if item_set.issubset(transactions[transaction - 1]):
            match_count += 1
    return float(match_count/len(transactions))


def get_TID_item(transactions, item):
    TID = 1
    list_TID = []
    for transaction in transactions:
        if item.issubset(transaction):
            list_TID.append(TID)
        
        TID += 1
    return list_TID

def find_least_support(level, item_set, dict_TID, transactions):
    min_item_supp = 1.0
    for index in range(0, level):
        item_id = item_set[index]   
        item_supp = float(len(dict_TID[item_id]) / len(transactions))
        if item_supp < min_item_supp:
            min_item_supp = item_supp
            min_item = item_id
    return min_item

        
def self_join(frequent_item_sets_per_level, level):
    current_level_candidates = list()
    last_level_items = frequent_item_sets_per_level[level - 1]
    
    if len(last_level_items) == 0:
        return current_level_candidates
    
    for i in range(len(last_level_items)):
        for j in range(i+1, len(last_level_items)):
            itemset_i = last_level_items[i][0]
            itemset_j = last_level_items[j][0]
            union_set = itemset_i.union(itemset_j)
            
            if union_set not in current_level_candidates and len(union_set) == level:
                current_level_candidates.append(union_set)
                
    return current_level_candidates

def get_single_drop_subsets(item_set):
    single_drop_subsets = list()
    for item in item_set:
        temp = item_set.copy()
        temp.remove(item)
        single_drop_subsets.append(temp)
        
    return single_drop_subsets


def is_valid_set(item_set, prev_level_sets):
    single_drop_subsets = get_single_drop_subsets(item_set)
    
    for single_drop_set in single_drop_subsets:
        if single_drop_set not in prev_level_sets:
            return False
    return True

def pruning(frequent_item_sets_per_level, level, candidate_set):
    post_pruning_set = list()
    if len(candidate_set) == 0:
        return post_pruning_set
    
    prev_level_sets = list()
    for item_set, _ in frequent_item_sets_per_level[level - 1]:
        prev_level_sets.append(item_set)
        
    for item_set in candidate_set:
        if is_valid_set(item_set, prev_level_sets):
            post_pruning_set.append(item_set)
            
    return post_pruning_set

def items_support(item_list, transactions):
    list_supp = []
    for item in range(1, len(item_list) + 1):
        support = get_support(transactions, {item})
        list_supp.append(support)
        list_supp.sort(key = None, reverse = True)  # Make sure that the list is sorted so we can take the highest item support to define minimum_support

    return list_supp

def get_interest_items(item_list, transactions):
    num_interest_items = len(transactions) / len(item_list)
    num_interest_items = math.ceil(num_interest_items)    

    return num_interest_items
    

interest_items = get_interest_items(item_list, transactions)


def get_min_support(interest_items, list_support_items):
    """
    This function aims to determine the minimum support value for the Apriori algorithm. It requires the following inputs:
    - `list_support_items`: A sorted list of item supports in ascending order.
    - `interest_items`: The number of items used to calculate the support.
    - `start_index`: The starting index for selecting the first interest item.
    """
    min_supp = 0

    if len(list_support_items) >=  interest_items:

       for index in range(interest_items):
          min_supp += list_support_items[index]

       min_supp = float(min_supp / interest_items )

       return min_supp
    else:
         print("No more items inside list_support_items")


def apriori(min_support):
    frequent_item_sets_per_level = defaultdict(list) #the problem is here try to fix it
    # print("level : 1", end = " ")
    dict_TID = {}
    list_support_items = []
    
    for item in range(1, len(item_list) + 1):
        support = get_support(transactions, {item})
        dict_TID[item] = get_TID_item(transactions, {item})
        if support >= min_support:
            frequent_item_sets_per_level[1].append(({item}, support))
    # print("Here is the dict_TID:")
    # print(dict_TID)   
    # print(frequent_item_sets_per_level)
    
    for level in range(2, len(item_list) + 1):
        # print(level, end = " ")
        current_level_candidates = self_join(frequent_item_sets_per_level, level)

        post_pruning_candidates = pruning(frequent_item_sets_per_level, level, current_level_candidates)
        if len(post_pruning_candidates) == 0:
            break
        print(level)

        for item_set in post_pruning_candidates:
            list_item_set = list(item_set)

            min_item = find_least_support(level, list_item_set, dict_TID, transactions)
            # print(list_item_set)
            # print(f"Here you will find the min_item:  {min_item}")

            support = optimized_get_support(transactions, item_set, min_item, dict_TID)
            # print(f"The value of support of the item-set {item_set} is : {support}")
            if support >= min_support:
                frequent_item_sets_per_level[level].append((item_set, support))
                

    # print(frequent_item_sets_per_level)
    return frequent_item_sets_per_level

min_support = get_min_support(interest_items, list_support_items)

item_support_dict = dict()
items_list = list()

key_list = list(item_dict.keys())
val_list = list(item_dict.values())

for level in frequent_item_sets_per_level:
    for set_support_pair in frequent_item_sets_per_level[level]:
        for i in set_support_pair[0]:
            items_list.append(key_list[val_list.index(i)])
        item_support_dict[frozenset(items_list)] = set_support_pair[1]
        items_list = list()

def find_subset(item, item_length):
    combs = []
    for i in range(1, item_length + 1):
        combs.append(list(combinations(item, i)))
        
    subsets = []
    for comb in combs:
        for elt in comb:
            subsets.append(elt)
            
    return subsets


def association_rule(min_confidence, support_dict):
    rules = list()
    for item, support in support_dict.items():
        item_length = len(item)
       
        if item_length > 1:
            subsets = find_subset(item, item_length)
           
            for A in subsets:
                B = item.difference(A)
               
                if B:
                    A = frozenset(A)
                    
                    AB = A | B
                    
                    confidence = support_dict[AB] / support_dict[A]
                    lift = support_dict[AB] / (support_dict[A] * support_dict[B])
                    # print(f"Value of lift for {A} and {B} is {lift}")
                    if confidence >= min_confidence and lift > 1:
                        rules.append((A, B, confidence))
    
    return rules


min_confidence = 0.8

association_rules = association_rule(min_confidence, item_support_dict)

is_optimal_min_supp = False
threshold = int(len(transactions) * 30 / 100)
# print(f"The value of Threshold is: {threshold}")

while not is_optimal_min_supp:

    if len(association_rules) < threshold:
        if len(list_support_items) > interest_items:  
            list_support_items.pop(0)
            min_support = get_min_support(interest_items, list_support_items)
            # print(f"The value of min_support is {min_support}")

            frequent_item_sets = apriori(min_support)
            
            print(frequent_item_sets)
            item_support_dict = dict()
            items_list = list()

            key_list = list(item_dict.keys())
            val_list = list(item_dict.values())

            for level in frequent_item_sets:
                for set_support_pair in frequent_item_sets[level]:
                    for i in set_support_pair[0]:
                        items_list.append(key_list[val_list.index(i)])
                    item_support_dict[frozenset(items_list)] = set_support_pair[1]
                    items_list = list()
            # print(item_support_dict)
            
            association_rules = association_rule(min_confidence, item_support_dict)
            print("Number of rules: ", len(association_rules), "\n")
        else:
            # print("no more possible values of min support!")
            # print("Threshold was higher than anticipated")
            # print(f"Best possible min support is: {min_support}")
            break

    else:
        # print(f"Optimal min support is {min_support}")
        is_optimal_min_supp = True
        
    

    
        