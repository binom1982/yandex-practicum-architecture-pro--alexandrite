from flask import Flask
import requests
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

# Настройка OpenTelemetry
trace.set_tracer_provider(TracerProvider())
exporter = OTLPSpanExporter()
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument() # Важно для пропагации контекста в HTTP вызовы

tracer = trace.get_tracer(__name__)

# Адрес сервиса B внутри Kubernetes
SERVICE_B_URL = "http://service-b:8080/calculate"

@app.route('/order')
def order():
    with tracer.start_as_current_span("order_logic"):
        # Вызов второго сервиса
        response = requests.get(SERVICE_B_URL)
        return f"Order created. {response.text}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)