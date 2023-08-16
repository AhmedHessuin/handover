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

# Step 3 Process the ASR 
on the server machine 
go to 
```cd ~/magz_scripts/test_upload_h4 ```

run `automate3_mul_latest_version.py`

modify 
the `folder_date` to be the folder date you want to Process inside `~/data/magz/ASR`
the `hard_folder` to be the subdirs inside the dare dire in the ASR path
Example
```py
folder_date="9-8-2023" # this is a folder  inside ~/data/magz/ASR
hard_folders={
"h4/اخبار اليوم":
["اخر ساعة"]
}```
this will generate dir in `~/data/magz/OCR/{folder_dare}/{hard_folder}/{hard_folder[values]}`
example
```~/data/magz/OCR/{folder_dare}/h4/اخبار اليوم/اخر ساعة```

