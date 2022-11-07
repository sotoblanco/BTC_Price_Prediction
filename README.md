# BTC Price prediction

## Problem description

Bitcoin is a cryptocurrency that trades on the financial market, investor use metrics and indicators based on historical data to predict the future movement of the price, predicting price is usually not enough for investor to develop a successful trading strategy, a lot of things needs to be considered, such as time and also constraints about risk willing to take and how long they keep with the assets.

Usually strategies follows trading guidelines and operators such as stop loss as measure of risk, take profit as measure of getting out of the market and entry as signal of exposure to the market, however, statistical decision based on probabilities is something we haven't seen yet with the amount of frequency we would like.

In this repository we evaluate the market based on certain indicators that allow to allocate probabilities on price zones, a key aspect about this repository is that it is not intended to be a strategy since it won't have the components needed to entry and exit a position, or even risk management, it would only show probabilities of certain regions of the market which can be used to reduce uncertainty in an already develop strategy.

For meet with this goal every day after 9am EST we get a new set of predicted features that feeds the ML service and returns a probability of reaching a zone of the market, the data gets hourly updates so every time you run the predicted notebook you will see how the price change but the probability and the line remain in the same place until the next day. 

## Data

The data was obtained from this repository that obtains data from binance API and using GitHub actions runs hourly and store the data into a csv file https://github.com/sotoblanco/Binance_data_live

Important details about the data:
- The timezone is UTC
- The data updates hourly
- The format of the data is: 
	- index 
	- datetime
	- open
	- high
	- low
	- close
	- volume
	- adj_close
 
 The last data store in the data folder to train our model was obtained November 3 2022 at 19:00 UTC
 
This data is processed using the ``feature_engineering_btc.py`` file store in the data folder.

We split the market hours into day and night:

Day means the price between 9:00 to 16:59 EST
Night means the price between 17:00 to 8:59 EST

For each split (Day and night) we obtain the **high**, **low**, **open** (first) and **close** (last) price of the session

Finally, we obtain the ``BTC_feature_data.csv`` which has the following features.

- index: datetime index format YYYY-mm-dd

Dependent features
- **phigh_day_touch**: If we touch previous high of the day 
- **plow_day_touch**: If we touch previous low of the day 
- **phigh_night_touch**: If we touch previous high of the night
- **plow_night_touch**: If we touch previous low of the night

Independent features
- **ret_distance_phigh_day_open**: distance between the high of the previous day and the open divided by the open
- **ret_distance_plow_day_open**: distance between the low of the previous day and the open divided by the open
- **ret_distance_phigh_night_open**: distance between the high of the previous night and the open divided by the open
- **ret_distance_phigh_night_open**: distance between the high of the previous night and the open divided by the open

## Model details

For this model we only use one dependent feature which is ``phigh_day_touch`` the rest of the dependent features are removed from the data.

The independent features represent the distance between features of the previous day and night and the initial price at 9:00 am EST

## Structure of the repository

### data folder

**BTCUSDT_historical_1h.csv** : Raw data obtained from binance
**feature_engineering_btc.py**: Script that creates the features of the data that we use for our model
**BTC_feature_data.csv**: Data with the features use for our model

### main folder

**bentofile.yaml**: Contains the bentoML file to run our service

**locustfile.py**: To test our prediction service

**notebook.ipynb**: contains the notebook to explore the data and choose the model with the best results

**Pipfile and Pipfile.lock**: contains the dependencies to run the repo

**predict.py**: Contains the prediction using bentoML (is already set to run the latest model exported by ``train.py``

**prediction_notebook.ipynb** Allows to interact with the prediction model in an interactive environment.

**train.py**: Contains the model with the best performance in the testing set and exported to bentoML


## How to run

Clone the repo: 

Install the dependencies
```
pipenv install
pipenv shell
```

### Building the prediction model and service

Run the ``train.py`` file to obtain and export the model to bentoml

```
python train.py
```

Run the ``predict.py`` using: 
```
bentoml serve predict.py:svc
```
This creates a local prediction service to see the performance of our model. 

Test the prediction of the model by using the **prediction_notebook.ipynb** this notebook use the latest data from this [repository](https://github.com/sotoblanco/Binance_data_live) and make a prediction about the BTC price using this chart:

![image](https://user-images.githubusercontent.com/46135649/199868693-967a9944-6d28-4698-acbf-d6cb7863e062.png)
 
 The box in the right upper corner is the predicted probability of that day of BTC reaching to that price. 

This can be run locally by changing  url in the prediction_notebook to ``http://localhost:3000/classify``

### Optional: locustfile test

**Optional**: locustfile.py can also be run to test the prediction service just run the ``predict.py`` using:

``
bentoml serve --production
``

This will run your service in the localhost:3000

open a new command line (make sure locust is installed) run:

``
locust -H http://localhost:3000
`` 

Open: ``localhost:8089`` in your browser and use the interface to add users and spawn rate:

![image](https://user-images.githubusercontent.com/46135649/199871260-3d6116c4-000b-472a-9752-c9e53d9f6665.png)

This is a picture of the overall performance of the prediction service

### Deployment and Docker image

The first step to deploy our model is building our bento:

``bentoml build``

After that we create the **docker** images using bento with:

``bentoml containerize previous_high_classifier:o3w23es35cp4kaav`` 

The tag ``o3w23es35cp4kaav`` is obtained from building your bento, you will get a different tag, make sure to copy the one from your model and not this one. 


### Cloud deployment

AWS

**pre-requisets** needs to have AWS CLI installed which is command line to interact with AWS ( I have a windows and working with WSL, so I download the cli using the linux command)

### Elastic Container Registry:
Place to store your container

Create repo
View push command

Go to security credentials and find the access key to configure your AWS

run in your command line:
``aws configure`` and type your credentials from the above step

run: 
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 924626007762.dkr.ecr.us-east-1.amazonaws.com
```
tag your docker
```
docker tag previous_high_classifier:o3w23es35cp4kaav 924626007762.dkr.ecr.us-east-1.amazonaws.com/predict-high-classifier-repo:latest
```

push the image
```
docker push 924626007762.dkr.ecr.us-east-1.amazonaws.com/predict-high-classifier-repo:latest
```

### Elastic container service
place to run your docker images

Create an Elastic container service cluster using fargate cluster (do not run in a gpu)

Create a task for your cluster on **task definition**
- Linux
- Task memory 0.5GB
- Task CPU 0.25vCPU
- Add container
- Get the URI of your image store in the Elastic container registry and set in the images box
- Soft limit to 256
- Port mapping 3000

After that run the task:
- Go to the cluster
- Taks
- Run new task
	- Select fargate
	- Linux
	- Default VPC
	- Subnet 1a

Security group -> Edit
- Add rule:
- custom TCP 
- port range 3000

This [video](https://www.youtube.com/watch?v=aF-TfJXQX-w&list=PL3MmuxUbc_hIhxl5Ji8t4O6lPAOpHaCLR&index=72) contains all the steps to get your production service into AWS.

The link to the prediction service is: http://3.232.96.214:3000/
