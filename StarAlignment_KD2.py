import os, sys

exp, file= sys.argv[1], sys.argv[2]

rootpath= '/home/colin/Root/%s/%s' % (exp,file)
ncrnaDir= '/home/colin/bowtie/indexes/rna/star_scer3'
genomeDir= '/home/colin/bowtie/indexes/chromosome/star_scer3_KD2'

# mismatch
mismatch= 0.1         #outFilterMismatchNoverLmax
adapterseq= 'NNNNNNCACTCGGGCACCAAGGA' #linker2     or   # CTGTAGGCACCATCAAT     #linker1
remove_duplicate= 'False'   # or 'False'

############################################################################################################################################
filein= '%s/%s.fastq.gz' %(rootpath,file)
tempfolder= '%s/temp' %(rootpath)
if not os.path.exists(tempfolder):    os.makedirs(tempfolder)
ncrna_outpath= '%s/ncrna_out' %(rootpath)
ncrna_outfile= '%s/%s_Unmapped.fastq.gz' %(ncrna_outpath,file)
if not os.path.exists(ncrna_outpath):   os.makedirs(ncrna_outpath)

if not os.path.exists(ncrna_outfile):
    # De-duplicate reads
    tallyout= '%s/%s_tally.fastq.gz' %(tempfolder,file)
    CMMD= 'tally --with-quality -i %s -o %s' %(filein,tallyout)
    if remove_duplicate== 'True':
        print CMMD
        os.system(CMMD)
    
    # Trim 5'end of reads
    if remove_duplicate== 'True':   inputfile= tallyout
    else:   inputfile= filein

    trimmedfastq= '%s/%s_5trimmed.fastq' %(tempfolder,file)
    starInput= '%s/%s_5trimmed-trimmed.fastq' %(tempfolder,file)
    CMMD1= 'seqtk trimfq -b 4 %s > %s' %(inputfile,trimmedfastq)
    if not os.path.exists(trimmedfastq):
        print CMMD1
        os.system(CMMD1)
        
    # Remove adapter
    if not os.path.exists(starInput):
        #CMMD2= 'skewer -x CTGTAGGCACCATCAAT -l 15 %s -o %s/%s.fastq' %(inputfile,tempfolder,file)    # linker1
        CMMD2= 'skewer -t 32 -x %s -l 10 %s' %(adapterseq,trimmedfastq)  # barcoded linker2
        print CMMD2
        os.system(CMMD2)

    # Remove ncrna
    if os.path.exists(starInput):
        CMMD3= 'STAR --runThreadN 45 --readFilesIn %s --genomeDir %s --limitBAMsortRAM 6000000000 --alignEndsType Local --alignEndsProtrude 15 DiscordantPair --outSAMtype BAM SortedByCoordinate --outReadsUnmapped Fastx --outFilterMismatchNoverLmax 0.3 --outFileNamePrefix %s/' %(starInput,ncrnaDir,ncrna_outpath)
        print CMMD3
        os.system(CMMD3)

        command= 'pigz -c %s/Unmapped.out.mate1 > %s && rm %s/Unmapped.out.mate1' %(ncrna_outpath,ncrna_outfile,ncrna_outpath)
        print command
        os.system(command)

# Align to genome
outfolder= '%s/%s_starM01/' %(rootpath,file)
if not os.path.exists(outfolder):  os.makedirs(outfolder)
outfile= '%sAligned.sortedByCoord.out.bam' %(outfolder)
newoutfile= '%s%s_match.bam' %(outfolder,file)
outfileindex= '%s%s_match.bai' %(outfolder,file)
unmapped= '%s/%s_unmapped.fastq.gz' %(outfolder,file)

if not os.path.exists(outfileindex):
    CMMD='STAR --runThreadN 45 --readFilesIn %s --readFilesCommand gunzip -c --limitBAMsortRAM 6000000000 --alignIntronMax 1000 --outSJfilterIntronMaxVsReadN 1000 1000 1000 --genomeDir %s --outFilterType BySJout --outFilterIntronMotifs RemoveNoncanonicalUnannotated --outFilterMultimapNmax 1 --outFilterMismatchNoverLmax %s --outWigType wiggle read1_5p --outWigNorm RPM --outSAMtype BAM SortedByCoordinate --outReadsUnmapped Fastx --alignEndsType Extend5pOfRead1 --outFileNamePrefix %s' %(ncrna_outfile,genomeDir,mismatch,outfolder)
    print CMMD
    os.system(CMMD)
    
    if os.path.exists(outfile):
        os.rename(outfile,newoutfile)
        CMMD= 'samtools index %s %s' %(newoutfile,outfileindex)
        print CMMD
        os.system(CMMD)

    command= 'pigz -c %s/Unmapped.out.mate1 > %s && rm %s/Unmapped.out.mate1' %(outfolder,unmapped,outfolder)
    print command
    os.system(command)
