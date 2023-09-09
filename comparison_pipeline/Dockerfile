FROM python

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY extract.py .
COPY load.py .
COPY compare.py .
COPY main.py .

CMD ["python3", "main.py"]