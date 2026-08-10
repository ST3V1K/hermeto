FROM registry.access.redhat.com/ubi9/python-39@sha256:27733ce9532708c896ff25b7ff1b1c1ac6745954b9b97734f1a48220f07bc2a4

# Test disabled network access
RUN if curl -IsS www.google.com; then echo "Has network access!"; exit 1; fi

WORKDIR /opt/test_package_cachi2
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "/opt/test_package_cachi2/src/test_package_cachi2/main.py"]
