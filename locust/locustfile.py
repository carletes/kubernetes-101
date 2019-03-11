from locust import HttpLocust, TaskSet, task


class UserBehaviour(TaskSet):

    @task(1)
    def index(self):
        self.client.get('/')


class WebsiteUser(HttpLocust):

    task_set = UserBehaviour
