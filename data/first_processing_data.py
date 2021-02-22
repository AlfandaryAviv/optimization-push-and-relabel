import csv
import random


# calculate the degrees of
def calculate_degrees(edges_file):
    edges_dict = {i:[] for i in range(1, 1175)}
    degree_dict = {1: [], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[]}

    with open(edges_file, 'r') as ed_file:
        lines = ed_file.readlines()
        for row in lines:
            row = row.split(' ')
            if row[0] == '%':
                continue
            edges_dict[int(row[0])].append(row[1].rstrip())
            edges_dict[int(row[1].rstrip())].append(row[0])

        for key, value in edges_dict.items():
            degree_dict[len(value)].append(key)

        for key in degree_dict.keys():
            print(f'Num of vertices with degree {key}: {len(degree_dict[key])}')
            print(degree_dict[key], '\n')


# creating new file with weights between 30 to 500
def adding_weights(edges_file, output_file):
    with open(edges_file, 'r') as ed_file:
        with open(output_file, 'w') as out_file:
            writer = csv.writer
            lines = ed_file.readlines()
            for row in lines:
                split_row = row.split(' ')
                if split_row[0] == "%":
                    out_file.write(row)
                else:
                    cur_random = random.randint(50, 300)
                    split_row[1] = split_row[1].rstrip()
                    split_row.extend([str(cur_random), '\n'])
                    row_with_weight = ' '.join(split_row)
                    out_file.write(row_with_weight)


if __name__ == "__main__":
    original_file = "road-euroroad.edges"
    new_file = "road-euroroad_with_weight.csv"

    # calculate_degrees(original_file)
    # adding_weights(original_file, new_file)





