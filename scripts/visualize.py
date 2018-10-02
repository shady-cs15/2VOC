import cv2

vid_id = 'P_01'
vid_name = '../videos/'+vid_id+'.MP4'
annotation_file = '../ADL_annotations/object_annotation/object_annot_'+vid_id+'.txt'

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

frame_id = 0
while True:
    ret, frame = cap.read()
    if ret is False:
        break
    if frame_id in annotations:
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        print frame.shape
        cur_annotations = annotations[frame_id]
        for (rect, class_name) in cur_annotations:
            cv2.rectangle(frame, (int(rect[0]), int(rect[1])), (int(rect[2]), int(rect[3])), (0, 255, 0), 2)
            cv2.putText(frame, class_name, (int(rect[0]), int(rect[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow(vid_name.split('/')[-1], frame)
        k = cv2.waitKey(0)
        if k == 27:
            break
    frame_id +=1
