export VERSION := "1.71.5-gtxn"

docker-build:
  DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -t matrixdotorg/synapse:local -f docker/Dockerfile .
  
docker-publish:
  @echo "Tagging local with version: ${VERSION}"
  docker tag matrixdotorg/synapse:local europe-west3-docker.pkg.dev/buoy-money/gtxn-docker-repo/synapse:v${VERSION}
  docker push europe-west3-docker.pkg.dev/buoy-money/gtxn-docker-repo/synapse:v${VERSION}
