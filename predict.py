import bentoml
from bentoml.io import JSON

model_ref = bentoml.xgboost.get("previous_high_model:latest")
dv = model_ref.custom_objects['dictVectorizer']

model_runner = model_ref.to_runner()

svc = bentoml.Service("previous_high_classifier", runners=[model_runner])


@svc.api(input=JSON(), output=JSON())
async def classify(application_data):
    vector = dv.transform(application_data)
    prediction = await model_runner.predict.async_run(vector)
    print(prediction)

    result = prediction[0]
    
    return result
