#!/usr/bin/env python
from ion.plugin import *
import os
import subprocess
import xlsxwriter
from django.template import Context, Template
from django.conf import settings
from math import sqrt

class IonCtDNA(IonPlugin):
    """ IonCtDNA """
    version = "1.0"
    allow_autorun = False
    author = "cormieralexandre@gmail.com"
    envDict = dict(os.environ)
    
    def launch(self, data=None):
        # 1 / Get global path
        self.outputDir 		= os.environ["RESULTS_DIR"]  # plugin results directory
        self.analysisDir 	= os.environ["ANALYSIS_DIR"] # main run directory
        self.pluginDir		= os.environ["PLUGIN_PATH"]
        self.urlRoot 		= os.environ["URL_ROOT"]   # /output/Home/X/
        self.urlPlugin 		= os.environ["TSP_URLPATH_PLUGIN_DIR"] # /output/Home/X/plugin_out/<plugin>.xxxx
        self.date               = os.environ["TSP_ANALYSIS_DATE"]
        self.genome		= os.environ["TSP_FILEPATH_GENOME_FASTA"]
        self.target		= "/results/uploads/BED/110/ctDNA_targets.bed"

        # 2 / Get instance parameters 
        fileCount = int(os.environ["PLUGINCONFIG__COUNT"])
        files = []
        for i in range(fileCount):
            item            = {}
            key             = "PLUGINCONFIG__ITEMS__"+str(i)
            barcode         = os.environ[key+"__BARCODE"]
            sample          = os.environ[key+"__SAMPLE"]
            item["input"]   = self.analysisDir +"/" + barcode + "_rawlib.bam"
            item["sample"]  = sample
            item["barcode"] = barcode
            item["key"]     = key
            item["xlsx"]    = self.outputDir + "/" + sample + "_" + self.date +".xlsx"
            item["excel"]   = self.urlPlugin + "/" + sample + "_" + self.date +".xlsx" 
            
            files.append(item)
            
        # 3 / Get targets
        readBED = open(self.target, "r") 
        targets = {}
        indels = {}
        
        for target in readBED:
            chr, start, end, gene = target.split()[0:4]
            
            pos = range(int(start), int(end))
            if not targets.has_key(chr):
                targets[chr]=dict((nucl,gene) for nucl in pos)
            else:
                targets[chr].update((nucl,gene) for nucl in pos)
            
            if len(pos) > 1:
                if not indels.has_key(chr):
                    indels[chr] = pos
                else:
                    targets[chr].extend(pos)

        # 4 / Loop on each files
        summary_nucl = {}
        summary_cov = []
        summary_indels = {}
        
        for item in files:    
            # 4.1 / Run pysamstats and extract the result for each target position
            posInterest = []
            for chr in targets.keys():
                pysamstats_cmd = 'pysamstats -f %s --chromosome %s --fields=chrom,pos,ref,reads_all,A,C,T,G,N,deletions,insertions --type variation %s' % (self.genome, chr, item["input"])
                process = subprocess.Popen(pysamstats_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                for line in process.stdout:
                    try:
                        if int(line.split()[1]) in targets[chr].keys():
                            posInterest.append(line.split())
                    except:
                        pass
                out, err = process.communicate()
                if process.returncode == 1:
                    raise Exception(err)
                    exit(1)
            
            # 4.2 / Output the result in a Excel file
            
            # Parameters
            min_cov = 5000
            min_allelic_ratio = 0.005
            min_cov_obs = 8000
            
            # Formula
            #--> to update by user when the bed is modifed
            formula_noise_mut = {2 : ["=LARGE(F2:I2,2)"],
                                 3 : ["=LARGE(F3:G3,1)",0,3],
                                 9 : ["=H9",2],
                                 10 : ["=I10",3],
                                 11 : ["=LARGE(F11:I11,2)"],
                                 12 : ["=H12",2],
                                 13 : ["=LARGE(F13:I13,2)"],
                                 14 : ["=LARGE(F14:I14,2)"],
                                 15 : ["=LARGE(F15:I15,2)"],
                                 16 : ["=LARGE(F16:I16,2)"]}
            
            # Create a workbook and add a worksheet.
            workbook = xlsxwriter.Workbook(item["xlsx"])
            worksheet = workbook.add_worksheet()
            
            # Define cell format
            format01 = workbook.add_format()
            format01.set_num_format('0')
            format02 = workbook.add_format()
            format02.set_num_format('0.00000')
            
            # Add a bold format to use to highlight cells
            bold = workbook.add_format({'bold': 1})
            
            # First line of the worksheet
            worksheet.write('A1', 'gene', bold)
            worksheet.write('B1', 'chrom', bold)
            worksheet.write('C1', 'pos', bold)
            worksheet.write('D1', 'ref', bold)
            worksheet.write('E1', 'reads_all', bold)
            worksheet.write('F1', 'A', bold)
            worksheet.write('G1', 'C', bold)
            worksheet.write('H1', 'T', bold)
            worksheet.write('I1', 'G', bold)
            worksheet.write('J1', 'N', bold)
            worksheet.write('K1', 'deletions', bold)
            worksheet.write('L1', 'insertions', bold)
            worksheet.write('M1', 'large', bold)
            worksheet.write('N1', 'noise/mut', bold)
            worksheet.write('O1', 'noise/lowest cov', bold)
            worksheet.write('P1', 'test', bold)
            
            # Start from the first cell of the second row
            row = 1
            col = 0
            
            # Iterate over the data and write it out row by row.
            for chr, pos, ref, reads_all, reads_A, reads_C, reads_T, reads_G, reads_N, dele, ins in posInterest:
                ACTG = [int(reads_A), int(reads_C), int(reads_T), int(reads_G)]
                gene = targets[chr][int(pos)]
                if int(min_cov_obs) > int(reads_all):
                    min_cov_obs = int(reads_all)
                
                worksheet.write(row, col,             gene)
                worksheet.write(row, col +1 ,         chr)
                worksheet.write_number(row, col + 2,  int(pos))
                worksheet.write(row, col + 3,         ref)
                worksheet.write_number(row, col + 4,  int(reads_all))
                worksheet.write_number(row, col + 5,  int(reads_A))
                worksheet.write_number(row, col + 6,  int(reads_C))
                worksheet.write_number(row, col + 7,  int(reads_T))
                worksheet.write_number(row, col + 8,  int(reads_G))
                worksheet.write_number(row, col + 9,  int(reads_N))
                worksheet.write_number(row, col + 10, int(dele))
                worksheet.write_number(row, col + 11, int(ins))
                
                if indels.has_key(chr) and int(pos) in indels[chr]:
                    if not summary_indels.has_key(chr):
                        summary_indels[chr]={pos: [gene, '', dele]}
                    elif not summary_indels[chr].has_key(pos):
                        summary_indels[chr].update({pos: [gene, '', dele]})
                    else:
                        summary_indels[chr][pos].append(dele)
                
                else:
                    #--> to update by user when the bed is modifed
                    # M
                    formula = '=LARGE(F%d:I%d,1)' % (row+1, row+1)
                    value01 = max(ACTG)
                    worksheet.write_formula(row, col + 12, formula, format01, value01)
                    
                    # N
                    key = row+1
                    formula = formula_noise_mut[key][0]
                    if key in [2,11,13,14,15,16]:
                        value02 = int(self.second_max(ACTG))
                        worksheet.write_formula(row, col + 13, formula, format01, value02)
                    elif key in [9,10,12]:
                        cell = formula_noise_mut[key][1]
                        value02 = int(ACTG[cell])
                        worksheet.write_formula(row, col + 13, formula, format01, value02)
                    else:
                        s = formula_noise_mut[key][1]
                        e = formula_noise_mut[key][2]
                        value02 = int(max(ACTG[s:e]))
                        worksheet.write_formula(row, col + 13, formula, format01, value02)
                    
                    # O
                    formula = '=N%d/%d' % (row+1, min_cov)
                    value03 = float(value02) / float(min_cov)
                    worksheet.write_formula(row, col + 14, formula, format02, value03)
                    
                    # P
                    formula = '=(O%d-%f)/SQRT((%f*(1-%f))/%d)' % (row+1, min_allelic_ratio, min_allelic_ratio, min_allelic_ratio, min_cov)
                    value04 = (value03 - min_allelic_ratio) / sqrt((min_allelic_ratio * (1 - min_allelic_ratio)) / min_cov)
                    worksheet.write_formula(row, col + 15, formula, format02, value04)
                    
                    # summary part
                    if not summary_nucl.has_key(chr):
                        summary_nucl[chr]={pos: [gene, ref, "%.4f" % value04]}
                    elif not summary_nucl[chr].has_key(pos):
                        summary_nucl[chr].update({pos: [gene, ref, "%.4f" % value04]})
                    else:
                        summary_nucl[chr][pos].append("%.4f" % value04)
                
                row += 1
            summary_cov.append(min_cov_obs)
            workbook.close()
        
        # 6 / Generate results html (django)
        settings.configure()
        source = open(os.environ["RUNINFO__PLUGIN__PATH"] + "/block_template.html", "r").read()
        t = Template(source)
        # Pass files arguments to the template 
        c = Context({'files': files, 'summary_nucl':summary_nucl, 'summary_indels':summary_indels, 'summary_cov':summary_cov})
        html = t.render(c)
        # Output html render 
        f = open(self.outputDir+"/resultat_block.html","w")
        f.write(html)
        f.close()
        
    def second_max(self, lst):
        m = max(lst)
        ms = max(n for n in lst if n!=m)
        
        return ms
    
if __name__ == "__main__":
    PluginCLI()