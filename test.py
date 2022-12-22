import itertools
import random

def assign_fencers_to_matches(fencers, num_pistes):
    # List of all the possible combinations of fencers
    combinations = list(itertools.combinations(fencers, 2))

    # Shuffle the list of combinations
    random.shuffle(combinations)

    # Initialize a list of empty lists, one for each piste
    pistes = [[] for _ in range(num_pistes)]

    # Iterate over the shuffled list of combinations and assign each pair of fencers to a piste
    for fencer_1, fencer_2 in combinations:
        for piste in pistes:
            if not piste:
                piste.append((fencer_1, fencer_2))
                break

    # Check if there are any fencers that do not have a match
    unmatched_fencers = [fencer for fencer in fencers if not (fencer in piste for piste in pistes)]

    # Assign the unmatched fencers to a piste where they do not have a match with any of the other fencers
    for fencer in unmatched_fencers:
        for piste in pistes:
            if fencer not in piste:
                piste.append((fencer,))
                break

    return pistes

# Example: assign fencers to 4 pistes
fencers = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve', 'Frank', 'Grace', 'Helen', 'Ivan', 'Judy', 'Karl', 'Linda', 'Mike', 'Nancy', 'Oscar', 'Pam', 'Quinn', 'Ralph', 'Steve', 'Tina', 'Ursula', 'Victor', 'Wendy', 'Xavier', 'Yvonne', 'Zach']
pistes = assign_fencers_to_matches(fencers, 4)

# Print the matches for each piste
for i, piste in enumerate(pistes):
    print(f'Piste {i + 1}: {piste}')
