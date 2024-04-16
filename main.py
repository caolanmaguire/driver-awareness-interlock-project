"""Main file - multi threading implemented to run multiple camera feeds at once"""
import cv2
import mediapipe as mp
from threading import Thread
import dlib
import numpy as np
import time
import pygame
import pygame
from datetime import time, datetime
from math import pi, cos, sin
import serial
import time
import psutil
import obd

def face_pose_analysis() -> None:
    """analysis for face pose estimation

    Args:
        mp_face_mesh (_type_): _description_
        cap (_type_): _description_
        mp_drawing (_type_): _description_
        mp_drawing_styles (_type_): _description_
    """
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh

    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    cap = cv2.VideoCapture(1)
    global face_pose_x, face_pose_var

    # DETECT THE FACE LANDMARKS
    with mp_face_mesh.FaceMesh\
        (min_detection_confidence=0.7, min_tracking_confidence=0.7) as face_mesh:
        while True:
            success, image = cap.read()
            # Flip the image horizontally and convert the color space from BGR to RGB
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance
            image.flags.writeable = False
            # Detect the face landmarks
            results = face_mesh.process(image)
            # To improve performance
            image.flags.writeable = True
            # Convert back to the BGR color space
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            img_h, img_w, img_c = image.shape
            face_3d = []
            face_2d = []
            # Draw the face mesh annotations on the image.
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    for idx, lm in enumerate(face_landmarks.landmark):
                        if idx == 33 or idx == 263 or idx == 1 \
                            or idx == 61 or idx == 291 or idx == 199:
                            if idx ==1:
                                nose_2d = (lm.x * img_w, lm.y * img_h)
                                nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)
                            x_point, y_point = int(lm.x * img_w), int(lm.y * img_h)

                            #Get the 2d coordinates
                            face_2d.append([x_point,y_point])

                            #3d coordinates
                            face_3d.append([x_point,y_point, lm.z])
                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)

                    #The camera matrix
                    focal_length = 1 * img_w

                    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                            [0, focal_length, img_w / 2],
                                            [0, 0, 1]])
                    dist_matrix = np.zeros((4,1), dtype=np.float64)
                    success, rot_vec, trans_vec = cv2.solvePnP\
                        (face_3d, face_2d, cam_matrix, dist_matrix)
                    rmat, jac = cv2.Rodrigues(rot_vec)
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                    x = angles[0] * 360
                    y = angles[1] * 360
                    z = angles[2] * 360

                    global rpm_state
                    rpm_state = y

                    face_pose_x = angles[0] * 360

                    if y < -10:
                        # print('looking left')
                        face_pose_var = 'looking left'
                    elif y > 10:
                        # print('looking right')
                        face_pose_var = 'looking right'
                    elif x < -10:
                        print('looking down')
                        face_pose_var ='looking down'
                    elif x > 10:
                        # print('looking up')
                        face_pose_var = 'looking up'
                    else:
                        # print('looking forward')
                        face_pose_var = 'looking forward'
                    

                    nose_3d_projection, jacobian = cv2.projectPoints\
                        (nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

                    point_1 = (int(nose_2d[0]), int(nose_2d[1]))
                    point_2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))
                    cv2.line(image, point_1, point_2, (255,0,0), 3)
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_tesselation_style())

            # Display the image
            # cv2.imshow('face pose estimation', image)
            # Terminate the process
            if cv2.waitKey(5) & 0xFF == 27:
                break

