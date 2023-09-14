FROM python

WORKDIR /dashboard/

COPY requirements.txt .

RUN  pip3 install -r requirements.txt

COPY header_image.png .

COPY .streamlit/config.toml .streamlit/

COPY main.py .

ENTRYPOINT [ "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0" ]