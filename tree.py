##
# Tree class for the PIN inference software
##
from node import Node


class Tree:
    def __init__(self):
        self.root = Node("e", 0)
        self.build(self.root, 0)

    ##
    # @returns the root node of this tree
    ##
    def get_root(self):
        return self.root

    ##
    # This function builds a tree containing all possible 4 digit PINs
    ##
    def build(self, parent, level):
        if parent is not None and level < 4:
            for x in range(0, 10):
                new_child = Node(parent.get_digit(), x)
                parent.add_child(new_child)
                self.build(new_child, level + 1)

    # TODO rank all PINs in order of highest to lowest probability
    # This function ranks all possible PINs in the order of highest
    # to lowest probability
    ##
    def rank(self):
        return 0

    ##
    # This function displays the contents of this tree
    ##
    def display(self):
        self.root.display(0)

    ##
    # This function counts the total number of nodes in this tree
    ##
    def size(self):
        count = 0
        if self.root.get_children() is not None:
            count += self.root.size()
        print(count)

# End of file
