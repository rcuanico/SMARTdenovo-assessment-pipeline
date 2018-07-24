'''
Python script for combining all the Quast relults into single text file.
It reads necessary information in .filenames
'''

# Read necessary information on filename of results ===
try:
	with open('.filenames', 'r') as names:
		nameList = names.readlines()
		quastDir = nameList.pop(0).strip()
except IOError as e:
	print("Error: Reading filenames.")

# Start aggregating the results into one file ==========
summary = open('assembly_summary.txt', 'w')
# Matrix to store all info
matrix = []
# Write Headers
summary.write('ASSEMBLY\t\t\t\t')
for h in nameList:
	summary.write(h.strip()+'\t\t')
summary.write('\n')

matrix.append(['# CONTIGS(>=0bp)','# CONTIGS(>=1000bp)','# CONTIGS(>=5000bp)','# CONTIGS(>=10000bp)','# CONTIGS(>=25000bp)','# CONTIGS(>=50000bp)',
'TOTAL LEN(>=0bp)','TOTAL LEN(>=1000bp)','TOTAL LEN(>=5000bp)','TOTAL LEN(>=10000bp)','TOTAL LEN(>=25000bp)','TOTAL LEN(>=50000bp)',
'# CONTIGS','LARGEST CONTIG','TOTAL LENGTH','GC %','N50','N75','L50','L75','# N\'s per 100 kbp'])

data = []
# Iterate over all quast results -----
for name in nameList:
	file = open(quastDir+'/result_'+name.strip()+'/report.txt', 'r')
	lines = file.readlines()
	del lines[:3]	# remove first two lines of report
	for l in lines:
		data.append(l.split()[-1])
	file.close()
	matrix.append(data.copy())
	data.clear()

for col in range(0,21):
	for row in range(0,len(nameList)+1):
		summary.write(matrix[row][col])

		if len(matrix[row][col]) < 4:
			summary.write('\t\t\t\t\t\t')
		elif len(matrix[row][col]) < 8:
			summary.write('\t\t\t\t\t')
		elif len(matrix[row][col]) < 12:
			summary.write('\t\t\t\t')
		elif len(matrix[row][col]) < 16:
			summary.write('\t\t\t')
		elif len(matrix[row][col]) < 20:
			summary.write('\t\t')
		else:
			summary.write('\t')
	summary.write('\n')

summary.close()
