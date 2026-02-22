"""Credit risk model training and prediction.

Handles the full lifecycle of the credit scoring model:
- Loading the feature matrix from DuckDB
- Training and cross-validating candidate models
- Persisting the best model and metrics to disk
- Scoring individual borrowers against the trained model

The trained model artifact is cached in memory after first load
to avoid repeated disk I/O on every prediction request.
"""

import json
import logging
from functools import lru_cache
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler

from backend.core.config import ARTIFACTS_DIR, MODEL_PATH, risk_label
from backend.core.database import get_connection
from backend.services.feature_engine import FEATURE_COLUMNS, TARGET_COLUMN

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Model artifact caching
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_artifact_cached(model_mtime_ns: int) -> dict[str, Any]:
    """Load the model artifact from disk, caching by file modification time.

    The mtime_ns parameter is not used inside the function body -- it
    exists solely as a cache key so that lru_cache invalidates when the
    model file changes on disk.
    """
    return joblib.load(MODEL_PATH)


def load_artifact() -> dict[str, Any]:
    """Return the trained model artifact, loading from disk only when the file changes.

    Raises:
        FileNotFoundError: If the model has not been trained yet.
    """
    mtime_ns = MODEL_PATH.stat().st_mtime_ns
    return _load_artifact_cached(mtime_ns)


# ---------------------------------------------------------------------------
# Feature matrix loading
# ---------------------------------------------------------------------------

def load_feature_matrix() -> pd.DataFrame:
    """Read the full credit feature mart from DuckDB."""
    with get_connection() as conn:
        return conn.execute("SELECT * FROM mart_credit_features").fetchdf()


# ---------------------------------------------------------------------------
# Candidate model construction
# ---------------------------------------------------------------------------

def _build_candidates() -> dict[str, Any]:
    """Return a dictionary of named sklearn classifiers to evaluate."""
    return {
        "logistic_regression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=42,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100, class_weight="balanced", random_state=42,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=100, random_state=42, max_depth=4,
        ),
    }


def _needs_scaling(model_name: str) -> bool:
    """Return True if the model benefits from feature scaling."""
    return model_name == "logistic_regression"


# ---------------------------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------------------------

def _cross_validate(
    candidates: dict[str, Any],
    features: np.ndarray,
    features_scaled: np.ndarray,
    target: pd.Series,
) -> dict[str, dict]:
    """Run stratified k-fold cross-validation on each candidate model.

    Returns a dict mapping model name to its AUC statistics.
    """
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results: dict[str, dict] = {}

    for name, model in candidates.items():
        input_data = features_scaled if _needs_scaling(name) else features
        scores = cross_val_score(model, input_data, target, cv=cv, scoring="roc_auc")
        results[name] = {
            "mean_auc": float(scores.mean()),
            "std_auc": float(scores.std()),
            "cv_scores": scores.tolist(),
        }
        logger.info("%s: AUC = %.3f (+/- %.3f)", name, scores.mean(), scores.std())

    return results


# ---------------------------------------------------------------------------
# Feature importance extraction
# ---------------------------------------------------------------------------

def _extract_feature_importance(
    model: Any,
    feature_columns: list[str],
) -> list[tuple[str, float]]:
    """Extract and rank feature importances from a trained model.

    Supports tree-based models (feature_importances_) and linear
    models (coef_). Falls back to zeros for unsupported model types.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_[0])
    else:
        importances = np.zeros(len(feature_columns))

    return sorted(
        zip(feature_columns, importances.tolist()),
        key=lambda pair: pair[1],
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Artifact persistence
# ---------------------------------------------------------------------------

def _save_model_artifact(
    model: Any,
    scaler: StandardScaler,
    model_name: str,
    feature_importance: list[tuple[str, float]],
    cv_results: dict[str, dict],
) -> dict[str, Any]:
    """Serialize the trained model and metadata to disk.

    Returns the artifact dictionary for immediate use.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": model,
        "scaler": scaler,
        "model_name": model_name,
        "feature_columns": FEATURE_COLUMNS,
        "feature_importance": feature_importance,
        "metrics": cv_results,
        "best_metrics": cv_results[model_name],
    }
    joblib.dump(artifact, MODEL_PATH)
    logger.info("Model artifact saved to %s", MODEL_PATH)
    return artifact


