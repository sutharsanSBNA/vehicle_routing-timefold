# Use official Python image
# docker build -t vrp/trip-vehicle-optimizer:latest .
# docker tag vrp/trip-vehicle-optimizer:latest vrp/trip-vehicle-optimizer:v1
# docker push vrp/trip-vehicle-optimizer:v1
FROM python:3.10

# Set the working directory inside the container
WORKDIR /src/vehicle_routing/

# Copy all files frsom the host machine to the container
COPY . .

# Set PYTHONPATH so Python recognizes the 'app' module
ENV PYTHONPATH=/src/vehicle_routing/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
