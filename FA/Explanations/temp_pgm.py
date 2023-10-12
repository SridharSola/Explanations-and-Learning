next_dir_terms = ['next_dir(north,north_east1).','next_dir(north_east1,north_east2).','next_dir(north_east2,north_east).',
                  'next_dir(north_east,east1).','next_dir(east1,east2).','next_dir(east2,east).',
                  'next_dir(east,south_east1).','next_dir(south_east1,south_east2).','next_dir(south_east2,south_east).',
                  'next_dir(south_east,south1).','next_dir(south1,south2).','next_dir(south2,south).',
                  'next_dir(south,south_west1).','next_dir(south_west1,south_west2).','next_dir(south_west2,south_west).',
                  'next_dir(south_west,west1).','next_dir(west1,west2).','next_dir(west2,west).',
                  'next_dir(west,north_west1).','next_dir(north_west1,north_west2).','next_dir(north_west2,north_west).',
                  'next_dir(north_west,north1).','next_dir(north1,north2).','next_dir(north2,north).']

directions = ['north', 'south', 'east', 'west', 'north_east', 'north_west', 'south_east', 'south_west', 'north1', 'south1', 'east1', 'west1', 'north_east1', 'north_west1', 'south_east1', 'south_west1', 
              'north2', 'south2', 'east2', 'west2', 'north_east2', 'north_west2', 'south_east2', 'south_west2']

next_dir_not = []

# Check for pairs of directions that are not in next_dir_terms
for i in range(len(directions)):
    for j in range(i + 1, len(directions)):
        pair = (directions[i], directions[j])
        reversed_pair = (directions[j], directions[i])
        if ('next_dir(' + pair[0] + ',' + pair[1] + ').') not in next_dir_terms and \
           ('next_dir(' + pair[1] + ',' + pair[0] + ').') not in next_dir_terms and \
           ('next_dir(' + reversed_pair[0] + ',' + reversed_pair[1] + ').') not in next_dir_terms and \
           ('next_dir(' + reversed_pair[1] + ',' + reversed_pair[0] + ').') not in next_dir_terms:
            next_dir_not.append('-next_dir('+directions[i]+','+directions[j]+').')

# Now, next_dir_not contains pairs of directions that are not next to each other
print(next_dir_not)

with open('next_dir','w') as f:
	for i in next_dir_terms:
		f.write(i+'\n')
	for i in next_dir_not:
		f.write(i+'\n')

