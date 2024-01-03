import cv2

def show_number_at_position(image, name, cx, cy):
    """
    Show a number at a given position on the image.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    font_color = (0, 0, 255)  # White color for the text

    cv2.putText(image, name, (cx, cy), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

    return image


def show_all_name_at_position(frame, light_point_array):
        for i, (name, _, x, y) in enumerate(light_point_array):
            frame = show_number_at_position(frame, name, x, y)
            print(f"Point {i+1}: {name} at ({x}, {y})")