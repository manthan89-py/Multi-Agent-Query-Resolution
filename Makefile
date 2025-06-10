# Makefile

# --- Configurable variables ---
IMAGE_NAME=cloudwalk:multi-agent-chatbot
PORT=8000
ENV_FILE=.env
VENV_DIR=.venv

# ================================
# === Docker Commands ============
# ================================

build:
	sudo docker build -t $(IMAGE_NAME) .

run:
	sudo docker run --env-file $(ENV_FILE) -p $(PORT):$(PORT) $(IMAGE_NAME)

rebuild: clean build run

clean:
	- sudo docker rm -f $(IMAGE_NAME)-container
	# Optional: remove image
	# - sudo docker rmi $(IMAGE_NAME)

# ================================
# === Helper =====================
# ================================

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Docker targets:"
	@echo "  build         Build Docker image"
	@echo "  run           Run Docker container with env"
	@echo "  rebuild       Clean and rebuild Docker image"
	@echo "  clean         Stop and remove Docker container"