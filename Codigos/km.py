def validate_data(X, threshold=None):
    """
    Validates the dataset to check for any NaN, infinite, or extreme values.
    
    Parameters:
    X : numpy.ndarray
        The dataset to validate.
    threshold : float, optional
        Threshold for extreme values. If None, no extreme value check is performed.
    
    Returns:
    bool
        True if the dataset is valid, False otherwise.
    """
    # Check for NaN
    if np.isnan(X).any():
        print("Validation Failed: Dataset contains NaN values.")
        return False

    # Check for infinite values
    if np.isinf(X).any():
        print("Validation Failed: Dataset contains infinite values.")
        return False

    # Check for extreme values if threshold is provided
    if threshold is not None:
        if (X > threshold).any() or (X < -threshold).any():
            print(f"Validation Failed: Dataset contains values beyond the threshold ±{threshold}.")
            return False

    print("Validation Passed: No NaN, infinite, or extreme values detected.")
    return True

# Main execution
current_path = os.getcwd()
file_path = 'Codigos/test_kalman.csv'
rel_path = os.path.join(current_path, file_path)

# Load dataset
X = np.genfromtxt(rel_path, delimiter=',', skip_header=1)

# Validate data
threshold_value = 1000  # Example threshold; adjust based on your dataset
is_valid = validate_data(X, threshold=threshold_value)

if not is_valid:
    print("Data validation failed. Please check your preprocessing.")
else:
    print("Data is ready for Kalman filtering.")

H_all, H_significant, H_non_significant = observation_matrices(14, 3, 11)
results_all = kalmanEnsemble(X, H_all)

# Plot the results
sensors = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
plot_signal(results_all, X, sensors, sensors)
