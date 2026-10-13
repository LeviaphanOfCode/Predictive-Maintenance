class Settings:
    MODEL_VERSION: str = "1.3.0"
    FALLBACK_THRESHOLD: float = 0.75
    
    # Параметры скейлера из train_x
    SCALER_MINS = [0.0, 0.0, 0.0, 0.0]       # temp, press, vib, hum
    SCALER_MAXS = [200.0, 100.0, 50.0, 100.0] # диапазоны датчиков

    CLASSES = ["safe", "warning", "critical"]

settings = Settings()
