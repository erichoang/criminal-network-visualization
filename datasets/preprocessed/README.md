# List of Criminal Datasets
The folder contains the criminal datasets in Networkx JSON or NDJSON format that we collected or generated from different data sources, including the [ROXANNE project](https://roxanne-euproject.org/)'s partners and law enforcement agencies.

## Primary Dataset

### Burglary Dataset
The dataset contained around 23,000 reports of solved burglary cases in Israel between 2012 and 2021, which were provided by the Israel National Police and duly anonymized according to the standards of Israeli national law and GDPR and further approved by a legal advisor of the Israel National Police. The information in the reports included a crime identifier, the respective anonymized identifiers of the offenders, the min-max-scaled site coordinates of the crime that prevent precise retrieval of the localization of the site, timestamps, and a parameterized free-text description of the case in the form of an embedding vector.

There are two Networkx JSON networks built from the dataset:
- Offender Network: ``israel_lea_inp_burglary_offender_id_network.json``
- Crime Network: ``israel_lea_inp_burglary_v2_crime_id_network.json``

>**_Note_**: the other files with the same above prefix and timestamps are the subgraphs sliced from the two core networks. The generated networks are compatible with the Networkx library.

## Other Datasets

### Telephone Traffic Dataset
Provided by the Israel National Police, this dataset contains phone numbers anonymized by the phone IDs of each unique number. The data comprises traffic information, including source and target telephone numbers, and the ways of communication, such as calls or SMS. The LEA partner provided two versions of this dataset: 
- #CASE 1 consists of 33 phone calls, and a small network is generated from this dataset with 33 nodes and 38 links in the file ```israel_lea_case1_speakers.json``` using NDJSON format. 
- #CASE 2 contains 124 individuals’ communications and includes traffic information, including anonymized source and target telephone numbers and whether the links are calls or SMS. The generated network has 124 nodes and 178 links in the file ```israel_lea_case2_speakers.json``` using NDJSON format. 

### NIST Dataset
It consists of two clusters of the phone call network dataset published under NIST Speaker Recognition and Evaluation and acquired by the ROXANNE partners. These two networks have 2044 nodes & 5866 links in the file ```nist_c1.json``` and 354 nodes & 468 links in the file ```nist_c2.json```, respectively. The two networks used the NDJSON format.

### CSI Dataset
This is a collection of conversational networks among characters selected from episodes of the Crime Scene Investigation series. Partners in the ROXANNE project have run extensive experiments on this dataset and helped to extract “who talked to whom” information from the videos. Using this information, we have constructed a network among 14 main characters of two episodes: Season 1 - Episode 7 with 60 links in the NDJSON file ```csi_indiap_s01e07.json```, and Season 1 - Episode 8 with 91 links in the NDJSON file ```csi_indiap_s01e08.json```. Each link means its two characters have been involved in some conversation. 

### Madoff Fraud Dataset
This is the network that depicts the finance flows in the Madoff case. The individuals in the network are the involved financial institutions and firms, and the links are money flows.  There are 61 individuals and 61 links in this dataset, and its NDJSON network file could be at ```madoff.json```.
