import json

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

from backend.core.config import ARTIFACTS_DIR, DB_PATH, MODEL_PATH, risk_label
from backend.services.feature_engine import FEATURE_COLUMNS, TARGET_COLUMN


def load_feature_matrix() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("SELECT * FROM mart_credit_features").fetchdf()
    con.close()
    return df


def _build_candidates(y: pd.Series) -> dict:
    return {
        "logistic_regression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=42
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, class_weight="balanced", random_state=42
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100, random_state=42, max_depth=4
        ),
    }


def _needs_scaling(model_name: str) -> bool:
    return model_name == "logistic_regression"


def _cross_validate(models: dict, X: np.ndarray, X_scaled: np.ndarray, y: pd.Series) -> dict:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    for name, model in models.items():
        data = X_scaled if _needs_scaling(name) else X
        scores = cross_val_score(model, data, y, cv=cv, scoring="roc_auc")
        results[name] = {
            "mean_auc": float(scores.mean()),
            "std_auc": float(scores.std()),
            "cv_scores": scores.tolist(),
        }
        print(f"{name}: AUC = {scores.mean():.3f} (+/- {scores.std():.3f})")
    return results


def _extract_feature_importance(model, feature_cols: list[str]) -> list[tuple]:
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        importances = np.zeros(len(feature_cols))

    return sorted(
        zip(feature_cols, importances.tolist()),
        key=lambda x: x[1],
        reverse=True,
    )


def _save_artifacts(model, scaler, model_name, results, feature_importance, y, y_proba):
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": model,
        "scaler": scaler,
        "model_name": model_name,
        "feature_columns": FEATURE_COLUMNS,
        "feature_importance": feature_importance,
        "metrics": results,
        "best_metrics": results[model_name],
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    metrics = {
        "best_model": model_name,
        "all_results": results,
        "feature_importance": feature_importance,
        "full_auc": float(roc_auc_score(y, y_proba)),
        "accuracy": float(accuracy_score(y, model.predict(y_proba)[:1] if False else y_proba)),
        "default_rate": float(y.mean()),
        "total_borrowers": int(len(y)),
    }

    metrics_path = ARTIFACTS_DIR / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))
    print(f"Metrics saved to {metrics_path}")

    return artifact


def train_and_evaluate():
    df = load_feature_matrix()
    print(f"Feature matrix: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Default rate: {df[TARGET_COLUMN].mean():.1%}")

    X = df[FEATURE_COLUMNS].fillna(0)
    y = df[TARGET_COLUMN]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    models = _build_candidates(y)
    results = _cross_validate(models, X, X_scaled, y)

    best_name = max(results, key=lambda k: results[k]["mean_auc"])
    print(f"\nBest model: {best_name}")

    best_model = models[best_name]
    data = X_scaled if _needs_scaling(best_name) else X
    best_model.fit(data, y)

    feature_importance = _extract_feature_importance(best_model, FEATURE_COLUMNS)

    y_pred = best_model.predict(data)
    y_proba = best_model.predict_proba(data)[:, 1]

    print(f"\nFull dataset AUC: {roc_auc_score(y, y_proba):.3f}")
    print(f"Accuracy: {accuracy_score(y, y_pred):.3f}")
    print(f"\nClassification Report:\n{classification_report(y, y_pred)}")
    print(f"Confusion Matrix:\n{confusion_matrix(y, y_pred)}")

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": best_model,
        "scaler": scaler,
        "model_name": best_name,
        "feature_columns": FEATURE_COLUMNS,
        "feature_importance": feature_importance,
        "metrics": results,
        "best_metrics": results[best_name],
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")

    metrics_out = {
        "best_model": best_name,
        "all_results": results,
        "feature_importance": feature_importance,
        "full_auc": float(roc_auc_score(y, y_proba)),
        "accuracy": float(accuracy_score(y, y_pred)),
        "default_rate": float(y.mean()),
        "total_borrowers": int(len(y)),
    }
    metrics_path = ARTIFACTS_DIR / "metrics.json"
    metrics_path.write_text(json.dumps(metrics_out, indent=2))
    print(f"Metrics saved to {metrics_path}")

    return artifact


def predict_risk(features: dict) -> dict:
    artifact = joblib.load(MODEL_PATH)
    model = artifact["model"]
    scaler = artifact["scaler"]
    model_name = artifact["model_name"]
    feature_cols = artifact["feature_columns"]

    X = pd.DataFrame([{col: features.get(col, 0) for col in feature_cols}])
    X_input = scaler.transform(X) if _needs_scaling(model_name) else X

    proba = model.predict_proba(X_input)[0]
    risk_score = float(proba[1])

    importance = dict(artifact["feature_importance"])
    contributions = sorted(
        [
            {"feature": col, "value": features.get(col, 0), "importance": importance.get(col, 0)}
            for col in feature_cols
        ],
        key=lambda x: x["importance"],
        reverse=True,
    )

    return {
        "risk_score": risk_score,
        "risk_label": risk_label(risk_score),
        "default_probability": risk_score,
        "model_used": model_name,
        "top_factors": contributions[:10],
    }
