import cv2
import time
from datetime import datetime

def noise():
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    fps = 0

    while True:
        ret, frame1 = cap.read()
        ret, frame2 = cap.read()

        # Motion detection logic
        diff = cv2.absdiff(frame2, frame1)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        diff = cv2.blur(diff, (5, 5))
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Detect and display motion
        if len(contours) > 0:
            max_cnt = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_cnt)
            if cv2.contourArea(max_cnt) > 500:  # Ignore small motions
                cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame1, "MOTION", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                print(f"Motion detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            cv2.putText(frame1, "NO-MOTION", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

        # Show the frame
        cv2.imshow("Motion Detection - Press ESC to Exit", frame1)

        # FPS counter
        fps += 1
        elapsed_time = time.time() - start_time
        if elapsed_time > 1:
            print(f"FPS: {fps}")
            fps = 0
            start_time = time.time()

        # Exit on ESC key
        if cv2.waitKey(1) == 27:
            cap.release()
            cv2.destroyAllWindows()
            break

