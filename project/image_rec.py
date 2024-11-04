import cv2

def recognize_qr_code(image_path):
    """
    Tries to recognize a QR code in the given image using OpenCV.
    Returns True if a QR code is detected, False otherwise.
    """
    try:
        image = cv2.imread(image_path)
        detector = cv2.QRCodeDetector()
        decoded_text, points, _ = detector.detectAndDecode(image)
        isQR = True
        if not decoded_text:
            isQR = False

        return isQR, decoded_text
    except Exception as e:
        print(f"Error detecting QR code: {e}")
        return False
