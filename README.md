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

To run the script, you have to make 3 main modifications.

#### 3.1 Modify the localisation of the BED

The localisation of the BED file is hardcoded into the variable `self.target`.

#### 3.2 Case of indels

You need to specify manually the range of indels. It will be used after to separate them from the unique localizations. The current method and structure are unadapted. I will update the script to directly extract this information from the BED and add it into a dictionary.

#### 3.3 Excel formulas

The script generate 1 Excel file per sample. The formula to compute the ratio between the noise and the mutation (N column) is specific to our group and is variable for each position. You need to modify `formula_noise_mut` dictionary according to your BED file. The dictionnary key correspond to the position into the output Excel file.
You don't care about deletions, nothing is calculated in this case.

## 4 Future work

- Possibility to select the BED
- Make a dictionary of formulas for each BED
- Automatically select the correct dictionary of formulas according the BED name