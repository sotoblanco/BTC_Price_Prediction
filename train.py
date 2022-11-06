import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
import xgboost as xgb
import bentoml

df = pd.read_csv("data/BTC_feature_data.csv", index_col="Unnamed: 0", parse_dates=True)

df.dropna(inplace=True)


df_train_full, df_test = train_test_split(df, test_size=0.2, random_state=1)

df_train_full = df_train_full.reset_index(drop=True)

categorical = ["phigh_day_touch", "plow_day_touch","phigh_night_touch", "plow_night_touch"]

numerical = ["ret_distance_phigh_day_open", "ret_distance_plow_day_open", 
            "ret_distance_phigh_night_open", "ret_distance_plow_night_open"]

y_train_full = df_train_full[categorical[0]]

dicts_full_train = df_train_full[numerical].to_dict(orient='records')
dv = DictVectorizer(sparse=False)
X_full_train = dv.fit_transform(dicts_full_train)

dfulltrain = xgb.DMatrix(X_full_train, label=y_train_full)

xgb_params = {
    'eta':0.3,
    'max_depth': 1,
    'min_child_weight':7,

    'objective':'binary:logistic',
    'eval_metric':'auc',

    'nthread':8,
    'seed':1,
    'verbosity':1

}

model = xgb.train(xgb_params, dfulltrain, num_boost_round=30)

bentoml.xgboost.save_model("previous_high_model", model,
                            custom_objects={
                                "dictVectorizer":dv
                            },
                            signatures={
                                "predict": {
                                    "batchable":True,
                                    "batch_dim":0,
                                }
                            })

import json
request = df_test[numerical].iloc[0].to_dict()
print(json.dumps(request, indent=2))

