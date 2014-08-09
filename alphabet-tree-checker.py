'''
Alphabet tree output checker.

Takes input as a filename argument, or requests from keyboard if no
filename is provided. Reports on whether input matches requirement for
the following question:

http://codegolf.stackexchange.com/questions/35862/make-me-an-alphabet-tree
'''

import string

CONNECTIONS = dict(A = [3, 4],
                   C = [2, 4],
                   E = [2, 4],
                   F = [2, 3],
                   G = [2],
                   H = [1, 2, 3, 4],
                   I = [1, 2, 3, 4],
                   J = [1, 3],
                   K = [1, 2, 3, 4],
                   L = [1, 4],
                   M = [3, 4],
                   N = [2, 3],
                   P = [3],
                   Q = [4],
                   R = [3, 4],
                   S = [2, 3],
                   T = [1, 2],
                   U = [1, 2],
                   V = [1, 2],
                   W = [1, 2],
                   X = [1, 2, 3, 4],
                   Y = [1, 2],
                   Z = [1, 4]
                   )

VALID_LETTERS = set(string.ascii_uppercase) - set('BDO')
VALID_CHARACTERS = VALID_LETTERS | set(' ')


class Node():
    
    def __init__(self, character, location, all_nodes=[]):
        self.location = location
        self.connections = CONNECTIONS[character]
        self.all_nodes = all_nodes
        self.all_nodes.append(self)
        
    def attachees(self):
        attached_to_self = []
        for direction in range(1, 5):
            if direction in self.connections:
                reverse_direction = 5 - direction
                x, y = self.location
                other_location = (x+1-(direction%2)*2,y+1-(direction<3)*2)
                other = self.node_at(other_location)
                if other and (reverse_direction in other.connections):
                    attached_to_self.append(other)
        return attached_to_self
                       
    def node_at(self, location):
        if (location in self.occupied_locations()):
            return [node for node in self.all_nodes
                    if node.location == location
                    ][0]
        else:
            return None
        
    def occupied_locations(self, location_list=[]):
        if not location_list:
            location_list = [node.location for node in self.all_nodes]
        return location_list
        
        
def verify(source):
    '''Print report of whether source matches question requirements.'''
    grumbles = ''
    line_count = 0
    lines = []
    for line in source:
        line_count += 1
        if line_count > 30:
            grumbles += 'PROBLEM: more than 30 lines.\n'
            break
        length = len(line)
        if length > 29:
            grumbles += ('PROBLEM: more than 30 characters in line {}'
                         .format(line_count) +
                         ' (including newline).\n'
                         )
        invalid_characters = set(line) - VALID_CHARACTERS
        if invalid_characters:
            grumbles += ('PROBLEM: Invalid characters in line {}:\n'
                         .format(line_count)
                         )
            while invalid_characters:
                grumbles += invalid_characters.pop()
            grumbles += '\n'
        lines.append(line)
    present_letters = ''.join(''.join(line.split()) for line in lines)
    duplicate_letters = present_letters
    for letter in VALID_LETTERS:
        duplicate_letters = duplicate_letters.replace(letter, '', 1)
        duplicate_letters = ''.join(letter for letter in duplicate_letters
                                    if letter in VALID_LETTERS)
    if duplicate_letters:
        grumbles += ('PROBLEM: Duplicate letters:\n' +
                     duplicate_letters +
                     '\n'
                     )
    represented_letters = set(present_letters)
    missing_letters = ''.join(sorted(list(VALID_LETTERS -
                                          represented_letters
                                          )))
    if missing_letters:
        grumbles += ('PROBLEM: Missing letters:\n' +
                     missing_letters +
                     '\n'
                     )
    nodes = set()
    for line_number in range(len(lines)):
        line = lines[line_number]
        for character_number in range(len(line)):
            character = line[character_number]
            location = (character_number, line_number)
            if character in VALID_LETTERS:
                nodes.add(Node(character, location))
    trees = []
    for node in nodes:
        if not any(node in tree for tree in trees):
            trees.append(home_tree(node, nodes))
    distinct_parts = len(trees)
    if distinct_parts == 0:
        grumbles += 'PROBLEM: No valid letters present.\n'
    elif distinct_parts > 1:
        grumbles += 'PROBLEM: {} disconnected trees:\n'.format(distinct_parts)
    if grumbles:
        print(grumbles)
    else:
        print('This is a valid tree.\n')
    print('\n________________________________________\n'
          .join(display_tree(tree, lines) for tree in trees))
    
    
def home_tree(node, nodes):
    current_tree = {node}
    while True:
        expanded_tree = tree_expansion(current_tree, nodes)
        if len(expanded_tree) == len(current_tree):
            break
        current_tree = expanded_tree
    return current_tree


def tree_expansion(tree, nodes):
    expanded_tree = tree.copy()
    for node in tree:
        expanded_tree.update(node.attachees())
    return expanded_tree
    
    
def display_tree(tree, lines):
    locations = {node.location for node in tree}
    node_lookup = {node.location:node for node in tree}
    rows_of_characters = []
    for row_number in range(len(lines)):
        letter_characters = []
        line = lines[row_number]
        for column_number in range(len(line)):
            character = line[column_number]
            location = (column_number, row_number)
            if location in locations:
                letter_characters.append(character)
            else:
                letter_characters.append(' ')
            letter_characters.append(' ')
        rows_of_characters.append(letter_characters)
        if row_number < len(lines) - 1:
            connector_characters = []
            for column_number in range(len(line)):
                location = (column_number, row_number)
                connector_characters.append(' ')
                connector_characters.append(connector_at(location,
                                                         locations,
                                                         node_lookup
                                                         ))
            rows_of_characters.append(connector_characters)
    output_string = "\n".join("".join(row) for row in rows_of_characters)
    return output_string

    
def connector_at(location, locations, node_lookup):
    '''Return connector between this location and down right.'''
    x, y = location
    down_right = (x + 1, y + 1)
    if (location in locations and
        down_right in locations and
        4 in node_lookup[location].connections and
        1 in node_lookup[down_right].connections
        ):
        return '\\'     # Escaped \
    down = (x, y + 1)
    right = (x + 1, y)
    if (down in locations and
        right in locations and
        2 in node_lookup[down].connections and
        3 in node_lookup[right].connections
        ):
        return '/'
    return ' '

    
def from_file(filename):
    with open(filename) as f:
        for line in f:
            if line:
                neat_line = line.replace('\n', '')
                yield neat_line
            else:
                break
                
            
def from_keyboard():
    print('Enter your tree with an additional newline to terminate')
    while True:
        line = input()
        if line:
            yield line
        else:
            break

            
if __name__=='__main__':
    import sys
    arguments = sys.argv[1:]
    if arguments:
        source = from_file(arguments[0])
    else:
        source = from_keyboard()
    verify(source)

