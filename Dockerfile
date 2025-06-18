FROM python:latest  

WORKDIR /app

COPY . .

COPY .env .env

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
#ngrok http 192.168.49.2:30099
#http://localhost:9090

#http://localhost:3000

#https://github.com/shazforiot/Prometheusalertmanager/blob/main/slack_alertmanager.yml

#https://dev.to/yash_sonawane25/how-to-set-up-github-actions-for-any-project-step-by-step-8ga