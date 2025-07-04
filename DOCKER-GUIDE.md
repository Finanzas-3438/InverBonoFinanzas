# 1. Construye la imagen con el nuevo código
docker-compose build

# 2. Etiqueta la nueva versión
docker tag inverbonofinanzas-web augustopin/inverbono:latest

# 3. Sube la nueva versión a Docker Hub
docker push augustopin/inverbono:latest