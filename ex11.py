import itertools


class Node:
    def __init__(self, data, positive_child=None, negative_child=None):
        self.data = data
        self.positive_child = positive_child
        self.negative_child = negative_child


class Record:
    def __init__(self, illness, symptoms):
        self.illness = illness
        self.symptoms = symptoms


def parse_data(filepath):
    with open(filepath) as data_file:
        records = []
        for line in data_file:
            words = line.strip().split()
            records.append(Record(words[0], words[1:]))
        return records


class Diagnoser:
    def __init__(self, root: Node):
        self.root = root

    def diagnose(self, symptoms):  # symptoms is a list of strings
        return self.helper_d(self.root, symptoms)

    def helper_d(self, curr_root, symptoms):
        """
        returns the sickness according to the symptoms
        """
        boolean = curr_root.data in symptoms
        if not curr_root.negative_child and not curr_root.positive_child:
            return curr_root.data
        if boolean:
            return self.helper_d(curr_root.positive_child,
                                 symptoms)
        else:
            return self.helper_d(curr_root.negative_child,
                                 symptoms)

    def calculate_success_rate(self, records):
        """Calculates the success rate of the tree according to other reocrds"""
        rate = 0
        for record in records:
            illness = record.illness
            record_lst = record.symptoms
            if illness == self.diagnose(record_lst):
                rate += 1
        if not len(records):
            raise ValueError
        return rate / len(records)

    def all_illnesses(self):
        """
              returns all the illnesses in the tree
              """
        data_set = {}
        self.helper_ill(self.root, data_set)
        sorted_dic = dict(sorted(data_set.items(), key=lambda value: value[1]))
        illnesses = list()
        for key, value in sorted_dic.items():
            illnesses.insert(0, key)
        return illnesses

    def helper_ill(self, curr_root, data_set):
        if not curr_root.negative_child and not curr_root.positive_child:
            if curr_root.data in data_set:
                data_set[curr_root.data] += 1
            else:
                data_set[curr_root.data] = 1
            return data_set
        if curr_root.positive_child is not None:
            self.helper_ill(curr_root.positive_child, data_set)
        if curr_root.negative_child is not None:
            self.helper_ill(curr_root.negative_child, data_set)
        return data_set

    def paths_to_illness(self, illness):
        """
        retuns all the paths to a specific illness in the tree
        """
        paths = []
        self.helper_path(self.root, paths, illness)
        return paths

    def helper_path(self, parent, paths, illness, temp=[]):
        if not parent.negative_child and not parent.positive_child:
            if parent.data == illness or not illness:
                paths.append(temp[:])
            if len(temp):
                temp.pop()
            return
        self.add_childs(illness, parent, paths, temp)

    def add_childs(self, illness, parent, paths, temp):
        if not parent.positive_child:
            if len(temp):
                temp.pop()
        else:
            temp.append(True)
            self.helper_path(parent.positive_child, paths, illness,
                             temp)
        if not parent.negative_child:
            if len(temp):
                temp.pop()
        else:
            temp.append(False)
            self.helper_path(parent.negative_child, paths, illness,
                             temp)
        if len(temp):
            temp.pop()

    def minimize(self, remove_empty=False):
        """removes unnecessary data from the tree"""
        return Diagnoser(self.minimize_helper(self.root, self.root))

    def minimize_helper(self, root, root1):

        all_ills = self.all_illnesses()
        for ill in all_ills:
            root = root1
            paths = self.paths_to_illness(ill)
            if len(paths) > 1:
                newRoot = Node
                N = self.gotopath(root, paths[0])
                root1 = self.addnodes(newRoot, root, paths[0], 0, N)
                return root1
        return root1
        # return newRoot

    def gotopath(self, root, path, counter=0):

        if counter == len(path) - 1:
            return Node(root.positive_child.data)

        if path[counter]:
            return self.gotopath(root.positive_child, path, counter + 1)
        else:
            return self.gotopath(root.positive_child, path, counter + 1)

    def addnodes(self, newRoot, root, paths, counter, N):
        if counter == len(paths) - 1:
            return N
        if counter != len(paths) - 1:
            if paths[counter]:
                newRoot= Node(
                    root.data,
                    self.addnodes(newRoot, root.positive_child, paths,
                                  counter + 1, N), root.negative_child)
                return newRoot
            if not paths[counter]:
                newRoot= Node(
                    (root.data, root.positive_child,
                     self.addnodes(newRoot, root.negative_child, paths,
                                   counter + 1, N)))
                return newRoot


