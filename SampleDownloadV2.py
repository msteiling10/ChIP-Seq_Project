import yaml #for writing yamls
import sys #for seeing if yaml is available 
import subprocess #allows for running bash in python
import os #for connecting to directories 


if 'yaml' in sys.modules:
    print(" Yaml Module already imported.")
else:
    print("Yaml Module not imported yet. Please insure the Yaml Module is installed")
    
# Reading data from the YAML file
with open('YourSamplesHere.yaml', 'r') as file:
    loaded_data = yaml.safe_load(file)

print("Data read from 'data.yaml':")
print(loaded_data)

def get_sra_layout(accession, target_dir): #this is to look at the layouts of SRAs
    
# I originally tried to do this code with vbd-dumb, which is a surface level scan of the data
#it hated me, exit error 3 and 64, it has to do with SRA using cloud now instead of on my disk
#I tried to fix it with --root and different paths but no dice 
    
    try:
        # -X 1: Only look at the first spot
        # -Z: Print to stdout (no files created)
        # --split-spot: If it's paired, it splits 1 spot into 2 reads.
        cmd = ["fastq-dump", "-X", "1", "-Z", "--split-spot", accession]
        
        # We run it from the target directory where the data was downloaded
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=target_dir)
        
        # A single-end FASTQ record has 4 lines.
        # A paired-end FASTQ record (split) will have 8 lines.
        line_count = len(result.stdout.strip().split('\n'))
        
        if line_count >= 8:
            return "PAIRED"
        elif line_count == 4:
            return "SINGLE"
        else:
            return "UNKNOWN (Unexpected line count)"
            
    except Exception as e:
        # If fastq-dump also fails, we check the directory directly for help
        print(f"DEBUG: Detection failed for {accession}: {e}")
        return "UNKNOWN"

def download_sra(accession, target_dir="initial_data"): #function to do SRA download
    command = ["prefetch", accession, "--output-directory", target_dir] #command is prefetch to get SRA + the accession
    if not os.path.exists(target_dir):
        os.makedirs(target_dir) 
    try: #try this section
        # Runs the command on the given accession
        result = subprocess.run(command, check=True, capture_output=True, text=True) 
        #check breaks is if no connection
        #capture_output means python will save what you get
        #text=true means python will decode bytes to text of the output
        print(f"Downloaded {accession}") #for comfort 

        #this calls get_sra_layout to the download code
        layout = get_sra_layout(accession, target_dir)
        print(f"Layout detected for {accession}: {layout}")

    except subprocess.CalledProcessError as e: #if this fails pass and throw error
        print(f"Error Downloading {accession}: {e.stderr}") #what failed, error
        

for a in loaded_data:
    download_sra(a)