import cv2
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom as minidom

vid_id = 'P_01'
vid_name = '../videos/'+vid_id+'.MP4'
annotation_file = '../ADL_annotations/object_annotation/object_annot_'+vid_id+'.txt'
jpeg_dir = '../out/JPEGImages'
xml_dir = '../out/Annotations'


annotations = {}
with open(annotation_file, 'r') as f:
    lines = f.readlines()
    for line in lines:
        data = line.split()
        assert len(data)==8
        f_id = int(data[5])
        if f_id not in annotations:
            annotations[f_id] = [(data[1: 5], data[7])]
        else:
            annotations[f_id].append((data[1: 5], data[7]))


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
    if frame_id in annotations:
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        h, w, _ = frame.shape
        cur_annotations = annotations[frame_id]
        for (rect, class_name) in cur_annotations:
            xmin = min(int(rect[0]), int(rect[2]))
            xmax = max(int(rect[0]), int(rect[2]))
            ymin = min(int(rect[1]), int(rect[3]))
            ymax = max(int(rect[1]), int(rect[3]))
            object_root = SubElement(top, 'object')
            object_type = class_name
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

        xmlstr = minidom.parseString(tostring(top)).toprettyxml(indent="    ")
        anno_file = os.path.join(xml_dir, vid_id+'_'+str(frame_id)+'.xml')
        with open(anno_file, "w") as f:
            f.write(xmlstr)
        
        image_file = os.path.join(jpeg_dir, vid_id+'_'+str(frame_id)+'.jpg')
        cv2.imwrite(image_file, frame)
        #break
    frame_id +=1
