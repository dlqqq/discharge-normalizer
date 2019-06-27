#!/usr/bin/env python2.7
# See LICENSE and README.md
# Latest build : github.com/diracs-delta

import os
import csv
import tempfile

def main():
	print('Type "help" for info or type "quit" to quit.')
	while True:
		dir = raw_input("Enter the full path of the .csv directory: ")
		if dir == "help" or dir == "":
			print("=========================================="*2)
			print("The full path of a directory should look like "
				"[DRIVE]://[DATA_FOLDER] on Windows.\n"
				"You can copy this path by right clicking on "
				"the data folder in File Explorer.\n"
				'Do not include a trailing "/".\n'
				"\tex. D://Data/20190605/SWCNT1 where the "
				"folder SWCNT1 contains the .csv files.\n\n"
				"On UNIX-like systems, the full path begins "
				"in the root directory /.\n\n"
				"The required columns must be labelled as "
				"follows:\n"
				'The cycle index column is labelled as '
				'"Cycle_Index".\n'
				'The current column is labelled as '
				'"Current".\n'
				'The voltage column is labelled as '
				'"Voltage".\n'
				'The discharge capacity column is labelled as '
				'"Discharge_Capacity".')
			print("=========================================="*2)
			continue
		elif dir == "quit":
			break
		elif os.path.isdir(dir) == False:
			print('[ERROR]: {0} is not a valid directory. See '
				'"help" for more info.'.format(dir))
			continue

		recurse = raw_input('Normalize data recursively? Press "Enter "'
					'if you don\'t know what this means! '
					'[y/N]: ').lower()
		if recurse == "":
			recurse = "n"
		if recurse != "y" and recurse != "n":
			print('Not a valid option. Defaulting to "n".')
			recurse = "n"

		trim = raw_input("Trim data? This will not produce any columns "
					"other than those needed for data "
					"analysis. [y/N]: ")
		if trim == "":
			recurse = "n"
		if trim != "y" and recurse != "n":
			print('Not a valid option. Defaulting to "n".')
			recurse = "n"

		file_list = find_files(dir, recurse)
		print("[INFO]: Detected files: ")
		for filename in file_list:
			print("\t{0}".format(filename))

		state = normalize(file_list, trim)
		if state == "no_files":
			print("[ERROR]: No .csv files exist in the directory.")
		elif state == "success":
			print("[SUCCESS]: All files normalized successfully.")
		elif state == "some_success":
			print("[WARNING]: Some files not normalized. "
				'Look for "[ERROR]" in the output above for '
				"details.")
		elif state == "no_success":
			print("[ERROR]: No files normalized. "
				'Look for "[ERROR]" in the output above for '
				"details.")

# Returns a list of .csv files within the directory specified by the `dir`
# parameter. Supports recursion based on `recurse` parameter.
def find_files(dir, recurse):
	csv_list = []
	for (path, x, files) in os.walk(dir):
		if recurse == "n":
			csv_list += [os.path.join(path, file) for file in files
					if(file[-4:] == ".csv" and path == dir)]
		elif recurse == "y":
			csv_list += [os.path.join(path, file) for file in files
					if file[-4:] == ".csv"]
	return csv_list


