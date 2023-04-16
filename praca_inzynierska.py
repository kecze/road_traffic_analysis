import cv2
import matplotlib.pyplot as plt
import numpy as np
import tkinter
from tkinter import *
from tkinter import Tk, Canvas, Frame, BOTH
from PIL import Image as im
from PIL import ImageTk, Image
import os
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure 
from moviepy.editor import *
import glob 
from os import environ
import datetime

def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

film_name = "nagranie_chodnik.mp4"

def clear_files(dir_path):
    for filename in os.scandir(dir_path):
        if filename.is_file():
            os.remove(filename)


def exit_detect(filename):
    cap = cv2.VideoCapture(filename)
    ret, img = cap.read()


    

    scale_percent = 100 #zmian rozmiaru
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img_res = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    copy = np.copy(img_res) #kopia do przedstawiania wyniku końcowego 
    '''
    parametry do modyfikowania 

    GAUSS
    ksize - rozmiar kxk 

    HOUGH
    min_length - minimalna liczba punktów, która może stworzyć linię - propozycje krótsze są odrzucane
    max_gap - maksymalna przerwa między punktami aby dalej była linia
    '''
    ksize = 5
    min_length = 70
    max_gap = 60
    img_res = cv2.GaussianBlur(img_res, (ksize, ksize), cv2.BORDER_DEFAULT)
    gray = cv2.cvtColor(img_res, cv2.COLOR_BGR2GRAY) #zmiana na skalę szarości
    edges = cv2.Canny(gray, 100, 200) #użycie detektora Canny - wykrycie linii
    #cv2.imshow('canny', edges)

    lines = cv2.HoughLinesP(edges, 2, np.pi/180, 100, np.array([]), minLineLength=min_length, maxLineGap=max_gap)
    lines_image = display_lines(copy, lines)
    #cv2.imshow("Img", lines_image)

    key = cv2.waitKey(0)
    
    return copy, lines_image, edges, width, height



def display_lines(image, lines):
    lines_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            start = (x1, y1)
            end = (x2, y2)
            cv2.line(lines_image, start, end, (0, 0, 255), 3)
    return lines_image


def make_comparison(im1, im2, im3):
    size = (12, 8)
    rows = 2
    columns = 2

    fig = plt.figure(figsize=(size))
    fig.add_subplot(rows, columns, 1)
    plt.imshow(im1)
    plt.axis('off')
    plt.title('Oryginalna klatka')
    fig.add_subplot(rows, columns, 2)
    plt.imshow(im2)
    plt.axis('off')
    plt.title('Linie wykryte przy użyciu detekcji Hougha\n(po optymalizacji)')
    fig.add_subplot(rows, columns, 3)
    plt.imshow(im3)
    plt.axis('off')
    plt.title('Linie wykryte detektorem Canny')
    #plt.show()

counter = 0

