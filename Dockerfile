# Use the image python;
FROM python
WORKDIR /chatbot
# Copy the python scripts and other files to the container;
COPY . /chatbot
# Install the dependencies using the two pip install commands;
RUN pip install update
RUN pip install -r requirements.txt
# Set the environment variables.
ENV CHATGPT_ACCESS_TOKEN=96c7dfd2-5e63-4962-b0f5-014b32d842f9 
ENV CHATGPT_APIVERSION=2023-12-01-preview 
ENV CHATGPT_BASICURL=https://chatgpt.hkbu.edu.hk/general/rest 
ENV CHATGPT_MODELNAME=gpt-4-turbo 
ENV REDIS_HOST=redis-13632.c323.us-east-1-2.ec2.cloud.redislabs.com 
ENV REDIS_PASSWORD=zu3haYJIeB6TyqNVkvDAbVyARZp4eFKv 
ENV REDIS_PORT=13632 
ENV TELEGRAM_ACCESS_TOKEN=6643221960:AAEaYncLwQUw-rmu8_xeFigwDu1Tob8twdg,
ENV MYSQL_PASSWORD=4NXNxaN6z7Mnstpw
# Set the ENTRYPOINT and/or CMD
CMD python chatbot.py