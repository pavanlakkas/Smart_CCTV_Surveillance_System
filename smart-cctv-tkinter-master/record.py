import cv2
import os
from datetime import datetime

def record():
    cap = cv2.VideoCapture(0)

    # Create recordings folder if it doesn't exist
    if not os.path.exists('recordings'):
        os.makedirs('recordings')

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None
    recording = False

    while True:
        _, frame = cap.read()

        # Add timestamp
        cv2.putText(frame, f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', (50,50), cv2.FONT_HERSHEY_COMPLEX,
                        0.6, (255,255,255), 2)

        # Control recording with the 'r' key
        if cv2.waitKey(1) == ord('r'):
            if not recording:
                recording = True
                out = cv2.VideoWriter(f'recordings/{datetime.now().strftime("%H-%M-%S")}.avi', fourcc, 20.0, (640, 480))
                print("Recording started...")
            else:
                recording = False
                out.release()  # Stop recording
                print("Recording stopped.")

        if recording:
            out.write(frame)

        # Display frame
        cv2.imshow("Press 'r' to start/stop recording. Press ESC to exit.", frame)

        # Exit on ESC key
        if cv2.waitKey(1) == 27:
            cap.release()
            cv2.destroyAllWindows()
            break
