from joblib import dump
import numpy as np
import json
import pandas as pd
import shap
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, make_scorer
from sklearn.ensemble import IsolationForest
# Extended Isolation Forest 
import eif_new

# Loading EV Charging data and performing data filtering and transformation
ev_data = None
ev_data_frame = None

with open("../data/acndata_sessions.json") as json_file:
    ev_data = json.loads(json_file.read())
    ev_data_frame = pd.DataFrame.from_dict(ev_data["_items"], orient="columns")
    print(ev_data_frame.info())

ev_data_frame.dropna(inplace=True)
ev_data_frame.drop(columns=["_id", "clusterID", "userID", "spaceID", "timezone", "siteID"], inplace=True)

ev_data_frame["userInputs"] = ev_data_frame["userInputs"].str[0]
ev_data_frame = pd.concat([ev_data_frame.drop(["userInputs"], axis=1), ev_data_frame["userInputs"].apply(pd.Series)], axis=1)    
ev_data_frame.drop(columns=["WhPerMile", "milesRequested", "minutesAvailable", "modifiedAt", "paymentRequired", "requestedDeparture", "sessionID", "stationID"], inplace=True)
ev_data_frame[["connectionTime", "disconnectTime", "doneChargingTime"]] = ev_data_frame[["connectionTime", "disconnectTime", "doneChargingTime"]].apply(pd.to_datetime)
# ev_data_frame["connectionDuration"] = (ev_data_frame.disconnectTime-ev_data_frame.connectionTime).astype('timedelta64[h]')
ev_data_frame["chargingDuration"] = (ev_data_frame.doneChargingTime-ev_data_frame.connectionTime).astype('timedelta64[h]')
ev_data_frame.drop(columns=["connectionTime", "disconnectTime", "doneChargingTime", "userID"], inplace=True)

print(ev_data_frame.columns)

# Tuning the isolation forest 

tuned = {'n_estimators':[1000,500], 
        'max_samples':['auto'],
        'contamination':[0.01,0.001], 
        'max_features':[3],
        'bootstrap':[True],  
        'random_state':[None,42]
}  

def scorer_f(estimator, X):   #your own scorer
    return np.mean(estimator.score_samples(X))

# Running model tuning and finding the parameters

isolation_forest = GridSearchCV(IsolationForest(), tuned, scoring=scorer_f)
model = isolation_forest.fit(ev_data_frame.to_numpy())

print(model.best_params_)

# Create Isolation forest with the tuned parameters

isolation_forest = IsolationForest(n_estimators=model.best_params_["n_estimators"], max_samples=model.best_params_["max_samples"], contamination=model.best_params_["contamination"], 
max_features=model.best_params_["max_features"], bootstrap=model.best_params_["bootstrap"], n_jobs=-1, random_state=model.best_params_["random_state"], verbose=1)

# Fit the model
isolation_forest.fit(ev_data_frame.to_numpy())

# Test the isolation forest model with anomaly value 

test_data = pd.DataFrame([{"kWhDelivered": 126.608, "kWhRequested":100.0, "chargingDuration":4}])

pred = isolation_forest.predict(test_data.to_numpy())

print("Anomaly") if pred < 0 else print("Normal")

# Creating Extended Isolation Forest model and fitting

extended_isolation_forest = eif_new.iForest(ntrees=model.best_params_["n_estimators"], sample=len(ev_data_frame.to_numpy()), random_state=model.best_params_["random_state"])
extended_isolation_forest = extended_isolation_forest.fit(ev_data_frame.to_numpy())

# Predicting the Extended isolation forest with test value

pred = extended_isolation_forest.predict(test_data.to_numpy())

print("Anomaly") if pred else print("Normal")

# Exploring and analyzing the model explainable features using SHAP

shap.initjs()

shap_values = shap.TreeExplainer(isolation_forest).shap_values(ev_data_frame)

print(shap_values[1])

# visualize the prediction's explanation using the summary plot and dependence plot
shap.summary_plot(shap_values, ev_data_frame)

for name in ev_data_frame.columns:
    shap.dependence_plot(name, shap_values, ev_data_frame, interaction_index="kWhDelivered")

# Saving the models
dump(isolation_forest, './isolation_forest.joblib')
dump(extended_isolation_forest, './extended_isolation_forest.joblib')

# TODO: ML Training Loop