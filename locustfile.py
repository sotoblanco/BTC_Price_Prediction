# this file is for test users and the behavior of the end point
from locust import task
from locust import between
from locust import HttpUser


# sample of the data that your are going to send
sample =  {
 "ret_distance_phigh_day_open": -0.0445565874068783,
  "ret_distance_plow_day_open": 0.0039019944241903,
  "ret_distance_phigh_night_open": -0.0237290079718873,
  "ret_distance_plow_night_open": 0.0145632856523623
}

# inheritance from httpuser which is a locus object
class MLZoomUser(HttpUser):
    """
    Usage:
        Start locust load testing client with:
            locust -H http://localhost:3000
        Open browser at http://0.0.0.0:8089, adjust desired number of users and spawn
        rate for the load test from the Web UI and start swarming.
    """

    @task
    def classify(self):
        self.client.post("/classify", json=sample)

    wait_time = between(0.01, 2)