import pandera as pa
from pandera import Column, Check, DataFrameSchema
RawTelemetrySchema = DataFrameSchema(
    {
        "device_id": Column(str, Check.str_matches(r"^DEV_\d{4}$"), nullable=False, required=False),
        "timestamp": Column(pa.DateTime, nullable=False),
        "temperature": Column(float, Check.in_range(-50.0, 250.0), nullable=True),
        "pressure": Column(float, Check.in_range(0.0, 100.0), nullable=True),
        "vibration": Column(float, Check.greater_than_or_equal_to(0.0), nullable=True),
        "humidity": Column(float, Check.in_range(0.0, 100.0), nullable=True, required=False),
        "current": Column(float, Check.greater_than_or_equal_to(0.0), nullable=True, required=False),
        "target": Column(int, Check.isin([0, 1, 2]), nullable=False, required=False),
    },
    strict=False,
    coerce=True,
)
