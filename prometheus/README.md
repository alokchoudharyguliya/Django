# Prometheus Django Project

## Setup
`django-admin startproject prometheus`
`pip install django-prometheus`

Add to `INSTALLED_APPS`


`INSTALLED_APPS = [
=>   "django_prometheus",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]`

Add Prometheus middleware at the top and bottom of `MIDDLEWARE`

`MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]`

Add the Prometheus metrics endpoint in your `urls.py`

`urlpatterns = [
    path('admin/', admin.site.urls),
=>    path('', include('django_prometheus.urls')),
]`

Open: http://127.0.0.1:8000/metrics

Create a `docker-compose.yml` file in the project root directory (same location as manage.py)

version: '3.7'

```docker
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

Create a Prometheus config file `prometheus.yml` in the same directory
```prometheus
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "django"
    static_configs:
      - targets: ["host.docker.internal:8000"]
```

Update the allowed hosts in `settings.py` to allow requests from the Prometheus container

`ALLOWED_HOSTS = ["*"]`

Start Prometheus & Grafana

`docker-compose up`
## Adding metrics for a new project