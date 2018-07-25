'''
	Pipeline script for SMARTdenovo benchmarking.
	by RCuanico

	PIPELINE ALGORITHM:
		1. Parse configuration file from argument[1]
		2. Write multiple SLURM files corresponding to combinations
			of the values of parameters
		3. Submit all SLURM files as jobs
		4. Analyze all finished assembly using QUAST
		5. Parse the result
		6. Suggest set of parameters that gives the best result

	CONFIGURATION FILE:
		[ UNIQUE VALUE ]
		prefix		threads		quastDir
		email		readsPath

		[ VARIABLE ]
		minReadLength		kmer
		overlapper

	EXTRA to implement
		- reversed range (i.e. N-n where N>n)
'''

import os
import sys
import re

'''
Parse a configuration file into a dictionary.
Key: parameter
Value: list of values
'''
def parseConfig():
	params = {}
	try:
		with open(sys.argv[1], 'r') as config:
			for line in config:
				line = line.strip()
				if len(line) == 0 or line[0] == '#': continue
				key, stringVal = line.split('=')
				if ',' in stringVal:
					vals = stringVal.split(',')
				else:
					vals = [stringVal]

				newVals = []
				for v in vals:
					if re.match("^\d+-\d+$", v.strip()):		#if its a range
						rng = v.split('-')
						for i in range(int(rng[0]), int(rng[1])+1):
							newVals.append(str(i))
					else:
						newVals.append(v.strip())
				params[key.strip()] = newVals
		return params
	except IOError as e:
		print("USAGE: python3 path/to/SMARTAssess.py <config_file>")

# MAIN ==========================================================================
if len(sys.argv) < 2:
	print("USAGE: python3 path/to/SMARTAssess.py <config_file>")	
	exit()

configDict = parseConfig()
if configDict is None:
	print('Unable to read the configuration file!')
	exit()

# set FLAGS for the presence of parameters -------------------
# if absent or no value given, set its default value
withThreads = True if 'threads' in configDict.keys() and configDict['threads'] != [''] else False
withEmail = True if 'email' in configDict.keys() and configDict['email'] != [''] else False
#----------
if 'prefix' in configDict.keys():
	withPrefix = True
else:
	withPrefix = False
	configDict['prefix'] = ['prefix']	#set default
#----------
if 'quastDir' in configDict.keys():
	withQuastDir = True
else:
	withQuastDir = False
	configDict['quastDir'] = ['quast_results']
#----------
if 'overlapper' in configDict.keys() and configDict['overlapper'] != ['']:
	withOverlapper = True
else:
	withOverlapper = False
	configDict['overlapper'] = ['']
#----------
if 'kmer' in configDict.keys() and configDict['kmer'] != ['']:
	withKmer = True
else:
	withKmer = False
	configDict['kmer'] = ['']
#----------
if 'minReadLength' in configDict.keys() and configDict['minReadLength'] != ['']:
	withMinReadLength = True
else:
	withMinReadLength = False
	configDict['minReadLength'] = ['']

# make Directory where to put all the assemblies ------------------
ctr = 0
while os.system('mkdir '+configDict['prefix'][0]+str(ctr)) != 0:	# prevent error in mkdir
	ctr += 1														# with same dir name
os.chdir(configDict['prefix'][0]+str(ctr))		# cd <folder_created>

# make Directory where to put all QUAST results ------------------
os.system('mkdir '+configDict['quastDir'][0]) != 0

fileNames = []		# where to store the file names
			# Format: <prefix>[_PARAMvalue]...[_PARAMvalue].slurm

# ITERATION over the parameters ----------------------------------
for km in configDict['kmer']:
	for ol in configDict['overlapper']:
		for rl in configDict['minReadLength']:
			file = configDict['prefix'][0]
			if withKmer:
				file = file + '_KM' + km
			if withOverlapper:
				file = file + '_OL' + ol
			if withMinReadLength:
				file = file + '_RL' + rl
			fileNames.append(file)

			# file writing ----------------------------------------
			slurmFile = open(file+'.slurm', 'w')
			slurmFile.write('#!/bin/bash\n')
			slurmFile.write('#SBATCH -J '+configDict['prefix'][0]+'\n')
			slurmFile.write('#SBATCH -o '+file+'.%j.out\n')
			slurmFile.write('#SBATCH -e '+file+'.%j.error\n')
			slurmFile.write('#SBATCH --partition=batch\n')
			if withThreads:
				slurmFile.write('#SBATCH -c '+configDict['threads'][0]+'\n')
			if withEmail:
				slurmFile.write('#SBATCH --mail-user='+configDict['email'][0]+'\n')
				slurmFile.write('#SBATCH --mail-type=begin\n')
				slurmFile.write('#SBATCH --mail-type=end\n')
			slurmFile.write('\n')
			slurmFile.write('module load smartdenovo\n')
			slurmFile.write('module load quast/4.3\n')
			slurmFile.write('\n')
			
			command = 'smartdenovo.pl -c 1 -p '+file
			if withOverlapper:
				command = command+' -e '+ol
			if withThreads:
				command = command+' -t '+configDict['threads'][0]
			if withKmer:
				command = command+' -k '+km
			if withMinReadLength:
				command = command+' -J '+rl

			command = command+' '+configDict['readsPath'][0]+' > '+file+'.mak\n'
			slurmFile.write(command)
			slurmFile.write('make -f '+file+'.mak\n')
			slurmFile.write('\n')
			slurmFile.write('python /hpc/soft/quast/4.3/bin/quast.py '+file+'.'+ol+'.cns -o '+configDict['quastDir'][0]+'/result_'+file+' --no-html --no-plots\n')

			slurmFile.close()

# run all the slurm files created
for file in fileNames:
	os.system('sbatch '+file+'.slurm')

# Write the list of filenames into text
# so that it will be accessible to the python script
# that integrates all the quast result.
fNames = open('.filenames', 'w')
fNames.write(configDict['quastDir'][0]+'\n')
for f in fileNames:
	fNames.write(f+'\n')

# Write slurm file that calls the integrate_result.py
# with the dependency of finished assembly and analysis
slurmParser = open('resultParser.slurm', 'w')
slurmParser.write('#!/bin/bash\n')
slurmParser.write('#SBATCH -J '+configDict['prefix'][0]+'\n')
slurmParser.write('#SBATCH -o quast_results_parsing.%j.out\n')
slurmParser.write('#SBATCH -e quast_results_parsing.%j.error\n')
slurmParser.write('#SBATCH --partition=batch\n')
if withThreads:
	slurmParser.write('#SBATCH -c '+configDict['threads'][0]+'\n')
if withEmail:
	slurmParser.write('#SBATCH --mail-user='+configDict['email'][0]+'\n')
	slurmParser.write('#SBATCH --mail-type=begin\n')
	slurmParser.write('#SBATCH --mail-type=end\n')
slurmParser.write('\n')
slurmParser.write('module load anaconda2/4.2.0')
slurmParser.write('\n')
slurmParser.write('python3 ../'+sys.argv[0][0:-14]+'integrate_result.py\n')
slurmParser.close()

os.system('sbatch --dependency=singleton resultParser.slurm')

