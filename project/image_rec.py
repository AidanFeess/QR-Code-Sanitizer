import cv2

def recognize_qr_code(image_path):
    """
    Tries to recognize a QR code in the given image using OpenCV.
    Returns True if a QR code is detected, False otherwise.
    """
    try:
        # Load the image
        image = cv2.imread(image_path)

        # Initialize the QRCode detector
        detector = cv2.QRCodeDetector()

        # Detect and decode the QR code
        decoded_text, points, _ = detector.detectAndDecode(image)

        # If there's a QR code and it is decoded successfully, return True
        return bool(decoded_text)  # Returns True if text is detected, False otherwise
    except Exception as e:
        print(f"Error detecting QR code: {e}")
        return False
