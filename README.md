# IonCtDNA
#### Estimate the proportion of circulating tumor DNA in blood samples

This document is meant to guide you to adapt the code for your personnal usage.

## 1 Tools and dependencies
Tools used from other projects are shown below.

- Samtools
- Bcftools
- Python   
--pysam   
--pysamstats  
--xlsxwriter   
--django   

## 2 Input files
The plugin takes 2 main files:
- BAM
- BED

The BED file needs to be properly formatted. It's composes of 4 columns:
- 1 / Chromosome name
- 2 / Start
- 3 / End
- 4 / Gene/mutation name

By default, only the base from the start position is taken into account. But the script it's capable to deal with intervals (for deletions).

`chr7	55241707	55241708	EGFR_2155`  
`chr7	55241708	55241709	EGFR_2156`  
`chr7	55242470	55242475	DelE19` # deletion  

## 3 Adapt the script

To run the script, you have to make 2 main modifications.

#### 3.1 Modify the localisation of the BED

The localisation of the BED file is hardcoded into the variable `self.target`.

#### 3.2 Excel formulas

The script generate 1 Excel file per sample. The formula to compute the ratio between the noise and the mutation(s) of interest (N column) is specific to each position (depending of the number of known mutations: A -> C; A -> C/T; A -> C/T/G). You need to modify `formula_noise_mut` dictionary according to your BED file.

For example: plop

`chrom	pos	ref	reads_all	A	C	T	G`  
`chr7	55241707	G	7994	2	0	0	7992`

Known  mutations: G -> C/T/A  
Associated formula: =LARGE(E2:H2,2)

`chr7	55241708	G	7992	13	0	0	7979`

Known  mutations: G -> C/A  
Associated formula: =LARGE(E2:F2,1)

`chr7	55249071	C	7840	0	7833	7	0`

Known  mutation: C -> T  
Associated formula: =G9

The dictionnary key correspond to the position into the output Excel file. The simplest solution consists to run a first time the plugin without compute any formulas and thereby get the line corresponding to each gene.
An important thing with this formula: we always assume that the reference nucleotide recrute the largest number of reads.

You don't care about deletions, nothing is calculated in this case.