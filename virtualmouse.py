import cv2
import mediapipe as mp
import pyautogui
import time

pyautogui.FAILSAFE = True
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils
plocX, plocY = 0, 0
clocX, clocY = 0, 0
is_dragging = False
has_clicked = False  # Track if click has been performed
last_click_time = 0  # Initialize the last click time
click_delay = 10  # Set the click delay to 10 seconds
cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

while True:
    _, img = cap.read()
    img = cv2.flip(img, 1)
    img_height, img_width, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

        # For Right Hand
    if results.multi_hand_landmarks:
        for L_hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = (
                    results.multi_handedness[L_hand_index].classification[0].label
                )
            if handedness != "Right":
                continue

            landmarks = hand_landmarks.landmark
            fingers_open = [False, False, False, False]
            thumb_open = False
            tip_ids = [
                    mp_hands.HandLandmark.THUMB_TIP,
                    mp_hands.HandLandmark.INDEX_FINGER_TIP,
                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                    mp_hands.HandLandmark.RING_FINGER_TIP,
                    mp_hands.HandLandmark.PINKY_TIP,
                ]
            finger_tips = [landmarks[tip_id] for tip_id in tip_ids]
                # Thumb
            pseudo_fix_key = landmarks[2].x
            if not (
                    landmarks[3].x < pseudo_fix_key and landmarks[4].x < pseudo_fix_key
                ):
                thumb_open = True
                # Index Finger
            pseudo_fix_key = landmarks[6].y
            if landmarks[7].y < pseudo_fix_key and landmarks[8].y < pseudo_fix_key:
                fingers_open[0] = True
                # Middle Finger
            pseudo_fix_key = landmarks[10].y
            if (
                    landmarks[11].y < pseudo_fix_key
                    and landmarks[12].y < pseudo_fix_key
                ):
                fingers_open[1] = True
                # Ring Finger
            pseudo_fix_key = landmarks[14].y
            if (
                    landmarks[15].y < pseudo_fix_key
                    and landmarks[16].y < pseudo_fix_key
                ):
                fingers_open[2] = True
                # Pinky
            pseudo_fix_key = landmarks[18].y
            if (
                    landmarks[19].y < pseudo_fix_key
                    and landmarks[20].y < pseudo_fix_key
                ):
                fingers_open[3] = True
                # Gesture recognition,V-shape: Cursor-moving state
            if fingers_open == [1, 1, 0, 0]:  # Ignored thumb for anlge issue
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False
                has_clicked = False  # Reset click state
                x = int(finger_tips[1].x * screen_width)
                y = int(finger_tips[1].y * screen_height)
                    # Smoothing formula
                clocX = plocX + (x - plocX) / 5
                clocY = plocY + (y - plocY) / 5
                pyautogui.moveTo(clocX, clocY)
                plocX, plocY = clocX, clocY
            
            elif (
                    fingers_open == [1, 0, 0, 0] and not has_clicked
                ):  # Only index finger open: Left click
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False
                if time.time() - last_click_time > click_delay:  # Check the click delay
                    pyautogui.click()
                    has_clicked = True  # Set click state to prevent multiple clicks
                    last_click_time = time.time()  # Update the last click time
            
            elif (
                    fingers_open == [0, 1, 0, 0] and not has_clicked
                ):  # Only middle finger open: Right click
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False
                if time.time() - last_click_time > click_delay:  # Check the click delay
                    pyautogui.rightClick()
                    has_clicked = True  # Set click state to prevent multiple clicks
                    last_click_time = time.time()  # Update the last click time
            
            elif (
                    fingers_open == [1, 1, 0, 1] and not has_clicked
                ):  # ring finger closed: Double click
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False
                if time.time() - last_click_time > click_delay:  # Check the click delay
                    pyautogui.doubleClick()
                    has_clicked = True  # Set click state to prevent multiple clicks
                    last_click_time = time.time()  # Update the last click time
            
            elif fingers_open == [0, 1, 1, 1]:
                pyautogui.scroll(-120)  # Scroll down
            
            elif fingers_open == [0, 0, 1, 1]:
                pyautogui.scroll(120)  # Scroll up

            elif fingers_open == [0, 0, 0, 0]:
                if not is_dragging:
                    pyautogui.mouseDown()# All closed: Drag
                    is_dragging = True
                x = int(finger_tips[1].x * screen_width)
                y = int(finger_tips[1].y * screen_height)
                pyautogui.moveTo(x, y)
                has_clicked = False  # Reset click state
            
            else:
                if is_dragging:
                    pyautogui.mouseUp()
                    is_dragging = False
                has_clicked = False
    
    cv2.imshow('Virtual Mouse',img)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()