def eyelid_detection() -> None:
    # Initialize the face detector and shape predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    # Function to calculate the eye aspect ratio (EAR)
    def eye_aspect_ratio(eye):
        # Compute the euclidean distances between the two sets of vertical eye landmarks
        A = ((eye[1][0] - eye[5][0])**2 + (eye[1][1] - eye[5][1])**2)**0.5
        B = ((eye[2][0] - eye[4][0])**2 + (eye[2][1] - eye[4][1])**2)**0.5
        # Compute the euclidean distance between the horizontal eye landmark
        C = ((eye[0][0] - eye[3][0])**2 + (eye[0][1] - eye[3][1])**2)**0.5
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear

    # Load the webcam
    cap = cv2.VideoCapture(1)

    # global variable eyelidstate
    global eyelid_state

    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = detector(gray)

        eyelid_state = 0

        for face in faces:
            # Predict facial landmarks
            shape = predictor(gray, face)
            shape = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

            # Extract left and right eye landmarks
            left_eye = shape[36:42]
            right_eye = shape[42:48]

            # Calculate eye aspect ratio (EAR)
            left_ear = eye_aspect_ratio(left_eye)
            right_ear = eye_aspect_ratio(right_eye)

            # Average the EAR of both eyes
            ear = (left_ear + right_ear) / 2.0

            # Draw the detected eyes on the frame
            for (x, y) in left_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            for (x, y) in right_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # Check if the eye aspect ratio is below the threshold (eyes closed)
            if ear < 0.2:
                # if eyes_closed_timestamp != None:
                
                try:
                    print(time.time() - eyes_closed_timestamp)
                    if time.time() - eyes_closed_timestamp > 5:
                        eyelid_state = 'Driver deemed unconscious'
                    else:
                        eyelid_state = 'Eyes Closed'
                except Exception as e:
                    print(e)

                # eyelid_state = 'Eyes Closed'
                cv2.putText(frame, "Eyes Closed" + str(eyes_closed_timestamp), (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                eyes_closed_timestamp = time.time()
                # eyes_closed_timestamp = None
                eyelid_state = 'Eyes Open'

        # Display the frame
        cv2.imshow("Frame", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close all windows
    cap.release()
    cv2.destroyAllWindows()


def display() -> None:

    bg = pygame.image.load("dashboard-background.png")

    # try:
    #     # open a serial connection
    #     s = serial.Serial("COM3", 115200)
    # except:
    #     print('no com channel available')


    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    PINK = (227, 0, 166)
    NAVY = (0, 0, 53)
    GRAY = (178, 170, 234)

    THE_STRING = "MM" + ':' + "SS" + ':' + "MS"

    WIDTH, HEIGHT = 1080, 450
    center = (510, HEIGHT / 2)
    clock_radius = 200
    screen = pygame.display.set_mode((WIDTH, HEIGHT))#, pygame.NOFRAME)
    developer_screen = pygame.display.set_mode((WIDTH, HEIGHT))#, pygame.NOFRAME)


    # car states -> change based on  how you chose to read your data
    speed_state = 0
    current_time = 0
    best_lap = "00:00:00"
    past_lap = "00:00:00"


    def write_text(text, size, position):
        font = pygame.font.SysFont("copperplategothic", size, True, False)
        text = font.render(text, True, WHITE)
        text_rect = text.get_rect(center=position)
        screen.blit(text, text_rect)


    def render_time(start, size, position):
        hundredth_of_a_second = int(str(start)[-2:])  # hundredth of a second
        time_in_ms = time((start // 1000) // 3600, ((start // 1000) // 60 % 60), (start // 1000) % 60)
        time_string = "{}{}{:02d}".format(time_in_ms.strftime("%M:%S"), ':', hundredth_of_a_second)
        write_text(time_string, size, position)


    # theta is in degrees
    def polar_to_cartesian(r, theta, width_center, height_center):
        x = r * sin(pi * theta / 180)
        y = r * cos(pi * theta / 180)
        return x + width_center, -(y - height_center)


    # rg_end is non-inclusive
    def clock_nums(rg_strt, rg_end, mult, size, r, angle, strt_angle, width_center, height_center):
        for number in range(rg_strt, rg_end, mult):
            write_text(str(number), size,
                    polar_to_cartesian(r, ((number / mult) * angle + strt_angle), width_center, height_center))


    def ticks(rg_strt, rg_end, r, angle, strt_angle, width_center, height_center):
        for number in range(rg_strt, rg_end):
            tick_start = polar_to_cartesian(r, (number * angle + strt_angle), width_center, height_center)
            if number % 10 == 0:
                tick_end = polar_to_cartesian(r - 25, (number * angle + strt_angle), width_center, height_center)
                pygame.draw.line(screen, GRAY, tick_start, tick_end, 2)
            elif number % 5 == 0:
                tick_end = polar_to_cartesian(r - 20, (number * angle + strt_angle), width_center, height_center)
                pygame.draw.line(screen, GRAY, tick_start, tick_end, 2)
            else:
                tick_end = polar_to_cartesian(r - 15, (number * angle + strt_angle), width_center, height_center)
                pygame.draw.line(screen, GRAY, tick_start, tick_end, 2)
    def pygame_task():
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Dashboard")
        global speed
       
        gameExit = False

        while not gameExit:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
            # screen.fill(NAVY)

            #INSIDE OF THE GAME LOOP
            developer_screen.blit(bg, (0, 0))

            # SPEEDOMETER
            # gauge label
            write_text("Speedometer", 20, (WIDTH / 4, (HEIGHT / 2) - (clock_radius / 2) - 35))
            # clock numbers
            clock_nums(0, 145, 20, 40, (clock_radius - 65), 38.57143, 223.2, (WIDTH / 4), (HEIGHT / 2) + 65)
            # ticks
            ticks(0, 36, (clock_radius - 15), 7.714286, 223.2, WIDTH / 4, (HEIGHT / 2) + 65)
            # speed = speed_state
            # if speed < 0:
            #     speed = 0
            # if speed > 35:
            #     speed = 35
            # speed = 0
            
            try:
                msg = s.readline()
                if msg == b'0\r\n':
                    if speed != 0:
                        speed = speed - 2
                elif msg == b'1\r\n':
                    if speed >34:
                        print('woah! slow down there cowboy!')
                    else:
                        speed = speed + 2
            except:
                speed = 0
            theta = (speed * (270.0 / 35.0)) + (223.2 - (270.0 / 35.0))
            # draw line on gauge indicating current speed
            pygame.draw.line(developer_screen, RED, ((WIDTH / 2) / 2, HEIGHT / 2 + 45),
                            polar_to_cartesian(140, theta, WIDTH / 4, (HEIGHT / 2) + 45), 4)
            # print speed below gauge
            str_speed = str(speed)
            pygame.draw.rect(developer_screen, GRAY, [WIDTH / 4.8, HEIGHT - 55, WIDTH / 12, HEIGHT / 9], 3)
            write_text(str_speed, 50, (WIDTH / 4, (HEIGHT - 30)))

            # DRIVER VISIBILITY
            # gauge label
            write_text("DRIVER VISIBILITY", 20, ((WIDTH / 4) * 3, (HEIGHT / 2) - (clock_radius / 2) - 35))
            theta = ((rpm_state + 25) * (270.0 / 50.0)) + (223.2 - (270.0 / 50.0))
            # draw line on gauge indicating current RPM
            pygame.draw.line(developer_screen, RED, (((WIDTH / 4) * 3), (HEIGHT / 2) + 45),
                            polar_to_cartesian(140, theta, (WIDTH / 4) * 3, (HEIGHT / 2) + 45), 4)
            
            theta = ((rpm_state + 30) * (270.0 / 50.0)) + (223.2 - (270.0 / 50.0))
            # draw line on gauge indicating current RPM
            pygame.draw.line(developer_screen, RED, (((WIDTH / 4) * 3), (HEIGHT / 2) + 45),
                            polar_to_cartesian(140, theta, (WIDTH / 4) * 3, (HEIGHT / 2) + 45), 4)
            
            theta = ((rpm_state + 20) * (270.0 / 50.0)) + (223.2 - (270.0 / 50.0))
            # draw line on gauge indicating current RPM
            pygame.draw.line(developer_screen, RED, (((WIDTH / 4) * 3), (HEIGHT / 2) + 45),
                            polar_to_cartesian(140, theta, (WIDTH / 4) * 3, (HEIGHT / 2) + 45), 4)


            now = datetime.now()
            formatted = now.strftime("%H:%M:%S")
            write_text(formatted, 15, ((WIDTH - (WIDTH/2)),10))
            
            battery = psutil.sensors_battery()
            write_text(str(battery.percent) + '% Battery', 15, ((WIDTH-70),10))
            # global runtime
            write_text('runtime @ ' + str(runtime), 15, (70,10))

            # Penalty label todo
            # write_text('formatted', 40, ((WIDTH - (WIDTH/2)),20))

            pygame.display.flip()
            clock.tick(60)
    
    pygame_task()


def obdScanner() -> None:

    # global speed

    connection = obd.Async("COM5")

    def new_rpm(r):
        print (int(float(str(r).split(' ')[0])))
        global speed
        speed = int(float(str(r).split(' ')[0]))
    
    def check_runtime(r):
        print(int(float(str(r).split(' ')[0])))
        global runtime
        runtime = int(float(str(r).split(' ')[0]))
    
    connection.watch(obd.commands.RPM, callback=new_rpm)
    connection.watch(obd.commands.RUN_TIME, callback=check_runtime)

    connection.start()

    # the callback will now be fired upon receipt of new values

    time.sleep(30)
    connection.stop()


if __name__ == '__main__':

    #define global variables
    face_pose_var = 0
    eyelid_state = 0
    rpm_state = 0
    speed = 0
    runtime = 0

    thread1 = Thread( target=face_pose_analysis, args=() )
    thread2 = Thread( target=eyelid_detection, args=() )
    thread3 = Thread( target=display, args=() )
    # thread4 = Thread( target=obdScanner)

    thread1.start()
    thread2.start()
    thread3.start()
    # thread4.start()

    # cap.release()
    cv2.destroyAllWindows()