def main():
    #czyszczenie katalogów, które będą używane 
    clear_files('C:/Users/piotr/Yolov7_StrongSORT_OSNet/charts_GUI')
    #clear_files('C:/Users/piotr/Yolov7_StrongSORT_OSNet/images_GUI')
    clear_files('C:/Users/piotr/Yolov7_StrongSORT_OSNet/results_GUI')

    scale = 0.5
    areas_avail = 5
    point_matrix = np.zeros((areas_avail*2,2),int)
    copy,lines_image, edges, width, height = exit_detect(film_name)
    make_comparison(copy, lines_image, edges)
    st_x, st_y, end_x, end_y =[], [], [], []

    def norm_chosen():
        photo = cv2.imread('images_GUI/copy.png')
        photo = cv2.resize(photo, (round(width * scale), round(height * scale)))
        cv2.imshow('Normal image', photo)
        #phototk = ImageTk.PhotoImage(image=photo)
        #Label(root, image=phototk).pack
        
        cv2.setMouseCallback('Normal image', click_event)


    def lines_chosen():
        photo = cv2.imread('images_GUI/lines_image.png')
        photo = cv2.resize(photo, (round(width * scale), round(height * scale)))
        cv2.imshow('Lines detector', photo)
        #phototk = ImageTk.PhotoImage(image=photo)
        #Label(root, image=phototk).pack
        
        cv2.setMouseCallback('Lines detector', click_event)


    def edges_chosen():
        photo = cv2.imread('images_GUI/edges.png')
        photo = cv2.resize(photo, (round(width * scale), round(height * scale)))
        cv2.imshow('Edges detector', photo)
        #phototk = ImageTk.PhotoImage(image=photo)
        #Label(root, image=phototk).pack
        
        cv2.setMouseCallback('Edges detector', click_event)
        


    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            global counter
            point_matrix[counter]= x/scale,y/scale
            
            if counter % 2 == 0:
                st_x.append(point_matrix[counter][0])
                st_y.append(point_matrix[counter][1])
            elif counter % 2 != 0:
                end_x.append(point_matrix[counter][0])
                end_y.append(point_matrix[counter][1])

            counter += 1    
    
    def show_result():
        photo = cv2.imread('images_GUI/copy.png')
        cv2.resize(photo, (width, height))
        print(counter)
        pic_size = (200, 200)
        for i in range(int(counter/2)):
            img_cropped = photo[st_y[i]:end_y[i], st_x[i]:end_x[i]]
            img_cropped = im.fromarray(img_cropped)

            resized_image = img_cropped.resize(pic_size, Image.ANTIALIAS)
            resized_image.save('images_GUI/res_cropped'+str(i)+'.png')
            image = ImageTk.PhotoImage(Image.open('images_GUI/res_cropped'+str(i)+'.png'))
            label = tkinter.Label(image=image)
            label.image = image
            label.grid(row=4, column=int(i))


    def run_detection():
        #tutaj przerabianie filmów + zapisywanie do folderu + wywyoływanie z parametrami
        with open('C:/Users/piotr/Yolov7_StrongSORT_OSNet/results/number.txt', 'w'):
            print("Creating file for saving number of cars")
        for i in range(int(counter/2)):  #tyle ile zaznaczonych obszarów
            my_clip = VideoFileClip(film_name)
            new_clip = my_clip.crop(x1=st_x[i], y1=st_y[i], x2=end_x[i], y2=end_y[i]) #przycina do zazczenia
            new_clip.write_videofile('C:/Users/piotr/Yolov7_StrongSORT_OSNet/nagrania_przyciete/input_'+str(i)+'.mp4') #zapisuje przycięte
            f = open('runs/results.txt', 'w') #otwiera wyniki zapisania
            
            time1 = datetime.datetime.now()
            os.system('python track.py --yolo-weights yolov7.pt --classes 0 1 2 3 5 7 --save-txt --source C:/Users/piotr/Yolov7_StrongSORT_OSNet/nagrania_przyciete/input_'+str(i)+'.mp4')   # wywołanie dla podanego wycięcia
            # os.system('python track.py --yolo-weights yolov7-w6.pt --classes 0 1 2 3 5 7 --save-txt --source C:/Users/piotr/Yolov7_StrongSORT_OSNet/nagraniaoficjalne_testy/nagranie_chodnik_1.mp4')   # wywołanie dla podanego wycięcia
            time2 = datetime.datetime.now()
            dif = time2 - time1
            print(dif)

            #praca na zapisanych danych po skończeniu pracy na danym nagraniu
            #wczytanie wartości do tabeli w celu dalszej analizy 
            frames = []
            ids = []
            number_f = []
            number = 0
            
            objects = []
            num_people0 = 0
            num_bikes1 = 0
            num_cars2 = 0
            num_motor3 = 0
            num_bus5 = 0
            num_truck7 = 0
            list_of_tuples = []
            list_of_tuples_unfiltred = []
            num_var = 3 #minimalna ilość wykrytych obiektów wymagana aby nastąpiło zliczenie 

            with open('runs/results.txt', 'r') as f:
                for line in f:
                    currentLine = line.split(" ")
                    frames.append(int(currentLine[0]))
                    ids.append(int(currentLine[1]))
                    objects.append(int(currentLine[9]))
                    list_of_tuples_unfiltred.append((int(currentLine[1]),int(currentLine[9])))
                    # if (int(currentLine[1]),int(currentLine[9])) not in list_of_tuples:
                    #     list_of_tuples.append((int(currentLine[1]),int(currentLine[9])))
                    if list_of_tuples_unfiltred.count((int(currentLine[1]),int(currentLine[9]))) >= num_var and (int(currentLine[1]),int(currentLine[9])) not in list_of_tuples:
                        list_of_tuples.append((int(currentLine[1]),int(currentLine[9])))
                
            for tuples in list_of_tuples:
                if tuples[1] == 0:
                    num_people0 += 1
                if tuples[1] == 1:
                    num_bikes1 += 1
                if tuples[1] == 2:
                    num_cars2 += 1
                if tuples[1] == 3:
                    num_motor3 += 1
                if tuples[1] == 5:
                    num_bus5 += 1
                if tuples[1] == 7:
                    num_truck7 += 1
            

            number = max(ids, default=0)
            number_frames = max(frames, default=0)
            start_frames = min(frames, default=0)
            with open('C:/Users/piotr/Yolov7_StrongSORT_OSNet/results/number.txt', 'a') as f:
                f.write(str(num_people0))
                f.write(' ')
                f.write(str(num_bikes1))
                f.write(' ')
                f.write(str(num_cars2))
                f.write(' ')
                f.write(str(num_motor3))
                f.write(' ')
                f.write(str(num_bus5))
                f.write(' ')
                f.write(str(num_truck7))
                f.write(' ')
                f.write(' \n')

            make_plots(frames, ids, number, i, number_frames, start_frames)

    def make_plots(frames, ids, number, i, number_frames, start_frames):
        plt.figure(figsize=(4.8, 4.8))
        plt.scatter(frames, ids, label='Wyniki detekcji')
        plt.xlabel('Numer klatki nagrania')
        plt.ylabel('Numer ID wykrytego obiektu')
        #plt.set_size_inches(10, 10)
        plt.savefig('charts_GUI/plot_'+str(i)+'.png')
        os.remove('C:/Users/piotr/Yolov7_StrongSORT_OSNet/runs/results.txt')#czyszczenie zawartości po każdym użyciu 
            
    def show_analysis():
        top = Toplevel()
        top.title('Analiza natężenia ruchu')
        top.configure(bg='#39B49B')
        top.state('zoomed')
        exits = 0
        p_s = 5
        pic_size = (200, 200)
        number = []
        num_people0 = []
        num_bikes1 = []
        num_cars2 = []
        num_motor3 = []
        num_bus5 = []
        num_truck7 = []

        with open('C:/Users/piotr/Yolov7_StrongSORT_OSNet/results/number.txt', 'r') as f:
            for line in f:
                currentLine = line.split(" ")
                num_people0.append(currentLine[0])
                num_bikes1.append(currentLine[1])
                num_cars2.append(currentLine[2])
                num_motor3.append(currentLine[3])
                num_bus5.append(currentLine[4])
                num_truck7.append(currentLine[5])

        for filename in os.scandir('C:/Users/piotr/Yolov7_StrongSORT_OSNet/charts_GUI'):
            if filename.is_file():
                exits += 1

        image_res = cv2.imread('images_GUI/copy.png') #tworzenie obrazu końcowego zawierającego zaznczone zjazdy

        for i in range(exits):
            image = Image.open('images_GUI/res_cropped'+str(i)+'.png')
            resized_image = image.resize(pic_size, Image.ANTIALIAS)
            new_image = ImageTk.PhotoImage(resized_image)
            label = tkinter.Label(image=new_image)
            label.image = new_image
            Label(top, text='Results for exit nr: {}\nPeople detected: {}\nBikes detected: {}\nCars detected: {}\nMotors detected: {}\nBuses detected: {}\nTrucks detected: {}'.format(i+1, num_people0[i], num_bikes1[i], num_cars2[i],num_motor3[i], num_bus5[i], num_truck7[i]), background="black", foreground="green").grid(ipadx = p_s, ipady = p_s, row=int(i), column=1)
            Label(top, image=new_image).grid(row=int(i), column=2)

            image = Image.open('charts_GUI/plot_'+str(i)+'.png')
            resized_image = image.resize(pic_size, Image.ANTIALIAS)
            new_image = ImageTk.PhotoImage(resized_image)
            label = tkinter.Label(image=new_image)
            label.image = new_image
            Label(top, image=new_image).grid(row=int(i), column=3)

            image = Image.open('results_GUI/results_'+str(i)+'.png')
            resized_image = image.resize(pic_size, Image.ANTIALIAS)
            new_image = ImageTk.PhotoImage(resized_image)
            label = tkinter.Label(image=new_image)
            label.image = new_image
            Label(top, image=new_image).grid(row=int(i), column=4)
            
            image_res = cv2.rectangle(image_res, (st_x[i], st_y[i]), (end_x[i], end_y[i]), (211, 26, 194), 3)
            cv2.putText(img=image_res,text='Exit {}'.format(i+1),org=(int(st_x[i]+((end_x[i]-st_x[i])/2)),int(st_y[i]+((end_y[i]-st_y[i])/2))), fontFace=0, fontScale=1, color=(211, 26, 194), thickness=3, lineType=cv2.LINE_AA)
            #image = Image.open('images_GUI/copy.png')
        scale = 50  
        width = int(image_res.shape[1] * scale / 100)
        height = int(image_res.shape[0] * scale / 100)
        dim = (width, height)     

        resized_image = cv2.resize(image_res, dim, interpolation = cv2.INTER_AREA)
        blue,green,red = cv2.split(resized_image)
        resized_image = cv2.merge((red,green,blue))
        resized_image = Image.fromarray(resized_image)

        new_image = ImageTk.PhotoImage(resized_image)
        label = tkinter.Label(image=new_image)
        label.image = new_image
        Label(top, image=new_image).place(x=780, y=0)


    btn_size = (500, 250)
    btn_size_s = 50

    #converting np.array type to jpg
    copy = im.fromarray(copy)
    copy.save('images_GUI/copy.png')
    copy_s = copy.resize(btn_size)
    copy_s.save('images_GUI/copy_s.png')

    lines_image = im.fromarray(lines_image)
    lines_image.save('images_GUI/lines_image.png')
    lines_image_s = lines_image.resize(btn_size)
    lines_image_s.save('images_GUI/lines_image_s.png')

    edges = im.fromarray(edges)
    edges.save('images_GUI/edges.png')
    edges_s = edges.resize(btn_size)
    edges_s.save('images_GUI/edges_s.png')

    root = Tk()
    root.title('Praca inzynierska Piotr Kaczmarek')
    root.iconbitmap('C:/Users/piotr/Yolov7_StrongSORT_OSNet/icon_GUI/icon1.ico')
    myLabel = Label(root, text="Wybierz dogodny widok do zaznaczenia obszaru zainteresowania")
    myLabel.grid(row=2, column=2)
    root.state('zoomed')
    #root.geometry('1500x800')
    root.configure(bg='#39B49B')

    #Creating buttons
    norm = PhotoImage(file = 'C:/Users/piotr/Yolov7_StrongSORT_OSNet/images_GUI/copy_s.png')
    but1 = Button(root, text = 'Obraz wejściowy', image=norm, command=norm_chosen)

    lines = PhotoImage(file = 'C:/Users/piotr/Yolov7_StrongSORT_OSNet/images_GUI/lines_image_s.png')
    but2 = Button(root, text = 'Obraz po obróbce z użycie detekcji Hough', image=lines, command=lines_chosen)
    but2.image = lines

    edges = PhotoImage(file = 'C:/Users/piotr/Yolov7_StrongSORT_OSNet/images_GUI/edges_s.png')
    but3 = Button(root, text = 'Obraz po obróbce z detektora Canny', image=edges, command=edges_chosen)

    but4 = Button(root, text='Pokaż wycięty obszar',padx=btn_size_s,pady=btn_size_s,command=show_result)
    but5 = Button(root, text='RUN DETECTION USING YOLOv7',padx=btn_size_s,pady=btn_size_s,command=run_detection)
    but6 = Button(root, text='Pokaż analizę wyników', padx=btn_size_s,pady=btn_size_s,command=show_analysis)
    
    but1.grid(row=1, column=0)
    but2.grid(row=2, column=0)
    but3.grid(row=3, column=0)
    but4.grid(row=3, column=3)
    but5.grid(row=2, column=3)
    but6.grid(row=1, column=3)

    root.mainloop()



if __name__ == "__main__":
    suppress_qt_warnings()
    main()