def build_tree(records, symptoms):
    """
    Builds a tree with specific symptoms and adds the illnesses according
    to the path
    """
    if not len(records):
        raise ValueError
    for x in records:
        if type(x) is not Record:
            raise TypeError
    for i in symptoms:
        if type(i) is not str:
            raise TypeError
    if len(symptoms):
        decision_tree = (tree_builder_helper(records, symptoms))
    else:
        decision_tree = Node(checker([], records, symptoms), None, None)
    return Diagnoser(decision_tree)


def tree_builder_helper(records, symptoms, curr_place=0, curr_root=Node,
                        curr_syms=list()
                        ):
    if curr_place < len(symptoms):
        curr_syms.append(symptoms[curr_place])

    if curr_place == len(symptoms):
        illness = Node(checker(curr_syms, records, symptoms), None, None)
        if len(curr_syms):
            curr_syms.pop()
        return illness
    curr_root = Node(symptoms[curr_place],
                     tree_builder_helper(records, symptoms,
                                         curr_place + 1,
                                         curr_root, curr_syms),
                     tree_builder_helper(records, symptoms,
                                         curr_place + 1,
                                         curr_root, curr_syms))

    return curr_root


def checker(curr_syms, records, symptoms):
    """
    a checker that returns the specific illness according to the path it took

    """
    repeated_max = 0
    most_repeated_illness = None
    removed_syms = [value for value in symptoms if value not in curr_syms]
    data_set = {}
    for record in records:
        flag = 1
        for i in removed_syms:
            if i in record.symptoms:
                flag = -1
                break
        if flag == -1:
            continue
        if set(curr_syms) == set(record.symptoms):
            if record.illness not in data_set:
                data_set[record.illness] = 1
            else:
                data_set[record.illness] += 1

        else:
            check_symptoms2(curr_syms, data_set, flag, record)

    for key, value in data_set.items():
        if value > repeated_max:
            repeated_max = value
            most_repeated_illness = key
    return most_repeated_illness


def check_symptoms2(curr_syms, data_set, flag, record):
    for ill in curr_syms:
        if ill not in record.symptoms:
            flag = -1
            break
        flag = 1
    if flag == 1:
        if record.illness not in data_set:
            data_set[record.illness] = 1
        else:
            data_set[record.illness] += 1


def tree_printer(parent):
    """
    prints a tree (for myself to test)
    """
    return tree_printer_helper(parent, "")


def tree_printer_helper(parent, symptoms):
    if not parent.negative_child and not parent.positive_child:
        print("this is leaf: ", parent.data)
        return parent.data
    if parent.positive_child:
        print("this is pos: ", parent.data)
        tree_printer_helper(parent.positive_child, symptoms)
    if parent.negative_child:
        print("this is neg: ", parent.data)
        tree_printer_helper(parent.negative_child, symptoms)


def optimal_tree(records, symptoms, depth):
    """
    a function that gets a number from the user and creates tree with x amount
    of that number combinations, and in the end returns the tree with the high
    est success rate amogn the others
    """
    max_value = 0
    end_result = Diagnoser
    if depth < 0 or depth > len(symptoms):
        raise ValueError
    combinations_list = []
    random_combinations = itertools.combinations(symptoms, depth)
    for combinations in random_combinations:
        combinations_list.append(combinations)
    for pos in range(len(combinations_list)):
        comb_tree = build_tree(records, combinations_list[pos])
        curr = comb_tree.calculate_success_rate(records)
        if curr > max_value:
            max_value = curr
            end_result = comb_tree

    return end_result
