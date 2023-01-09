




def transpose_list_for_placements(input_list):
    # Create a new list to store the new groups
    transposed_list = []

    # Iterate over the sublists
    for sublist in input_list:      # in this for loop, the var sublist is a list of fencers

        advanced = []               # List to temporarily store the advanced fencers
        eliminated = []             # List to temporarily store the eliminated fencers

        # Iterate over the elements in the sublist
        for i in range(len(sublist)):
            
            if i < len(sublist) / 2:            # If the index of the fencer is in the first half of the list
                advanced.append(sublist[i])     # Add the fencer to the advanced list
            else:                               # else
                eliminated.append(sublist[i])   # Add the fencer to the eliminated list

        # Add the advanced and eliminated lists to the transposed list in the correct order (advanced first, then eliminated)
        transposed_list.append(advanced)
        transposed_list.append(eliminated)

    # Return the transposed list
    return transposed_list




# ---- Test ----

x = [["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]]

print("\n\nCurrent:   ", x, "\n\n") # Print the current list

for i in range(3):
    x = advance_tree(x) # Advance the tree

    print(f"Advancement {i+1}:   ", x) # Print the new list

    print("") # Print a new line