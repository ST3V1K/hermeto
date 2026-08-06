FROM registry.access.redhat.com/ubi9/python-39@sha256:cc1e31fb4fd4007220feb8afbbb59ec90e5e95c3af8b02a8fa8694304265fe4d

# Test disabled network access
RUN if curl -IsS www.google.com; then echo "Has network access!"; exit 1; fi

WORKDIR /opt/test_package_cachi2
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "/opt/test_package_cachi2/src/test_package_cachi2/main.py"]
