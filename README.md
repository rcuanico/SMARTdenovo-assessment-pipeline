# SMARTdenovo-assessment-pipeline
This simple pipeline helps you automate multiple execution of SMARTdenovo genome assembler
with the same input file but with different set of parameters.

USAGE:
```
/path/to/SMARTAsses.py <config>
```
The configuration file is where all unique and variable parameters are placed.
Sample configuration file is included as reference.
_Whole line comments_ start with a hash (#) and are ignored in parsing.
```
# UNIQUE VALUE ========
prefix = my_assembly
threads = 8
email = me@gmail.com
readsPath = /path/to/reads/file.fa
quastDir = my_results

# VARIABLE ============
minReadLength = 5000,6000,7000
kmer = 16-20
overlapper = zmo, dmo
```
### Required Parameters
#### readsPath
  absolute or relative path to input reads file
#### quastDir
  directory name to be made for storage of results

### Optional Parameters
#### prefix
  for naming purposes
#### threads
  number of threads to be used [_int_]
#### email
  for slurm notifications
#### minReadLength
  minimum read length to be considered [_int_]
#### kmer
  kmer size [_int_]
#### overlapper
  engine of overlapper. [zmo, dmo]
### Output
  The output can be seen in assembly_summary.txt.
  Columns are the different combination of parameters and 
  rows are the metrics provided by Quast.