def _save_metrics_report(
    model_name: str,
    cv_results: dict[str, dict],
    feature_importance: list[tuple[str, float]],
    target: pd.Series,
    predicted_proba: np.ndarray,
    predicted_labels: np.ndarray,
) -> None:
    """Write a human-readable metrics JSON report to the artifacts directory."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics = {
        "best_model": model_name,
        "all_results": cv_results,
        "feature_importance": feature_importance,
        "full_auc": float(roc_auc_score(target, predicted_proba)),
        "accuracy": float(accuracy_score(target, predicted_labels)),
        "default_rate": float(target.mean()),
        "total_borrowers": int(len(target)),
    }

    metrics_path = ARTIFACTS_DIR / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))
    logger.info("Metrics report saved to %s", metrics_path)


# ---------------------------------------------------------------------------
# Training entry point
# ---------------------------------------------------------------------------

def train_and_evaluate() -> dict[str, Any]:
    """Train candidate models, select the best, and persist artifacts.

    Workflow:
        1. Load the feature matrix from DuckDB.
        2. Scale features for models that require it.
        3. Cross-validate all candidate models.
        4. Select the candidate with the highest mean AUC.
        5. Fit the best model on the full dataset.
        6. Save the model artifact and metrics report.

    Returns:
        The model artifact dictionary.
    """
    df = load_feature_matrix()
    logger.info("Feature matrix: %d rows, %d columns", df.shape[0], df.shape[1])
    logger.info("Default rate: %.1f%%", df[TARGET_COLUMN].mean() * 100)

    features = df[FEATURE_COLUMNS].fillna(0)
    target = df[TARGET_COLUMN]

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    candidates = _build_candidates()
    cv_results = _cross_validate(candidates, features, features_scaled, target)

    best_name = max(cv_results, key=lambda name: cv_results[name]["mean_auc"])
    logger.info("Best model: %s", best_name)

    best_model = candidates[best_name]
    training_input = features_scaled if _needs_scaling(best_name) else features
    best_model.fit(training_input, target)

    feature_importance = _extract_feature_importance(best_model, FEATURE_COLUMNS)

    predicted_labels = best_model.predict(training_input)
    predicted_proba = best_model.predict_proba(training_input)[:, 1]

    logger.info("Full dataset AUC: %.3f", roc_auc_score(target, predicted_proba))
    logger.info("Accuracy: %.3f", accuracy_score(target, predicted_labels))
    logger.info("Classification Report:\n%s", classification_report(target, predicted_labels))
    logger.info("Confusion Matrix:\n%s", confusion_matrix(target, predicted_labels))

    artifact = _save_model_artifact(
        model=best_model,
        scaler=scaler,
        model_name=best_name,
        feature_importance=feature_importance,
        cv_results=cv_results,
    )

    _save_metrics_report(
        model_name=best_name,
        cv_results=cv_results,
        feature_importance=feature_importance,
        target=target,
        predicted_proba=predicted_proba,
        predicted_labels=predicted_labels,
    )

    return artifact


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def predict_risk(features: dict[str, float]) -> dict[str, Any]:
    """Score a single borrower and return risk details.

    Args:
        features: A mapping of feature column names to their numeric values.
                  Missing features default to 0.

    Returns:
        A dict containing risk_score, risk_label, default_probability,
        model_used, and the top contributing factors.

    Raises:
        FileNotFoundError: If no trained model artifact exists on disk.
    """
    artifact = load_artifact()

    model = artifact["model"]
    scaler = artifact["scaler"]
    model_name = artifact["model_name"]
    feature_columns = artifact["feature_columns"]

    borrower_features = pd.DataFrame(
        [{col: features.get(col, 0) for col in feature_columns}]
    )
    model_input = (
        scaler.transform(borrower_features)
        if _needs_scaling(model_name)
        else borrower_features
    )

    risk_score = float(model.predict_proba(model_input)[0, 1])

    importance_lookup = dict(artifact["feature_importance"])
    top_factors = sorted(
        [
            {
                "feature": col,
                "value": features.get(col, 0),
                "importance": importance_lookup.get(col, 0),
            }
            for col in feature_columns
        ],
        key=lambda factor: factor["importance"],
        reverse=True,
    )[:10]

    return {
        "risk_score": risk_score,
        "risk_label": risk_label(risk_score),
        "default_probability": risk_score,
        "model_used": model_name,
        "top_factors": top_factors,
    }
