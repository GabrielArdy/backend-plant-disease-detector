from app.models.inference_model import InferenceModel

# Load the model
model = InferenceModel()

def predict_disease(data):
    # Implement prediction logic using the model
    return model.predict(data)
