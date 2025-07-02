import cv2

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Define video writer with dynamic filename
output_filename = input("Enter output filename (e.g., output.avi): ") or "output.avi"
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_filename, fourcc, 20.0, (640, 480))

print("Recording... Press ESC to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        out.write(frame)  # Save frame to file
        cv2.imshow("Live Recording", frame)  # Show live feed

        # Exit on ESC key or if window is closed
        if cv2.waitKey(1) == 27 or cv2.getWindowProperty("Live Recording", cv2.WND_PROP_VISIBLE) < 1:
            break
except Exception as e:
    print(f"Error: {e}")
finally:
    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Recording saved as {output_filename}.")
