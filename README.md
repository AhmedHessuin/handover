# handover
# Step 1 Preprocessing 
1- prepare the reduced path 
first you need to run 
python generate_reduced_h4_a5bar_latest_version.py
change the `data_path_h1` variable to the dir contain the images example
```py
        data_path_h1="/home/administrator/data/raw/h4/اخبار اليوم"

```
this will generate reduced path almost for all images
this will genreate 2 json files 
1- `reduced_to_real_new_h4_a5r_sa3a_ali_start.json` this  contain reduced paths all numbers and doesn't contain -1 
2- `invalid_mapper_real_reduced_h4_a5r_sa3a_ali_start.json` this contain reduced path all number and contain -1 in one or more fields 
normally you will make xcel sheet for invalid mapper and ask hassan to fix it 
the reduced path files contain 
the "abs-path" : 'reduced-path"

# Step 2  
take the asr data from hasan and follow the step in the MCIT 2 machine 

steps.txt
the first section to upload the ASR



