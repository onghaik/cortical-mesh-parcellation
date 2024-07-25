def create_pitch_rotation_matrix(pitch_angle):
    """
    Create a rotation matrix for pitch rotation.

    Parameters:
    - pitch_angle: Angle in radians for pitch rotation.

    Returns:
    - R_pitch: Rotation matrix for pitch.
    """
    R_pitch = np.array([[1, 0, 0, 0],
                        [0, np.cos(pitch_angle), -np.sin(pitch_angle), 0],
                        [0, np.sin(pitch_angle), np.cos(pitch_angle), 0],
                        [0, 0, 0, 1]])
    return R_pitch

def create_yaw_rotation_matrix(yaw_angle):
    """
    Create a rotation matrix for yaw rotation.

    Parameters:
    - yaw_angle: Angle in radians for yaw rotation.

    Returns:
    - R_yaw: Rotation matrix for yaw.
    """
    R_yaw = np.array([[np.cos(yaw_angle), 0, np.sin(yaw_angle), 0],
                      [0, 1, 0, 0],
                      [-np.sin(yaw_angle), 0, np.cos(yaw_angle), 0],
                      [0, 0, 0, 1]])
    return R_yaw

def create_roll_rotation_matrix(roll_angle):
    """
    Create a rotation matrix for roll rotation.

    Parameters:
    - roll_angle: Angle in radians for roll rotation.

    Returns:
    - R_roll: Rotation matrix for roll.
    """
    R_roll = np.array([[np.cos(roll_angle), -np.sin(roll_angle), 0, 0],
                       [np.sin(roll_angle), np.cos(roll_angle), 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])
    return R_roll