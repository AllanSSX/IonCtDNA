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

## 3 Adapt the script for your purpose

To run the script, you have to make 3 main modifications.

#### 3.1 Modified the input BED file

The localisation of the BED file is hardcoded into the variable `self.target`  
