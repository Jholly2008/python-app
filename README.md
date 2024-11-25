docker build -t my-ins-app:v1.0 .

docker run -d -p 29001:29001 --name my-ins-app-container my-ins-app:v1.0
