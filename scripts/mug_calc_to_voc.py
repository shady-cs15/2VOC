import cv2
import os
import json
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as minidom
import argparse

vid_dir = '/home/schakra1/datasets/CUSTOM/videos'
ann_dir = '/home/schakra1/datasets/CUSTOM/annotations'
vid_ext = '.mp4'
ann_ext = '.json'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('vid_id', type=str, help='eg. 104')
    parser.add_argument('out_img_dir', type=str, default='/home/schakra1/packages/tf-faster-rcnn/data/mug_calc_vid/JPEGImages'\
                                                    , help='output image directory')
    parser.add_argument('out_xml_dir', type=str, default='/home/schakra1/packages/tf-faster-rcnn/data/mug_calc_vid/Annotations'\
                                                    , help='output annotation directory')
    args = parser.parse_args()
    return args


def get_str_f_id(f_id, l=6):
    f_id = str(f_id)
    assert len(f_id)<=6
    return '0'*(l-len(f_id))+f_id


def get_box_list_from_map(map):
    xmin = map['x']
    ymin = map['y']
    xmax = xmin + map['w']
    ymax = ymin + map['h']
    return [xmin, ymin, xmax, ymax]

def cls_map(class_name):
    if class_name in ['mug1', 'Mug1', '   mug1']:
        return 'mug1'
    elif class_name in ['calculator', 'Calculator', 'sharpner']:
        return 'calculator'


args = parse_args()
vid_name = os.path.join(vid_dir, args.vid_id + vid_ext)
annotation_file = os.path.join(ann_dir, args.vid_id + ann_ext)
jpeg_dir = args.out_img_dir
xml_dir = args.out_xml_dir

annotations = {}
all_objs = json.load(open(annotation_file, 'r'))
for f_id in range(len(all_objs)):
    f_boxes = []
    for obj in all_objs[f_id]:
        f_boxes.append((get_box_list_from_map(all_objs[f_id][obj]), obj))
    if len(f_boxes)>0:
        annotations[f_id]=f_boxes

cap = cv2.VideoCapture(vid_name)
if not cap.isOpened():
    print 'video not initialised!'

if not os.path.exists(jpeg_dir):
    os.makedirs(jpeg_dir)
if not os.path.exists(xml_dir):
    os.makedirs(xml_dir)

frame_id = 0
while True:
    ret, frame = cap.read()
    if ret is False:
        break
    top = Element('annotation')
    if frame_id > len(annotations):
        break
    if frame_id in annotations:
        h, w, _ = frame.shape
        cur_annotations = annotations[frame_id]
        for (rect, class_name) in cur_annotations:
            xmin = min(int(rect[0]), int(rect[2]))
            xmax = max(int(rect[0]), int(rect[2]))
            ymin = min(int(rect[1]), int(rect[3]))
            ymax = max(int(rect[1]), int(rect[3]))
            object_root = SubElement(top, 'object')
            object_type = cls_map(class_name)
            object_type_entry = SubElement(object_root, 'name')
            object_type_entry.text = str(object_type)
            object_bndbox_entry = SubElement(object_root, 'bndbox')
            x_min_entry = SubElement(object_bndbox_entry, 'xmin')
            x_min_entry.text = '%d'%(max(1, xmin))
            x_max_entry = SubElement(object_bndbox_entry, 'xmax')
            x_max_entry.text = '%d'%(min(w, xmax))
            y_min_entry = SubElement(object_bndbox_entry, 'ymin')
            y_min_entry.text = '%d'%(max(1, ymin))
            y_max_entry = SubElement(object_bndbox_entry, 'ymax')
            y_max_entry.text = '%d'%(min(h, ymax))
            difficult_entry = SubElement(object_root, 'difficult')
            difficult_entry.text = '0'
            
            # for visualisation, comment
            #cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255))
            #cv2.putText(frame, cls_map(class_name), (xmin+20, ymin+20), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255))

        xmlstr = minidom.parseString(tostring(top)).toprettyxml(indent="    ")
        anno_file = os.path.join(xml_dir, vid_id+'_'+get_str_f_id(frame_id)+'.xml')
        with open(anno_file, "w") as f:
            f.write(xmlstr)
        
        image_file = os.path.join(jpeg_dir, vid_id+'_'+str(frame_id)+'.jpg')
        cv2.imwrite(image_file, frame)
        #k = cv2.waitKey(33)
        #if k == 27:
        #    break

        #image_file = os.path.join(jpeg_dir, vid_id+'_'+str(frame_id)+'.jpg')
        #cv2.imwrite(image_file, frame)
        #break
    frame_id +=1

