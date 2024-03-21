import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict
import pandas as pd
from itertools import combinations

csv_path = ""
min_support = ""
min_confidence = ""

def choose_csv_file():
    global csv_path
    csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    csv_entry.delete(0, tk.END)
    csv_entry.insert(0, csv_path)

def run_algorithm():
    global csv_path, min_support, min_confidence
    csv_path = csv_entry.get().strip()
    min_support = float(support_entry.get())
    min_confidence = float(confidence_entry.get())

    if not csv_path:
        message_text.config(state=tk.NORMAL)
        message_text.delete("1.0", tk.END)
        message_text.insert(tk.END, "Please choose a CSV file.\n")
        message_text.config(state=tk.DISABLED)
        return

    try:
        min_confidence = float(min_confidence)
    except ValueError:
        message_text.config(state=tk.NORMAL)
        message_text.delete("1.0", tk.END)
        message_text.insert(tk.END, "Please enter a valid number for minimum confidence.\n")
        message_text.config(state=tk.DISABLED)
        return

    df = pd.read_csv(csv_path, low_memory=False)
    item_list = list(df.columns)
    item_dict = dict()

    for i, item in enumerate(item_list):
        item_dict[item] = i + 1

    transactions = list()

    for i, row in df.iterrows():
        transaction = set()
        
        for item in item_dict:
            if row[item] == 't':
                transaction.add(item_dict[item])
        transactions.append(transaction)
    
    def get_initial_support(transactions, item_set):
        transactionIDs = []
        match_count = 0
        transactionID = 0
        for transaction in transactions:
            if item_set.issubset(transaction):
                match_count += 1
                transactionIDs.append(transactionID)
            transactionID += 1

        return float(match_count/len(transactions)), transactionIDs


    def get_support(transactions, transactionIDs, item_set):
        match_count = 0
        newTransactionIDs = []
        for transactionID in transactionIDs:
            if item_set.issubset(transactions[transactionID]):
                match_count += 1
                newTransactionIDs.append(transactionID)
                
        return float(match_count / len(transactionIDs)), newTransactionIDs

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
        for item_set, _, _ in frequent_item_sets_per_level[level - 1]:
            prev_level_sets.append(item_set)
            
        for item_set in candidate_set:
            if is_valid_set(item_set, prev_level_sets):
                post_pruning_set.append(item_set)
                
        return post_pruning_set

    def apriori(min_support):
        frequent_item_sets_per_level = defaultdict(list)
        print("level : 1", end = " ")
        
        for item in range(1, len(item_list) + 1):
            support, transactionIDs = get_initial_support(transactions, {item})
            if support >= min_support:
                frequent_item_sets_per_level[1].append(({item}, support, transactionIDs))
            
        for level in range(2, len(item_list) + 1):
            print(level, end = " ")
            current_level_candidates = self_join(frequent_item_sets_per_level, level)

            post_pruning_candidates = pruning(frequent_item_sets_per_level, level, current_level_candidates)
            if len(post_pruning_candidates) == 0:
                break

            for item_set in post_pruning_candidates:
                min_support = 1
                selected_item_transactionIDs = []
                for item in item_set:
                    for tuple_item in frequent_item_sets_per_level[1]:
                        if item in tuple_item[0]: 
                            if (min_support > tuple_item[1]):
                                min_support =  tuple_item[1]
                                selected_item_transactionIDs = tuple_item[2]
                            break
                support, transactionIDs = get_support(transactions, selected_item_transactionIDs,  item_set)
                if support >= min_support:
                    frequent_item_sets_per_level[level].append((item_set, support, transactionIDs))
                    
        return frequent_item_sets_per_level
    
    frequent_item_sets_per_level = apriori(min_support)

    item_support_dict = dict()
    item_list = list()

    key_list = list(item_dict.keys())
    val_list = list(item_dict.values())

    for level in frequent_item_sets_per_level:
        for set_support_pair in frequent_item_sets_per_level[level]:
            for i in set_support_pair[0]:
                item_list.append(key_list[val_list.index(i)])
            item_support_dict[frozenset(item_list)] = set_support_pair[1]
            item_list = list()
    
    def find_subset(item, item_length):
        combs = []
        for i in range(1, item_length + 1):
            combs.append(list(combinations(item, i)))
            
        subsets = []
        for comb in combs:
            for elt in comb:
                subsets.append(elt)
                
        return subsets  

    def association_rules(min_confidence, support_dict):
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
                        if confidence >= min_confidence:
                            rules.append((A, B, confidence))
        
        return rules
    
    association_rules = association_rules(min_confidence = min_confidence, support_dict = item_support_dict)

    message_text.config(state=tk.NORMAL)
    message_text.delete("1.0", tk.END)
    for rule in association_rules:
        message_text.insert(tk.END, 'Number of rules: {0} \n'.format(len(association_rules)))
        message_text.insert(tk.END, '{0} -> {1} <confidence: {2}> \n'.format(set(rule[0]), set(rule[1]), rule[2]))
    message_text.config(state=tk.DISABLED)
    

root = tk.Tk()
root.title("CSV File Parameters")
root.geometry("830x450")

csv_label = tk.Label(root, text="CSV File Path:")
csv_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
csv_entry = tk.Entry(root, width=60)
csv_entry.grid(row=0, column=1, padx=10, pady=5)
csv_button = tk.Button(root, text="Browse", command=choose_csv_file)
csv_button.grid(row=0, column=2, padx=5, pady=5)

support_label = tk.Label(root, text="Minimum Support:")
support_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
support_default = tk.StringVar(value="0.05")
support_entry = tk.Entry(root, width=10, textvariable=support_default)
support_entry.grid(row=1, column=1, padx=10, pady=5)

confidence_label = tk.Label(root, text="Minimum Confidence:")
confidence_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
confidence_default = tk.StringVar(value="0.6")
confidence_entry = tk.Entry(root, width=10, textvariable=confidence_default)
confidence_entry.grid(row=2, column=1, padx=10, pady=5)

run_button = tk.Button(root, text="Run", command=run_algorithm)
run_button.grid(row=3, column=1, padx=10, pady=10)

message_frame = tk.Frame(root)
message_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
message_text = tk.Text(message_frame, width=100, height=18)
message_text.config(state=tk.DISABLED)
message_text.pack()

root.mainloop()