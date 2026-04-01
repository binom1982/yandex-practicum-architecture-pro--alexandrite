from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

# Настройка OpenTelemetry
trace.set_tracer_provider(TracerProvider())
exporter = OTLPSpanExporter()
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))
FlaskInstrumentor().instrument_app(app)

tracer = trace.get_tracer(__name__)

@app.route('/calculate')
def calculate():
    with tracer.start_as_current_span("calculate_logic"):
        return "Price calculated: 1000 RUB"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)