APP_NAME = lgu_plus_sync
MODEL_VOLUME = /home/sch9027/workspace/lgu_plus_sync:/app
#MODEL_VOLUME = /home/pjs102793/workspace/lgu_project:/workspace/junseo

# Build and run the container
build:
	@echo 'build docker $(APP_NAME)'
	docker build --no-cache -t $(APP_NAME) . 

run:
	@echo 'run docker $(APP_NAME)'
	docker run -d -t --name="$(APP_NAME)" --net=host --ipc=host --shm-size 32gb -v $(MODEL_VOLUME) --cpuset-cpus="32-47" --gpus all $(APP_NAME)

stop:
	@echo 'stop docker $(APP_NAME)'
	docker stop $(APP_NAME)

rm:
	@echo 'rm docker $(APP_NAME)'
	docker rm -f $(APP_NAME)

rmi:
	@echo 'rmi docker $(APP_NAME)'
	docker rmi $(APP_NAME)
