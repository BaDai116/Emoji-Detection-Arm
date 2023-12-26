import numpy as np
from scipy.optimize import minimize

# List of camera 2D coordinates (x, y)
camera_coordinates = [
    (32,354),(34,286),(38,218),(38,159),(55,334),(58,300),(60,270),(56,222),(60,172),(99,156),(100,186),(98,234),(102,280),(104,310),(101,335),(108,359),(142,317),(152,264),(152,220),(156,156),(204,154),(210,194),(208,252),(224,302),(233,356),(264,346),(286,290),(284,242),(290,190),(296,152),(336,152),(342,188),(347,256),(352,318),(366,356),(410,344),(420,295),(427,233),(430,188),(444,154),(478,154),(480,212),(484,255),(484,305),(514,301),(515,251),(528,156)
    # Add more coordinates here
]

# List of corresponding robot arm coordinates (x, y)
robot_coordinates = [
    (156.41,-146.96),(154.33,-187.03),(151.57,-225.71),(151.2,-259.191),(141.18,-158.20),(140.98,-179.51),(138.66,-196.13),(140.82,-223),(138.9,-252.4),(115.05,-261.54),(114.82,-244.89),(116.1,-217.81),(113.78,-189.89),(112.58,-172.60),(114.88,-158.58),(110.66,-144.86),(90.34,-169.48),(84.34,-198.68),(84.93,-223.20),(80.56,-259.73),(52.74,-259.52),(50.67,-237.46),(52.21,-204.94),(43.18,-176.99),(39.14,-146.25),(20.65,-151.62),(8.92,-183.76),(9.91,-210.32),(5.43,-240),(2.53,-260.40),(-20.37,-260.46),(-22.48,-240.17),(-26.01,-200),(-28.22,-167.19),(-36.25,-146.22),(-60.48,-150.92),(-66.59,-178.98),(-70.51,-213.32),(-72.29,-239.50),(-81.29,-257.44),(-99.86,-257.42),(-100.13,-224.8),(-102.50,-201.62),(-102.12,-173.24),(-119.98,-173.94),(-120.97,-202.42),(-128.114,-256)
    # Add more coordinates here
]

# Define the transformation matrix parameters (scale_x, scale_y, rotate, translate_x, translate_y)
initial_guess = [1.0, 1.0, 0.0, 0.0, 0.0]


# Function to compute the error between transformed camera coordinates and robot coordinates
def error_function(params):
    # Extract the transformation matrix parameters
    scale_x, scale_y, rotate, translate_x, translate_y = params

    # Construct the 2D transformation matrix
    transformation_matrix = np.array([
        [scale_x * np.cos(rotate), -scale_y * np.sin(rotate), translate_x],
        [scale_x * np.sin(rotate), scale_y * np.cos(rotate), translate_y]
    ])

    # Apply the transformation matrix to all camera coordinates
    transformed_camera_coordinates = np.dot(
        np.hstack((np.array(camera_coordinates), np.ones((len(camera_coordinates), 1)))), transformation_matrix.T)

    # Calculate the error as the sum of squared differences between robot and transformed camera coordinates
    error = np.sum((np.array(robot_coordinates) - transformed_camera_coordinates[:, :2]) ** 2)

    return error


# Use scipy's minimize function to find the optimal transformation matrix
result = minimize(error_function, initial_guess, method='BFGS')

# Extract the optimal transformation matrix parameters
optimal_params = result.x
scale_x, scale_y, rotate, translate_x, translate_y = optimal_params

# Construct the optimal transformation matrix
optimal_transformation_matrix = np.array([[scale_x * np.cos(rotate), -scale_y * np.sin(rotate), translate_x],
    [scale_x * np.sin(rotate), scale_y * np.cos(rotate), translate_y]
])

# Print the optimal transformation matrix
print("Optimal Transformation Matrix:")
print(optimal_transformation_matrix)