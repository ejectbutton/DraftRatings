import os
import math
import requests
from os import path
from PIL import Image
from io import BytesIO


ratings=['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F','SB']
working_dir='./LCI'
start_format_csv='DayOneTiers.csv'
end_format_csv='EndSeasonTiers.csv'

start_file = open(f'{working_dir}/{start_format_csv}', 'r')
start_dict = {}

if not path.exists(f'{working_dir}/images'):
    os.makedirs(f'{working_dir}/images')
if not path.exists(f'{working_dir}/compareResults/'):
    os.makedirs(f'{working_dir}/compareResults/')

for line in start_file:
    card_name = line.split(',')[0]
    if line[0] == "\"":
        card_name = line.split('"')[1]
        line = line.split('"')[2]
    start_dict[card_name] = line.split(',')[4]
    if not path.exists(f'{working_dir}/images/{card_name}.jpg'):
        response = requests.get(line.split(',')[8])
        img = Image.open(BytesIO(response.content))
        img.save(f'{working_dir}/images/{card_name}.jpg')

end_file = open(f'{working_dir}/{end_format_csv}', 'r')
end_dict = {}
for line in end_file:
    card_name = line.split(',')[0]
    if line[0] == "\"":
        card_name = line.split('"')[1]
        line = line.split('"')[2]
    end_dict[card_name] = line.split(',')[4]

accuracy_img_dict = {}
accuracy_count = {}
for card in start_dict.keys():
    start_rating = start_dict[card]
    end_rating = end_dict[card]

    start_rating_val = ratings.index(start_rating)
    end_rating_val = ratings.index(end_rating)

    diff = end_rating_val - start_rating_val
    diff_key = str(diff)
    card_image = Image.open(f'{working_dir}/images/{card}.jpg')
    if diff_key not in accuracy_img_dict:
        accuracy_img_dict[diff_key] = card_image
        accuracy_count[diff_key] = 1
    else:
        new_img = Image.new('RGB',(
            min(card_image.size[0]*5,card_image.size[0]*(1+accuracy_count[diff_key])),
            card_image.size[1]*(1+math.floor(accuracy_count[diff_key]/5))
            ), (0,0,0))
        new_img.paste(accuracy_img_dict[diff_key],(0,0))
        new_img.paste(card_image,(
            card_image.size[0]*(accuracy_count[diff_key] % 5),
            card_image.size[1]*math.floor(accuracy_count[diff_key]/5)
            ))

        accuracy_count[diff_key] = accuracy_count[diff_key] + 1
        accuracy_img_dict[diff_key] = new_img

for diff_image in accuracy_img_dict.keys():
    accuracy_img_dict[diff_image].save(f'{working_dir}/compareResults/{diff_image}.jpg')
