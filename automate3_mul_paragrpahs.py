import os
import requests
from PIL import Image, ImageDraw
import glob
import json
import multiprocessing as mp
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor


def ocr(image_path):
    # OCR_URL = "http://10.107.206.2:8080/recognize" on MCIT
    # OCR_URL = "http://192.168.1.200:6001/recognize" on our machine
    OCR_URL = "http://10.107.206.2:8080/recognize"
    GENERAL_PAYLOAD = {
        'correct_angle': 'false',
        'extract_tables': 'false',
        'extract_graphics': 'false',
        'threads': '24', "model_version": "typewritten/ar/latest"}
    files = [
        ('file', (os.path.basename(image_path),
                  open(image_path, 'rb'), 'image/jpeg'))
    ]
    headers = {}
    response = requests.request("POST", OCR_URL, headers=headers, data=GENERAL_PAYLOAD, files=files, verify=False,
                                timeout=4000)
    if response.status_code == 200:
        print("done")
      #  log_file.write(image_path,"response 200\n")
      #  log_file.flush()
        return response.json()
    else:
        log_file.write(image_path,"response not 200\n")
        log_file.flush()
        print(response.json())
        return ""


def get_text(ocr_output):
    text = []
    for page in ocr_output["pages"]:
        for zone in page["zones"]:
            for pha in zone["paragraphs"]:
                for line in pha["lines"]:
                    text.append(line["text"])
    return " ".join(text)


def run(book):
    book_id = book.split("/")[-1]
    book = book
    out = book
    for image in os.listdir(book):
        if image.endswith(".JPG") or image.endswith(".jpg"):
            filename = os.path.join(book, image)
            out_file = os.path.join(out, image)

            if os.path.exists(f"{out_file[0:-4]}_modified5.json"):
#                log_file.write(f" existed {filename} {datetime.now()} \n")
#                log_file.flush()
                continue


            log_file.write(f" start {filename} {datetime.now()} \n")
            log_file.flush()
            #txt_file = out_file[0:-4] + ".txt"

            if os.path.exists(f"{out_file[0:-4]}_modified5.json"):
                continue


            try:
                ocr_output = ocr(filename)
                for key in ['graphics', 'tables', 'Modified_image', 'page_height', 'page_width', 'process_time']:
                    ocr_output["pages"][0].pop(key)

            except Exception as e:
                print(e)
                log_file.write(f"{e} error {datetime.now()} \n")
                log_file.flush()

                ocr_output = {}
            if ocr_output !={}:
                #ocr_output = get_text(ocr_output)
                #open(txt_file, "w", encoding="utf-8").write(ocr_output)
                with open(f"{out_file[0:-4]}_modified5.json",
                          "w") as outfile:
                    json_object = json.dumps(ocr_output, indent=4)
                    outfile.write(json_object)
                    log_file.write(f"done {filename} {datetime.now()} \n")
                    log_file.flush()




def define_main_paths(prefix="./"):

    # contain ref_path/page_00-art_00-title_00.jpg # cropped
    # contain ref_path/page_00-art_00-title_00.txt
    titles_path=f"{prefix}/Titles" # hattrag3 hia bs

    # contain ref_path/page_00-art_00-image_00.jpg # cropped
    # contain ref_path/page_00-art_00-image_00.json
    images_path=f"{prefix}/Images"

    # contain ref_path/page_00-art_00-Paragraph_00.jpg # cropped
    # contain ref_path/page_00-art_00-Paragraph_00.txt
    paragraph=f"{prefix}/Paragraph"

    # contain ref_path/page_00-art_00.jpg # cropped
    # contain ref_path/page_00-art_00.json
    articles=f"{prefix}/Articles"


    # contain ref_path/page_00-art_00.jpg # cropped
    # contain ref_path/page_00-art_00.json # contain the titles and paragraphs as rectangle points (p1,p2,p3,p4)
    # contain the article as polygon

    segmentation_json=f"{prefix}/Segmentation_json"

    os.makedirs(titles_path,exist_ok=True)
    os.makedirs(images_path,exist_ok=True)
    os.makedirs(paragraph,exist_ok=True)
    os.makedirs(articles,exist_ok=True)
    os.makedirs(segmentation_json,exist_ok=True)
    return titles_path,images_path,paragraph,articles,segmentation_json

def from_points_to_rectangle_points(points):
    x_lst=[p[0] for p in points]
    y_lst=[p[1] for p in points]

    xmin=min(x_lst)
    ymin=min(y_lst)
    xmax=max(x_lst)
    ymax=max(y_lst)
    return [[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]]
