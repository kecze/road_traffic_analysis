import cv2

'''format danych 
0 - klatka
1 - identyfikator 
2 - x
3 - y 
4 - wysok
5 - szerok 
9 - klasa'''

film_path = "C:/Users/piotr/Yolov7_StrongSORT_OSNet/test_koncowy/test5.mp4"
frames, ids, x, y, w, h, objects, list_of_tuples, list_of_tuples_unfiltred = [], [], [], [], [], [], [], [], []
num_var = 7 #zmienna określająca liczbę detekcji po której następuje zliczenie

with open('C:/Users/piotr/Yolov7_StrongSORT_OSNet/test_koncowy/test5.txt', 'r') as f:
    for line in f:
        currentLine = line.split(" ")
        frames.append(int(currentLine[0]))
        ids.append(int(currentLine[1]))
        x.append(int(currentLine[2]))
        y.append(int(currentLine[3]))
        w.append(int(currentLine[4]))
        h.append(int(currentLine[5]))
        objects.append(int(currentLine[9]))
        list_of_tuples_unfiltred.append((int(currentLine[0]), int(currentLine[1]), int(currentLine[2]), int(currentLine[3]), int(currentLine[4]), int(currentLine[5]), int(currentLine[9])))

cap = cv2.VideoCapture(film_path)
success, img = cap.read()
fno = 0
frame_cnt = 0

id_list, number_list, id_list_all = [], [], []
number = 0 
num_id_dict = {}


while success:
    frame_cnt += 1 #licznik klatek 
    for tuple in list_of_tuples_unfiltred:            #sprawdza dla wszystkich wykryć
        id_list_all.append(tuple[1]) #dodaje id do listy wszystkich id z powtórzeniami  
        if tuple[0] == frame_cnt:  #sprawdza czy dla obecnej klatki są wykrycia 
            if tuple[1] not in id_list:  #lista zawierająca każdy numer ID tylko raz
                id_list.append(tuple[1])
                if id_list_all.count(tuple[1]) >= num_var: #sprawdza czy występuje ogólnie więcej niż num_var razy 
                    num_id_dict[tuple[1]] = number 
                    cv2.putText(img=img, text = str(number), org = (tuple[2] + int(tuple[4]/2), tuple[3]+ int(tuple[5]/2)),fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, color = (251, 48, 239),thickness =  3)  
                    number += 1
            else:
                if id_list_all.count(tuple[1]) >= num_var:
                    cv2.putText(img=img, text = str(num_id_dict[tuple[1]]), org = (tuple[2] + int(tuple[4]/2), tuple[3]+ int(tuple[5]/2)),fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, color = (251, 48, 239),thickness =  3)
            cv2.circle(img, (tuple[2] + int(tuple[4]/2), tuple[3]+ int(tuple[5]/2)), 4, (0,120, 240), 2)
    cv2.imshow('wyniki', img)
    success, img = cap.read()
    key = cv2.waitKey(10)#pauses for x miliseconds before fetching next image
    if key == 27:#if ESC is pressed, exit loop
        cv2.destroyAllWindows()

