import os, os.path
import numpy as np

# Images Folder Path
imageDir = "objimages/"

# Images valid extensions
valid_image_extensions = [".jpg", ".jpeg", ".png"]
valid_image_extensions = [item.lower() for item in valid_image_extensions]

# Helper function to get all the objects based on the images 
def getObjects():
    image_path_list = []
    obj_list = []
    obj_dict_list = []
    
    #create a list all files in directory and
    #append files with a vaild extention to image_path_list
    for file in os.listdir(imageDir):
        filename = os.path.splitext(file)[0]
        extension = os.path.splitext(file)[1]
        if extension.lower() not in valid_image_extensions:
            continue
        image_path_list.append(os.path.join(imageDir, file))
        obj_list.append(filename.split('_')[0])

    # get only the unique objects
    obj_list = np.unique(obj_list).tolist()

    # get the objects name
    for name in obj_list:
        images = []
        for image in image_path_list:
            if(name == image.split('_')[0].split('/')[1]):
                images.append(image)
        
        # create the dict with the obj name and image
        obj_dict = {'name': name.replace('@', ' '), 'images': images}
        obj_dict_list.append(obj_dict)
    
    return obj_dict_list

# Helper function to check the objects folder is empty
def objectsExist():
    obj_dict_list = getObjects()
    return len(obj_dict_list) > 0

# Helper function to clear the objects folder
def clearObjects():
    for the_file in os.listdir(imageDir):
        extension = os.path.splitext(the_file)[1]

        if extension.lower() in valid_image_extensions:
            file_path = os.path.join(imageDir, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