def get_images(test_data_path):
    '''
    find image files in test data path
    :return: list of files found
    '''
    files = []
    idx=0

    exts = ['jpg', 'png', 'jpeg', 'JPG', 'tif', "bmp"]
    print("scanning ",test_data_path)
    for parent, dirnames, filenames in os.walk(test_data_path):
        for filename in filenames:
            for ext in exts:
                if filename.endswith(ext):
                    idx+=1
                    # files.append(os.path.join(parent, filename))
                    # file_name_only.append(filename)
                    # parent_folder.append(parent.split("/")[-1])
                    full_path=os.path.join(parent, filename)
                    files.append(full_path)
                    break
    print('Find {} images'.format(len(files)))
    return files


def get_asr(test_data_path):
    '''
    find image files in test data path
    :return: list of files found
    '''
    files = []
    idx=0

    exts = ['asr']
    print("scanning ",test_data_path)
    for parent, dirnames, filenames in os.walk(test_data_path):
        for filename in filenames:
            for ext in exts:
                if filename.endswith(ext):
                    idx+=1
                    # files.append(os.path.join(parent, filename))
                    # file_name_only.append(filename)
                    # parent_folder.append(parent.split("/")[-1])
                    full_path=os.path.join(parent, filename)
                    files.append(full_path)
                    break
    print('Find {} images'.format(len(files)))
    return files

