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
the reduced json paths 
```py
        data_path=f"/home/administrator/data/magz/ASR/{folder_date}/{hard_name}/{internal_batch_name}"
        json_path_h4_a5bar1="reduced_to_real_new_h4_a5r_sa3a.json" # you can comment it 
        json_path_h4="reduced_to_real_new_h4.json" # you can comment it
        json_path_h4_invalid_fixed="invalid_reduced_to_real_new_h4_fixed.json"# you can comment it 
        json_path="reduced_to_real_new.json" # change it to the json generatted from step 1
        
        ocr_output_path=f"/home/administrator/data/magz/OCR/{folder_date}/{hard_name}/{internal_batch_name}" #"/home/administrator/data/magz/OCR/17-7-2023/h1/المصور/باتش 5 المصور 2"

        mapper_real_to_reduce_4=read_reduced_path(json_path_h4_a5bar1) # you can comment it
        mapper_real_to_reduce_1=read_reduced_path(json_path) # leave it as it is 
        mapper_real_to_reduce_2=read_reduced_path(json_path_h4) # you can comment it
        mapper_real_to_reduce_3=read_reduced_path(json_path_h4_invalid_fixed) # you can comment it

        mapper_real_to_reduce=mapper_real_to_reduce_4|mapper_real_to_reduce_2|mapper_real_to_reduce_1|mapper_real_to_reduce_3 # remove all of them except mapper_real_to_reduce_1 ### note that the | order matters a lot so take care

```
Example
```py
folder_date="9-8-2023" # this is a folder  inside ~/data/magz/ASR
hard_folders={
"h4/اخبار اليوم":
["اخر ساعة"]
}
```
this will generate dir in `~/data/magz/OCR/{folder_dare}/{hard_folder}/{hard_folder[values]}`
example
```~/data/magz/OCR/11-8-2023/h4/اخبار اليوم/اخر ساعة```
this folder contain the reduced paths `Titles Pargraphs Articles ...`

this python generate log file
example
```py
log_update_11-8-2023.txt 
```
you can check it with
```py
python check_log.py # modify the log_path inside this script          
```
** So Far we generated the segmentations and the Titles OCR **

# Step 4 OCR for paragraphs
run `automate3_mul_paragrpahs.py`
modify only the paths 
example 
```py
  for dir in [
"/home/administrator/data/magz/OCR/31-7-2023/h1/المصور/باتش 5 المصور 2/Paragraph/"
```
this will run on all dirs in this list and generate OCR dir 
this will loop 5 times to make sure no txt is missed 
```py
python automate3_mul_paragrpahs.py
```
this will generate log while runing 
example
```py
log_update_par_0_11-8-2023 
log_update_par_1_11-8-2023 
log_update_par_2_11-8-2023 
log_update_par_3_11-8-2023 
log_update_par_4_11-8-2023
```
best case when you see start and done 

example
```
start ocr 

 recognition start /home/administrator/data/magz/OCR/11-8-2023/h4/اخبار اليوم/اخر ساعة/Paragraph
done recognition 
```
so it started and didn't find any messing data so it's DONE :D