# Normalizes .csv files within a file list output by find_files().
#
# Calls the clean_csv() function, normalizes the returned data, and outputs
# processed .csv data into a new directory nested within the existing directory.
# Returns an integer return value. The return value is 0 on successful
# normalization of the files in `file_list`. Otherwise, the return value is
# negative and the returned string is used for error output.
#
def normalize(file_list, trim):
	errors = False
	processed = False
	if(file_list == []):
		return "no_files"

	for full_filename in file_list:
		dir = os.path.dirname(full_filename)
		filename = os.path.basename(full_filename)
		output_dir = os.path.join(dir, "Normalized_Discharge"
						"_Capacities")

		output_filename = os.path.join(output_dir, "Normalized-"
						+ filename)

		# skip file if it has already been normalized
		if os.path.isfile(output_filename):
			print("[ERROR]: {0} has already been normalized. "
				"Skipping...".format(full_filename))
			errors = True
			continue
		# skip file if it is a normalized output file
		if filename.startswith("Normalized-"):
			print("[ERROR]: {0} is a normalized output file. "
				"Skipping...".format(full_filename))
			errors = True
			continue

		# make the output directory
		if("Normalized_Discharge_Capacities" not in os.listdir(dir)):
			os.mkdir(output_dir)

		# check if .csv files are valid
		orig_file = open(full_filename)
		orig_reader = csv.reader(orig_file)
		csv_valid = True
		try:
			header = next(orig_reader)
			cycle_index = header.index("Cycle_Index")
			current_index = header.index("Current")
			voltage_index = header.index("Voltage")
			discharge_index = header.index("Discharge_Capacity")
		except ValueError:
			print("[ERROR]: This file {0} is not properly named.\n"
				"[.....]: See help for more info. Skipping..."
				"".format(full_filename))
			csv_valid = False
			errors = True
			continue
		except StopIteration:
			print("[ERROR]: The file {0} is empty. Skipping..."
				"".format(full_filename))
			csv_valid = False
			errors = True
			continue
		orig_file.seek(0)
		processed = True

		# instantiate needed output variables and objects
		output_file = open(output_filename, "w+")
		output_writer = csv.writer(output_file)
		clean_file = tempfile.TemporaryFile()
		clean_reader = csv.reader(clean_file)
		clean_writer = csv.writer(clean_file)

		# call the clean_csv() and select_cycles() functions
		print("[INFO]: Performing initial cleaning of {0} in {1}."
			"".format(filename, tempfile.tempdir))
		(max_current, max_cycles) = clean_csv(orig_reader, clean_writer,
							cycle_index,
							current_index,
							voltage_index,
							discharge_index, trim)
		if(trim == "y"):
			cycle_index = 0
			current_index = 1
			voltage_index = 2
			discharge_index = 3
		print("[INFO]: Maximum discharge current of {0} is {1}A after "
			"{2} cycles.".format(filename, max_current, max_cycles))
		clean_file.seek(0)
		selected_cycles = select_cycles(clean_reader, cycle_index,
						current_index, max_current,
						max_cycles)
		cycle_list = list(selected_cycles)
		cycle_list.sort()
		print("[INFO]: Selected cycles for {0}: {1}"
			"".format(filename, cycle_list))

		# select relevant cycles and get maximum discharge capacities.
		# this is written in the dictionary "cycle_dict", each entry of
		# the form cycle:max_capacity.
		select_file = tempfile.TemporaryFile()
		select_writer = csv.writer(select_file)
		select_reader = csv.reader(select_file)
		clean_file.seek(0)
		header = next(clean_reader)

		select_writer.writerow(header)
		cycle_dict = dict()
		for line in clean_reader:
			cycle = int(line[cycle_index])
			capacity = float(line[discharge_index])
			if(cycle in selected_cycles):
				select_writer.writerow(line)
				if(capacity > cycle_dict.get(cycle)):
					cycle_dict[cycle] = capacity

		print("[INFO]: Maximum discharge capacities per cycle: ")
		for i in sorted(list(cycle_dict.keys())):
			print("\t{0}: \t{1}".format(i, cycle_dict[i]))

		# normalize and write to the final output file
		select_file.seek(0)
		output_writer.writerow(header)
		next(select_file)

		for line in select_reader:
			cycle = int(line[cycle_index])
			line[discharge_index] = (float(line[discharge_index])
							/ cycle_dict[cycle])
			output_writer.writerow(line)
	if(processed == False):
		return "no_success"
	elif(errors == True):
		return "some_success"
	return "success"

# Writes only the rows containing discharge data to a .csv file through the
# csv.writer object passed as the parameter "writer". Returns a 2-tuple of the
# maximum (negative) discharge current detected and the number of cycles present
# in the data.
def clean_csv(reader, writer, cycle_index, current_index, voltage_index, discharge_index, trim):
	max_current = 0
	max_cycles = 0
	header = next(reader)
	# write header
	if trim == "y":
		writer.writerow([header[cycle_index],
				header[current_index],
				header[voltage_index],
				header[discharge_index]])
	else:
		writer.writerow(header)
	for line in reader:
		data_line = [float(i) if "." in i else int(i) for i in line]
		current = data_line[current_index]
		cycle = data_line[cycle_index]
		if(current < 0):
			if trim == "y":
				writer.writerow([data_line[cycle_index],
						data_line[current_index],
						data_line[voltage_index],
						data_line[discharge_index]])
			else:
				writer.writerow(line)
			if(current < max_current):
				max_current = current
			if(max_cycles < cycle):
				max_cycles = cycle

	return (max_current, max_cycles)

# Returns a set of selected cycles from a csv.reader object passed as the
# parameter "reader". For a full description of how cycles are selected, read
# the README.md.
def select_cycles(reader, cycle_index, current_index, max_current, max_cycles):
	# skip header and add the first cycle
	next(reader)
	cycles = {1}

	# detect anamolous cycles through a large change in current.
	for line in reader:
		data_line = [float(i) if "." in i else int(i) for i in line]
		cycle = data_line[cycle_index]
		current = data_line[current_index]
		if(((max_current - current) / max_current) > 0.1):
			cycles.add(cycle)

	# if no anomalous data cycles are detected, just pick every hundredth
	# cycle to sample. including the last.
	if(cycles == {1}):
		cycles.add(*range(100, max_cycles, 100))
		cycles.add(max_cycles)
	return cycles

# oh right, almost forgot. we have to call main(). :^)
main()
