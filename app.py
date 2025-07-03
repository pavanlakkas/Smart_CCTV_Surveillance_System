from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO
from detection import CCTVDetector
import cv2
import threading
import time
from twilio.rest import Client
import datetime
import os

app = Flask(__name__)
socketio = SocketIO(app)
detector = CCTVDetector()

# Configuration
## TWILIO_SID = 'Twilio_SID_here'
 ## TWILIO_TOKEN = 'Twilio_Token_here'
## TWILIO_NUMBER = '+1234567890'  # Your Twilio phone number
# Replace with your phone number
## YOUR_NUMBER = 'your_phone_number_here'
## client = Client(TWILIO_SID, TWILIO_TOKEN)

# Global States
system_state = {
    'recording': False,
    'fire_detection': False,
    'object_detection': False,
    'live_monitoring': False,
    'alert_cooldown': time.time()
}

recording_DIR="recordings"
if not os.path.exists(recording_DIR):
    os.makedirs(recording_DIR)

# Video Capture
cap = cv2.VideoCapture(0)
recording = None

def send_sms(message):
    if time.time() - system_state['alert_cooldown'] > 60:
        try:
            client.messages.create(
                body=f"SECURITY ALERT: {message}",
                from_=TWILIO_NUMBER,
                to=YOUR_NUMBER
            )
            system_state['alert_cooldown'] = time.time()
            socketio.emit('alert', {'message': message})
            print(f"SMS Sent: {message}")
        except Exception as e:
            print(f"SMS Error: {e}")

def generate_frames():
    global recording
    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to read frame from camera.")
            break
            
        alert_message = []
        danger_detected = False
        
        # Fire Detection
        if system_state['fire_detection'] or system_state['live_monitoring']:
            fires = detector.detect_fire(frame)
            if len(fires) > 0:
                alert_message.append("Fire detected!")
                danger_detected = True
                for (x, y, w, h) in fires:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), detector.colors['fire'], 2)
                    cv2.putText(frame, 'Fire', (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # Object Detection
        if system_state['object_detection'] or system_state['live_monitoring']:
            all_boxes, all_classes, danger_boxes = detector.detect_objects(frame)
            
            # Draw all objects
            for i, (x, y, w, h) in enumerate(all_boxes):
                class_name = detector.classes[all_classes[i]]
                color = detector.colors['danger'] if (x,y,w,h) in danger_boxes else detector.colors['normal']
                thickness = 2 if color == detector.colors['danger'] else 1
                
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)
                cv2.putText(frame, f"{class_name}", (x, y-5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

            # Check for dangerous objects
            if danger_boxes:
                danger_detected = True
                detected_items = list(set([detector.classes[all_classes[i]] 
                                       for i, box in enumerate(all_boxes) 
                                       if box in danger_boxes]))
                alert_message.append(f"Danger: {', '.join(detected_items)}")

        # Trigger alerts and recording
        if danger_detected:
            send_sms(" ".join(alert_message))
            if not system_state['recording']:
                system_state['recording'] = True
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    h, w, _ = frame.shape
                    recording = cv2.VideoWriter(f"recording_{ts}.mp4", 
                                              cv2.VideoWriter_fourcc(*'mp4v'), 
                                              20, (w, h))
                except Exception as e:
                    print(f"MP4 Error: {e}")
                    recording = cv2.VideoWriter(f"recording_{ts}.avi", 
                                              cv2.VideoWriter_fourcc(*'XVID'), 
                                              20, (w, h))

        # Handle recording
        if system_state['recording'] and recording is not None:
            recording.write(frame)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame.")
            continue
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('dashboard.html', system_state=system_state)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/control/<command>')
def control(command):
    if command == 'toggle_recording':
        system_state['recording'] = not system_state['recording']
    elif command == 'toggle_fire':
        system_state['fire_detection'] = not system_state['fire_detection']
    elif command == 'toggle_object':
        system_state['object_detection'] = not system_state['object_detection']
    elif command == 'toggle_monitoring':
        system_state['live_monitoring'] = not system_state['live_monitoring']
    elif command == 'exit':
        system_state.update({
            'recording': False,
            'fire_detection': False,
            'object_detection': False,
            'live_monitoring': False
        })
        if recording:
            recording.release()
        cap.release()
        cv2.destroyAllWindows()
    return jsonify(system_state)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)