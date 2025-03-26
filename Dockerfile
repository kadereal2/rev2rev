####### 👇 OPTIMIZED SOLUTION (x86)👇 #######

# tensorflow base-images are optimized: lighter than python-buster + pip install tensorflow
#FROM tensorflow/tensorflow:2.10.0
# OR for apple silicon, use this base image, but it's larger than python-buster + pip install tensorflow
# FROM armswdev/tensorflow-arm-neoverse:r22.09-tf-2.10.0-eigen
FROM python:3.10.6-buster


COPY prod prod
# We strip the requirements from useless packages like `ipykernel`, `matplotlib` etc...
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r prod/requirements.txt

#--port 8000 
# Change the route once we have the folders
CMD uvicorn prod.test:app --host 0.0.0.0 --port $PORT

