import json
import joblib
import mlflow
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from app.core.contracts import RawTelemetrySchema
RAW_PATH = Path("data/raw/telemetry.csv")
OUT_PATH = Path("data/processed")
ART_PATH = Path("artifacts")
OUT_PATH.mkdir(parents=True, exist_ok=True)
ART_PATH.mkdir(parents=True, exist_ok=True)
def main() -> None:
    raw_df = pd.read_csv(RAW_PATH, parse_dates=["timestamp"])
    validated_df = RawTelemetrySchema.validate(raw_df)

    clean_df = validated_df.drop_duplicates().copy()
    clean_df = clean_df.sort_values("timestamp").reset_index(drop=True)

    if "target" not in clean_df.columns:
        clean_df["target"] = 0

    clean_df["window_id"] = clean_df.index // 60

    available_features = [c for c in ["temperature", "pressure", "vibration", "humidity", "current"] if c in clean_df.columns]

    agg_dict = {col: "mean" for col in available_features}
    agg_dict["target"] = lambda x: x.mode()[0] if not x.mode().empty else 0

    windowed_df = clean_df.groupby("window_id").agg(agg_dict).reset_index()

    split_at = int(len(windowed_df) * 0.8)
    train_df = windowed_df.iloc[:split_at].copy()
    test_df = windowed_df.iloc[split_at:].copy()

    num_features = available_features[:2] 
    if len(num_features) < 2:
        raise ValueError("В датасете слишком мало числовых признаков для работы ColumnTransformer")

    cat_feature = available_features[2] if len(available_features) > 2 else available_features[0]
    for df in [train_df, test_df]:
        df["cat_feature"] = pd.qcut(df[cat_feature], q=3, labels=["LOW", "MED", "HIGH"], duplicates="drop")

    cat_features = ["cat_feature"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
        ]
    )

    x_train = preprocessor.fit_transform(train_df[num_features + cat_features])
    x_test = preprocessor.transform(test_df[num_features + cat_features])
    feature_names = preprocessor.get_feature_names_out()

    train_out = pd.DataFrame(x_train, columns=feature_names)
    test_out = pd.DataFrame(x_test, columns=feature_names)
    train_out["target"] = train_df["target"].to_numpy()
    test_out["target"] = test_df["target"].to_numpy()

    train_out.to_parquet(OUT_PATH / "train.parquet", index=False)
    test_out.to_parquet(OUT_PATH / "test.parquet", index=False)
    joblib.dump(preprocessor, ART_PATH / "preprocessor.joblib")

    report = {
        "raw_rows": int(len(raw_df)),
        "windowed_rows": int(len(windowed_df)),
        "train_rows": int(len(train_out)),
        "test_rows": int(len(test_out)),
    }
    (OUT_PATH / "validation_report.json").write_text(json.dumps(report, indent=2, default=int))

    mlflow.set_experiment("lab4-data-pipeline")
    with mlflow.start_run() as run:
        mlflow.log_params({"split_strategy": "time_ordered", "window_size": 60})
        mlflow.log_metrics(report)
        mlflow.log_artifact(str(OUT_PATH / "validation_report.json"))
        mlflow.log_artifact(str(ART_PATH / "preprocessor.joblib"))
        print(f"MLflow run_id: {run.info.run_id}")

if __name__ == "__main__":
    main()
