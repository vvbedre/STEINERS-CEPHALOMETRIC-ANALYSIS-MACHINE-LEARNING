import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class CephalometricML:
    def __init__(self):
        self.model_path = 'cephalometric_model.joblib'
        self.scaler_path = 'cephalometric_scaler.joblib'
        
        # Initialize or load the model and scaler
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            self.model = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=1000
            )
            self.scaler = StandardScaler()
            
        self.training_data = []
        self.training_labels = []
        
    def prepare_input_features(self, landmarks):
        """Convert landmarks dictionary to feature vector"""
        features = []
        for name, pos in landmarks.items():
            if pos['x'] is not None and pos['y'] is not None:
                features.extend([pos['x'], pos['y']])
            else:
                features.extend([0, 0])  # Use 0 for missing landmarks
        return np.array(features).reshape(1, -1)
    
    def predict_measurements(self, landmarks):
        """Predict cephalometric measurements using the trained model"""
        if len(self.training_data) < 5:  # Not enough training data
            return None
            
        features = self.prepare_input_features(landmarks)
        scaled_features = self.scaler.transform(features)
        predictions = self.model.predict(scaled_features)
        
        return {
            'SNA': predictions[0][0],
            'SNB': predictions[0][1],
            'ANB': predictions[0][2],
            'UI_NA': predictions[0][3],
            'LI_NB': predictions[0][4],
            'UI_LI': predictions[0][5]
        }
    
    def add_training_example(self, landmarks, correct_measurements):
        """Add a new training example with corrected measurements"""
        features = self.prepare_input_features(landmarks)
        labels = np.array([
            correct_measurements['SNA'],
            correct_measurements['SNB'],
            correct_measurements['ANB'],
            correct_measurements['UI_NA'],
            correct_measurements['LI_NB'],
            correct_measurements['UI_LI']
        ]).reshape(1, -1)
        
        self.training_data.append(features[0])
        self.training_labels.append(labels[0])
    
    def retrain_model(self):
        """Retrain the model with accumulated training data"""
        if len(self.training_data) < 5:
            return False, "Need at least 5 training examples"
            
        X = np.array(self.training_data)
        y = np.array(self.training_labels)
        
        # Fit scaler and transform training data
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Retrain model
        self.model.fit(X_scaled, y)
        
        # Save model and scaler
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        return True, f"Model retrained with {len(self.training_data)} examples" 