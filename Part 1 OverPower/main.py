import cv2
import numpy as np
import helper_methods



# Video camera properties
pathInputVideo = "Part 1/media/video1.mp4"
cap = cv2.VideoCapture(pathInputVideo)

header_gray = cv2.imread("Part 1/media/header.png", 0)


# global flags
biggest_found = False
paper_contour_found = False
SAVE_VIDEO = False
DISPLAY_VIDEO = True

def get_biggest():
    while True:

        if cap.isOpened():

            ret, img = cap.read()

            if not ret:
                break

            height = int(img.shape[0] / 2)
            width = int(img.shape[1] / 2)

            if width > height:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                height = int(img.shape[0] / 2)
                width = int(img.shape[1] / 2)

            img = cv2.resize(img, (width, height))

            # Main project pipeline
            img_blank = np.zeros((height, width, 3), np.uint8) #Blank image


            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
            img_threshold = cv2.Canny(img_blur, 100, 200)
            # Let's remove some noise and make the contours thicker. This is not necessary but generates better results
            img_dilated = cv2.dilate(img_threshold, np.ones((5,5)), iterations=2)
            img_threshold = cv2.erode(img_dilated, np.ones((5,5)), iterations=1)

            # Find contours
            img_contours = img.copy() #For displaying
            img_big_contour = img.copy() #For displaying

            contours, hierarchy = cv2.findContours(img_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 10)

            # Find the biggest contour and transform the perpective
            if paper_contour_found is False:
                biggest, max_area = helper_methods.get_biggest_contour(contours)
                biggest_found = biggest.size != 0

            if biggest_found:

                biggest = helper_methods.reorder(biggest)
                cv2.drawContours(img_big_contour, biggest, -1, (0, 255, 0), 20) # Draw contour 'biggest' in the 'img_big_contour'
                original_points = np.float32(biggest)
                destination_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]]) # We want our final points to be the edges of the image, so the image keeps it size
                transformation_matrix = cv2.getPerspectiveTransform(original_points, destination_points) # Get the transformation matrix from the image points to the destination points
                img_warp_colored = cv2.warpPerspective(img, transformation_matrix, (width, height))

                # Remove 20 pixels from each side so even if the contour is drawn with some errors on the side we remove them
                img_warp_colored = img_warp_colored[20:img_warp_colored.shape[0] - 20, 20:img_warp_colored.shape[1] - 20]
                img_warp_colored = cv2.resize(img_warp_colored, (width, height))

                # Convert our image to grayscale
                img_warp_gray = cv2.cvtColor(img_warp_colored, cv2.COLOR_BGR2GRAY)

                res = cv2.matchTemplate(img_warp_gray, header_gray, cv2.TM_CCOEFF_NORMED)

                threshold = 0.5
                if np.amax(res) > threshold:
                    #paper_contour_found = True
                    return biggest

            else:
                continue
        else:
            continue

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def video_fun(biggest):

    while True:

        if cap.isOpened():

            ret, img = cap.read()

            if not ret:
                break

            height = int(img.shape[0] / 2)
            width = int(img.shape[1] / 2)

            if width > height:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                height = int(img.shape[0] / 2)
                width = int(img.shape[1] / 2)

            img = cv2.resize(img, (width, height))

            #cv2.drawContours(img_big_contour, biggest, -1, (0, 255, 0), 20) # Draw contour 'biggest' in the 'img_big_contour'
            original_points = np.float32(biggest)
            destination_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]]) # We want our final points to be the edges of the image, so the image keeps it size
            transformation_matrix = cv2.getPerspectiveTransform(original_points, destination_points) # Get the transformation matrix from the image points to the destination points
            img_warp_colored = cv2.warpPerspective(img, transformation_matrix, (width, height))

            # Remove 20 pixels from each side so even if the contour is drawn with some errors on the side we remove them
            img_warp_colored = img_warp_colored[20:img_warp_colored.shape[0] - 20, 20:img_warp_colored.shape[1] - 20]
            img_warp_colored = cv2.resize(img_warp_colored, (width, height))

            # Convert our image to grayscale
            img_warp_gray = cv2.cvtColor(img_warp_colored, cv2.COLOR_BGR2GRAY)

            # Give it a more scanned look
            img_adaptive_threshold = cv2.adaptiveThreshold(img_warp_gray, 255, 1, 1, 7, 2) # Get binary image
            img_adaptive_threshold = cv2.bitwise_not(img_adaptive_threshold) # Reverse it, all 0 -> 1 and all 1 -> 0
            img_adaptive_threshold = cv2.medianBlur(img_adaptive_threshold,3) # Reduce some noise

            # image_array = ([img, img_gray, img_threshold, img_contours],
            #         [img_big_contour, img_warp_colored, img_warp_gray, img_adaptive_threshold])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if SAVE_VIDEO:
                # write the flipped frame
                frame_array.append( img_adaptive_threshold )


            if DISPLAY_VIDEO:
                #stacked_images = helper_methods.stackImages(image_array, 0.75, labels)
                cv2.imshow("window", img_warp_colored)


labels = [["Original", "Gray", "Threshold", "Contours"],
            ["Biggest Contour", "Warp Perpective", "Warp Grey", "Adaptive Threshold"]]




biggest = get_biggest()

cap.release()



cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

cap = cv2.VideoCapture(pathInputVideo)

pathOutputVideo = pathInputVideo.replace(".mp4","_output.mp4")



frame_array=[]
try:
    video_fun(biggest)
except:
    pass


cap.release()
cv2.destroyAllWindows()

if SAVE_VIDEO:

    size = (frame_array[0].shape[1],frame_array[0].shape[0])

    layers_3 = frame_array[0].shape[2] == 3

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(pathOutputVideo,fourcc, 20.0,size, layers_3) # TODO


    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])

    out.release()
