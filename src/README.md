Watsonx Team: Solutioning-US HCS Solutioners Use Case: Proposal content

Intro - https://github.ibm.com/Krishna-Damarla1/watsonx-hcs/blob/main/US%20HCS%20solutioners-proposal%20content.pdf 

Cloned and improved the scripts from https://github.ibm.com/davemarq/watsonx-jwt-auth 

Code Run steps:
1. Download the project folder as zip file to local computer
2. Edit the env-sample file to your credentials
3. Add the apikey.json file (downloaded  directly from IBM Cloud IAM Access Keys portal) to the project folder
4. Zip the project folder
5. Upload to IBM Watsonx challenge cloud shell
6. Unzip the folder in cloud shell
7. Run - source ./setup_shell.sh. - Installs necessary modules or packages 
8. Run - source ./convert-to-python.sh. - Converts jupyter notebooks (prompts saved in slide 8) to .py file. 
9. Run - source ./run-py-files.sh – Outputs the results of all converted ipynb books to a txt file.  
10.Run – python3  docx2.py – Writes the outputs from txt file to a word document

---
Dave instructions:

Here are my ideas for generating a Word document from the saved notebooks.

-   Use prompt lab, save work as notebook.

-   Start a cloud shell. If there is some way to attach the sandbox artifacts to the cloud shell, that would be very useful and you might be able to skip to step 5.

-   Download saved notebooks to a laptop.

-   Upload saved notebooks from laptop to the cloud shell.

-   Create an API key if you don't have one, and download it to the cloud shell.

-   Clone git repository containing needed scripts. Two options:
    -   This requires a personal access token:
        
        ```shell
        git clone https://github.ibm.com/davemarq/watsonx-jwt-auth.git
        ```
    
    -   Requires a SSH key:
        
        ```shell
        git clone git@github.ibm.com:davemarq/watsonx-jwt-auth.git
        ```

-   Run shell setup script. This installs needed software and sets needed environment variables:
    
    ```shell
    source watsonx-jmt-auth/setup_shell.sh
    ```

-   To verify software installation, run src_sh{jupyter} and see if it
    gives a help message.

-   Convert Jupyter notebooks to Python

	Run

	``` shell
	watsonx-jwt-auth/convert-to-python.sh
	```
	
	to convert the notebooks to Python and add a little code to print
    the results when the Python code is run.
	
- Run the Python code from the notebooks:
  
  ``` shell
  watsonx-jwt-auth/run-py-files.sh
  ```
  
  Now we have a file with prompts and results.
  
- Convert to Word document:
  
  Run
  
  ``` shell
  python3 watsonx-jwt-auth/create-docx.py
  ```
  
  to create results.docx.

# Potential improvements #

## Output and Word document paragraphs ##

run-py-files.sh currently dumps all output to 1 file, and
create-docx.py dumps that whole output into a single paragraph. It
might be better to save multiple output files and treat each one as
its own paragraph.

## Word document title and headers ##

This likely needs to be adjusted. Right now that would involve
updating create-docx.py. Maybe the title could be put in a file and
read in. Not sure how to handle headers.

## Investigate python-docx-templates ##

See if this package could be useful in formatting the document.

# OLD README

## Working with JWT

1. Source the env file
2. Run the script

See the video to provision watsonx: https://ibm.box.com/s/udme0l5v151jma7o3n7lb3evf03sahrw

Reach out to @cmihai for more details.


IAM Token documentation: https://cloud.ibm.com/docs/account?topic=account-iamtoken_from_apikey&code=python
