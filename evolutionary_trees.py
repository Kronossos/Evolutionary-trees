#!/usr/bin/python2
# -*- coding: utf-8 -*-
import random


class Leaf:
    def __init__(self, sequence):
        self.sequence = sequence

    def __iter__(self):
        yield self

    def __str__(self, level=0, blank=False, sign="  "):
        if not blank:
            blank = []
        line = list(" " * level + sign + str(self.sequence))
        for fill in blank:
            try:
                if line[fill] == " ":
                    line[fill] = "│"
            except:
                pass
        return "".join(line)

    def is_leaf(self):
        return True

    def label(self):
        return self.sequence

    def height(self):
        return 0

    def reconstruct_ancestors(self):
        pass


class BinNode:
    def __init__(self, left, right):
        for node in [left, right]:
            if node.__class__.__name__ not in ["BinNode", "Leaf"]:
                exit("Given nodes are not possible part of BinNode.")
        self.left = left
        self.right = right
        self.sequence = None

    def __iter__(self):
        for node in self.left:
            yield node
        yield self
        for node in self.right:
            yield node

    def __str__(self, level=0, blank=False, sign="  "):
        if not blank: blank = []
        switch = False
        line = list(" " * level + sign + "█>")

        if self.label():
            line += self.label()

        for fill in blank[:]:
            if switch or "".join(line[fill:fill + 3]) == "└":
                switch = True
                blank.pop(-1)
            elif line[fill] == " ":
                line[fill] = "│"

        tree = "".join(line)

        if not self.left.is_leaf(): blank.append(level + 2)

        tree += "\n" + self.left.__str__(level + 2, blank, "├-")
        tree += "\n" + self.right.__str__(level + 2, blank, "└-")
        return tree

    def is_leaf(self):
        return False

    def son(self, which):
        if which == "L":
            return self.left
        elif which == "R":
            return self.right
        else:
            print("Unknow son!")

    def set_label(self, sequence):
        self.sequence = sequence

    def label(self):
        return self.sequence

    def reconstruct_ancestors(self):

        self.right.reconstruct_ancestors()
        self.left.reconstruct_ancestors()

        container = Alignment(self.left.label(), self.right.label())[1]

        new_label = ""
        for i in range(len(container[0])):
            new_label += random.choice(container)[i]

        self.set_label(new_label.replace("_", ""))

    def history_cost(self):
        tree_cost = 0
        for child in iter(self):
            try:
                if not child.is_leaf():
                    tree_cost += Alignment(child.left.label(), child.right.label())[0]
            except TypeError:
                return None
        return tree_cost


class BinTree:
    def __init__(self, node):
        if node.__class__.__name__ in ["BinNode", "Leaf"]:
            self.node = node
        else:
            exit("Given root is not possible part of BinTree.")

    def __str__(self):
        if self.root: return self.node.__str__()

    def __iter__(self):
        return iter(self.node)

    def root(self):
        return self.node

    def reconstruct_ancestors(self):
        self.node.reconstruct_ancestors()

    def history_cost(self):
        return self.node.history_cost()


# https://en.wikipedia.org/wiki/Needleman%E2%80%93Wunsch_algorithm
def Alignment(seq1, seq2, gap=1, substitution=1):
    F = [[0 for col in range(len(seq2) + 1)] for row in range(len(seq1) + 1)]

    for i in range(len(seq1) + 1): F[i][0] = gap * i

    for j in range(len(seq2) + 1): F[0][j] = gap * j

    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            penalty = 0 if seq1[i - 1] == seq2[j - 1] else substitution
            match = F[i - 1][j - 1] + penalty
            delete = F[i - 1][j] + gap
            insert = F[i][j - 1] + gap
            F[i][j] = min(match, insert, delete)

    ali1, ali2 = "", ""
    i, j = len(seq1), len(seq2)
    while i > 0 or j > 0:
        try:
            penalty = 0 if seq1[i - 1] == seq2[j - 1] else substitution
        except:
            pass

        if j > 0 and i > 0 and F[i][j] == F[i - 1][j - 1] + penalty:
            ali1 = seq1[i - 1] + ali1
            ali2 = seq2[j - 1] + ali2
            i -= 1
            j -= 1
        elif i > 0 and F[i][j] == F[i - 1][j] + gap:
            ali1 = seq1[i - 1] + ali1
            ali2 = "_" + ali2
            i -= 1
        else:
            ali1 = "_" + ali1
            ali2 = seq2[j - 1] + ali2
            j -= 1

    return F[len(seq1)][len(seq2)], [ali1, ali2]


# http://telliott99.blogspot.com/2010/03/clustering-with-upgma.html
def Reconstruct_History(sequences):
    F = [[float('Inf') for col in range(len(sequences))] for row in range(len(sequences))]

    for row in range(len(sequences)):
        col = 0
        while col < row:
            F[row][col] = Alignment(sequences[row], sequences[col])[0]
            col += 1

    sequences_list = []
    for seq in sequences:
        sequences_list.append(Leaf(seq))

    while len(F) > 1:

        col_min_val = float("inf")
        for row in range(len(F)):
            col = min(F[row])
            if col < col_min_val:
                col_min_val = col
                col_min = F[row].index(min(F[row]))
                row_min = row

        container = Alignment(sequences_list[row_min].label(), sequences_list[col_min].label())[1]
        new_label = ""
        for i in range(len(container[0])):
            new_label += random.choice(container)[i]
        new_label = new_label.replace("_", "")

        new_node = BinNode(sequences_list[row_min], sequences_list[col_min])
        new_node.set_label(new_label)
        sequences_list.append(new_node)

        for index in sorted([col_min, row_min], reverse=True):
            del sequences_list[index]
            del F[index]
            for row in range(len(F)):
                del F[row][index]

        for row_number in range(len(F)):
            F[row_number].append(float("Inf"))

        new_row = []
        for seq_number in range(len(sequences_list) - 1):
            new_row.append(Alignment(new_label, sequences_list[seq_number].label())[0])
        new_row.append(float("Inf"))
        F.append(new_row)

    return BinTree(sequences_list[0])