def pill_mask(polygon,img):
    # img_array = numpy.asarray(img)
    # mask_img = Image.new('1', (img_array.shape[1], img_array.shape[0]), 0)
    # ImageDraw.Draw(mask_img).polygon(polygon, outline=1, fill=1)
    # mask = numpy.array(mask_img)
    # # assemble new image (uint8: 0-255)
    # new_img_array = numpy.empty(img_array.shape, dtype='uint8')
    #
    # # copy color values (RGB)
    # new_img_array[:,:,:3] = img_array[:,:,:3]
    #
    # # filtering image by mask
    # new_img_array[:,:,0] = new_img_array[:,:,0] * mask
    # new_img_array[:,:,1] = new_img_array[:,:,1] * mask
    # new_img_array[:,:,2] = new_img_array[:,:,2] * mask
    # # back to Image from numpy
    # newIm = Image.fromarray(new_img_array, "RGB")
    # # newIm.save("out.jpg")
    original = img.copy()
    polygon=[tuple(i) for i in polygon]
    xy = polygon
    min_x = min([i[0] for i in xy])
    min_y = min([i[1] for i in xy])
    max_x = max([i[0] for i in xy])
    max_y = max([i[1] for i in xy])
    mask = Image.new("L", original.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(xy, fill=255, outline=None)
    black =  Image.new("RGB", original.size, 0)
    #mask.show()
    result = Image.composite(original, black, mask)
    result = result.crop((min_x, min_y, max_x, max_y))
    #original.show()
    #result.show()
    return result

def make_mask(points,image):
    # print(points)
    ##################
    masked_image=pill_mask(image,points)
    points=from_points_to_rectangle_points(points)
    masked_image=masked_image.crop([points[0][0],points[0][1],points[2][0],points[2][1]])


    return masked_image


#
# def draw_polygon(points,image):
#     for point_i in range(len(points)-1):
#         cv2.line(image,pt1=(points[point_i][0],points[point_i][1]),
#                  pt2=(points[point_i+1][0],points[point_i+1][1]),color=(0,255,0),thickness=13)
#
#     cv2.line(image,pt1=(points[-1][0],points[-1][1]),
#              pt2=(points[0][0],points[0][1]),color=(0,255,0),thickness=13)
#     cv2.imshow("image",cv2.resize(image,dsize=(500,500)))
#     cv2.waitKey()



def from_annotator_path_to_real_path(annotation_folder_path):

    adding_prefix="/home/administrator/data/raw/"

    # the batch index of / is -9
    annotation_folder_path_cropped="/".join(annotation_folder_path.split("/")[-9:])
    images_path=adding_prefix+annotation_folder_path_cropped
    #    print(images_path)
    return images_path

def read_reduced_path(json_path):
    with open(json_path, "r") as outfile:
        z=json.load(outfile)
        return z

def get_reduced_path(real_path_with_image_name,reduced_dictionary):
    real_path_for_jpg="/".join(real_path_with_image_name.split("/")[0:-1])
    reduced_path=reduced_dictionary[real_path_for_jpg]
    return reduced_path


def main_multi(image_idx,asr_path):
    #    if image_idx ==1:exit()

    print(image_idx,"/",len(asr_paths))
    log_file.write(f"{image_idx}  {asr_path}  {datetime.now()} \n")
    # asr_path=".".join(path.split(".")[0:-1])+'.asr'
    # print(asr_path)
    path=from_annotator_path_to_real_path(asr_path)
    path=glob.glob(f"{path[0:-3]}*")[0] # name.asr --> name.
    lines=open(asr_path,'r').readlines()
    polygon_type=[]
    polygon_points=[]

    for line in lines:
        if "PolygonType" in line :
            polygon_type.append(line.split()[-1].strip().rstrip())

        if len(line.split())==1:
            continue

        if "polygon-pts" in line :
            line=line.split(" ")[1].strip().rstrip()
            points=line.split(":")
            points = [ [int(p.split(',')[0]),int(p.split(',')[1])] for p in points]
            polygon_points.append(points)
            # draw_polygon(points,img.copy())
            # make_mask(points,img.copy())

    # for i in range(len(polygon_type)):
    #     print(polygon_type[i])
    #     print(polygon_points[i])
    #     print("----")
    if len(polygon_type)!=len(polygon_points): print("miss match in the algorithm")
    dummy_list=[]
    dummy_list2=[]
    dummy_list3=[]
    dummy_read_order=0
    article_idx=0
    article_dict={}
    for i in range(len(polygon_type)):
        if polygon_type[i] != "Article":
            dummy_list.append(polygon_type[i])
            dummy_list2.append(from_points_to_rectangle_points(polygon_points[i]))
            dummy_list3.append(dummy_read_order)
            dummy_read_order+=1

        else :
            article_idx+=1
            article_dict[article_idx]={"Image":[],
                                       "Title":[],
                                       "Text":[],
                                       "Points":polygon_points[i]}


            image_order=0
            title_order=0
            text_order=0
            for dummy_i in range(len(dummy_list)):
                if dummy_list[dummy_i]=="Image":
                    image_order+=1
                    article_dict[article_idx]["Image"].append({"Points":dummy_list2[dummy_i],"Order":dummy_list3[dummy_i],
                                                               "Vis_Order":image_order})

                if dummy_list[dummy_i]=="Text":
                    text_order+=1
                    article_dict[article_idx]["Text"].append({"Points":dummy_list2[dummy_i],"Order":dummy_list3[dummy_i],
                                                              "Vis_Order":text_order})

                if dummy_list[dummy_i]=="Title":
                    title_order+=1
                    article_dict[article_idx]["Title"].append({"Points":dummy_list2[dummy_i],"Order":dummy_list3[dummy_i],
                                                               "Vis_Order":title_order})

            dummy_list.clear()
            dummy_list2.clear()
            dummy_list3.clear()
            dummy_read_order=0



    img =Image.open(path).convert("RGB")


    image_name=asr_path.split('/')[-1].split('.asr')[0]


    reduce_path=get_reduced_path(path,mapper_real_to_reduce)
    for key in article_dict:

        # KEY ACT AS ARTICLE INDEX


        # line seg
        os.makedirs(segmentation_json_path+"/"+reduce_path,exist_ok=True)
        with open(segmentation_json_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}.json", "w") as outfile:
            json_object = json.dumps(article_dict[key], indent=4)
            outfile.write(json_object)



        pill_mask(article_dict[key]["Points"],img.copy()).save(segmentation_json_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}.jpg")

        #
        # article

        os.makedirs(articles_path+"/"+reduce_path,exist_ok=True)
        with open(articles_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}.json", "w") as outfile:
            json_object = json.dumps(article_dict[key]["Points"], indent=4)
            outfile.write(json_object)



        pill_mask(article_dict[key]["Points"],img.copy()).save(articles_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}.jpg")

        ###############################################


        # images
        # page_00-art_00-image_00.jpg
        os.makedirs(images_path+"/"+reduce_path,exist_ok=True)
        for image in article_dict[key]["Image"]:
            pill_mask(image["Points"],img.copy()).save(images_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}-image_{str(image['Vis_Order']).zfill(2)}.jpg")

            with open(images_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}-image_{str(image['Vis_Order']).zfill(2)}.json", "w") as outfile:
                json_object = json.dumps(image["Points"], indent=4)
                outfile.write(json_object)


        ########################################
        # titles
        os.makedirs(titles_path+"/"+reduce_path,exist_ok=True)
        for title in article_dict[key]["Title"]:
            with open(titles_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}-title_{str(title['Vis_Order']).zfill(2)}.json", "w") as outfile:
                json_object = json.dumps(title["Points"], indent=4)
                outfile.write(json_object)

            pill_mask(title["Points"],img.copy()).save(titles_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}-title_{str(title['Vis_Order']).zfill(2)}.jpg")
        #################################################################
        # text
        os.makedirs(paragraph_path+"/"+reduce_path,exist_ok=True)
        for text in article_dict[key]["Text"]:
            with open(paragraph_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}-text_{str(text['Vis_Order']).zfill(2)}.json", "w") as outfile:
                json_object = json.dumps(text["Points"], indent=4)
                outfile.write(json_object)

            pill_mask(text["Points"],img.copy()).save(paragraph_path+"/"+reduce_path+f"/page_{image_name.zfill(2)}-art_{str(key).zfill(2)}-text_{str(text['Vis_Order']).zfill(2)}.jpg")

    #img.save(segmentation_json_path+"/"+reduce_path+f"/page_{image_idx}.jpg")
    log_file.write(f"done cropping \n")
    log_file.flush()

#data_path="/home/administrator/data/magz/ASR/6-7-2023/h1/المصور/باتش 5 المصور 1"
#json_path="reduced_to_real_new.json"
#mapper_real_to_reduce=read_reduced_path(json_path)
#titles_path,images_path,paragraph_path,articles_path,segmentation_json_path=define_main_paths("/home/administrator/data/magz/OCR/9-7-2023/h1/المصور/باتش 5 المصور 1/")
#asr_paths=get_asr(data_path)


for number_of_try in range(5):
    log_file=open(f"log_update_par_{number_of_try}_31-7-2023_h1_almosor",'w')
#with ProcessPoolExecutor() as executor:
#    for image_idx,asr_path in enumerate(asr_paths):
#        executor.submit(main_multi,image_idx,asr_path)


    p = mp.Pool(20)
    print("start ocr ")

    log_file.write("\n\n start ocr \n\n " )
    log_file.flush()

    for dir in [
"/home/administrator/data/magz/OCR/31-7-2023/h1/المصور/باتش 5 المصور 2/Paragraph/"
#"/home/administrator/data/magz/OCR/11-8-2023/h4/اخبار اليوم/اخر ساعة/Paragraph"
#"/home/administrator/data/magz/OCR/6-8-2023/h1/اخبار اليوم 2/Paragraph/",
#"/home/administrator/data/magz/OCR/6-8-2023/h1/الاثنين والدنيا/الاثنين/Paragraph/",
#"/home/administrator/data/magz/OCR/6-8-2023/h1/المصور/باتش 5 المصور 2/Paragraph/",
#"/home/administrator/data/magz/OCR/6-8-2023/h4/المصور/Batch 1/Paragraph/",
#"/home/administrator/data/magz/OCR/6-8-2023/h4/المصور/Batch 2/Paragraph/",
#"/home/administrator/data/magz/OCR/6-8-2023/h4/المصور/Batch 3/Paragraph/",
#"/home/administrator/data/magz/OCR/6-8-2023/h4/المصور/Batch 4/Paragraph/"
#"/home/administrator/data/magz/OCR/31-7-2023/h4/المصور/Batch 1/Paragraph/",
#"/home/administrator/data/magz/OCR/31-7-2023/h4/المصور/Batch 2/Paragraph/",#
#"/home/administrator/data/magz/OCR/31-7-2023/h4/المصور/Batch 3/Paragraph/",
#"/home/administrator/data/magz/OCR/31-7-2023/h4/المصور/Batch 4/Paragraph/",#
#"/home/administrator/data/magz/OCR/25-7-2023/h1/المصور/باتش 5 المصور 2/Paragraph/",
#"/home/administrator/data/magz/OCR/31-7-2023/h1/الاثنين والدنيا/الاثنين/Paragraph/",
]: # contain missing ["/home/administrator/data/magz/OCR/17-7-2023/h4/المصور/Batch 1/Paragraph/","/home/administrator/data/magz/OCR/17-7-2023/h1/المصور/باتش 5 المصور 2/Paragraph/"]: # ["/home/administrator/data/magz/OCR/12-7-2023_missed_images/h1/المصور/باتش 5 المصور 1/Paragraph","/home/administrator/data/magz/OCR/12-7-2023_missed_images/h1/المصور/باتش 5 المصور 2/Paragraph","/home/administrator/data/magz/OCR/9-7-2023_missed_images/h1/المصور/باتش 5 المصور 1/Paragraph"]:
        print("recognition start", dir )
        log_file.write(f"recognition start {dir}\n")
        log_file.flush()
        main_dir = dir #+"/"+reduce_path
        books = list(glob.glob(main_dir + '/**/*.jpg', recursive=True))
        books = list(set(["/".join(i.split("/")[0:-1]) for i in books]))
        print(len(books), flush=True)
        x = list(p.map(run, books))

    log_file.write(f"done recognition \n")
    log_file.write("-------------\n")
    log_file.flush()


############




#################3
