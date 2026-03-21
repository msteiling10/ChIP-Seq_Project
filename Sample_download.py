import subprocess
from Bio import Entrez, SeqIO
import os

print("Files will be written to your current working directory")

Entrez.email = input(f"Please enter email needed for Entrez: ") #email needed to use Entrez

samples = ["SRR5660030", "SRR5660033", "SRR5660044", "SRR5660045"] #sample SRA storage 
Ref_accession = "NC_006273.2" #this is for the index we want to use in the pipeline, the NC number is pulled from NCBI by you

reads_dir = "data/reads" #a driectory to hold reads
transcriptome_dir = "data/transcriptome" #a directory to hold the transcriptome 


os.makedirs(reads_dir, exist_ok=True) #making the directory inside your os system
os.makedirs(transcriptome_dir, exist_ok=True) #making the directory inside your os system

print("Fetching reference genome...") #for comfort

#handle format for Entrez is standard, looking inside nuccore by accession with genbank written to text
handle = Entrez.efetch( 
    db="nuccore",
    id=Ref_accession,
    rettype="gb",
    retmode="text"
)

record = SeqIO.read(handle, "genbank") #pull record based on handle
handle.close() #good practice 

with open(os.path.join(transcriptome_dir, "HCMV_CDS.fasta"), "w") as out_fasta: #add the HCMV_CDS.fasta to the directory
    for feature in record.features:
        if feature.type == "CDS" and "protein_id" in feature.qualifiers: #only going for the protein coding materials 
            protein_id = feature.qualifiers["protein_id"][0]
            sequence = feature.location.extract(record.seq)
            out_fasta.write(f">{protein_id}\n{sequence}\n")

print("HCMV_CDS.fasta created successfully.")


for sample in samples: #for all the samples in sample
    print(f"Processing {sample}...") #let user know that sample is being added 

    subprocess.run(["prefetch", sample], check=True) #fasterq_dump needs prefetch to get correct files 

    subprocess.run([ #make our samples into fastq files
        "fasterq-dump",
        sample,
        "-O", reads_dir
    ], check=True)

print("All sample files downloaded successfully.") #for comfort 


