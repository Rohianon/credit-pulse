"""Credit risk model training and prediction.

Handles the full lifecycle of the credit scoring model:
- Loading the feature matrix from DuckDB
- Baseline cross-validation of candidate models
- Hyperparameter tuning via RandomizedSearchCV
- SMOTE oversampling for class imbalance
- Feature selection with SelectKBest
- Ensemble stacking of tuned models
- Probability calibration for better estimates
- Persisting the best model and metrics to disk
- Scoring individual borrowers against the trained model

The trained model artifact is cached in memory after first load
to avoid repeated disk I/O on every prediction request.
"""

import json
import logging
import warnings
from functools import lru_cache
from typing import Any

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from scipy.stats import loguniform, randint, uniform
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    StackingClassifier,
)
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    RepeatedStratifiedKFold,
    StratifiedKFold,
    cross_val_score,
)
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
# Baseline candidate construction (untuned)
# ---------------------------------------------------------------------------

def _build_baseline_candidates() -> dict[str, Any]:
    """Return baseline sklearn classifiers (pre-tuning) for comparison."""
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
    return model_name in ("logistic_regression", "stacking")


# ---------------------------------------------------------------------------
# Baseline cross-validation
# ---------------------------------------------------------------------------

def _baseline_cross_validate(
    candidates: dict[str, Any],
    features: np.ndarray,
    features_scaled: np.ndarray,
    target: pd.Series,
) -> dict[str, dict]:
    """Run stratified k-fold cross-validation on each baseline candidate."""
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
        logger.info("Baseline %s: AUC = %.3f (+/- %.3f)", name, scores.mean(), scores.std())

    return results


# ---------------------------------------------------------------------------
# Hyperparameter tuning
# ---------------------------------------------------------------------------

def _get_param_distributions() -> dict[str, dict]:
    """Return RandomizedSearchCV parameter distributions for each model."""
    return {
        "random_forest": {
            "n_estimators": randint(50, 500),
            "max_depth": [3, 5, 7, 10, 15, None],
            "min_samples_split": randint(2, 11),
            "min_samples_leaf": randint(1, 6),
            "max_features": ["sqrt", "log2", None],
            "class_weight": ["balanced", "balanced_subsample"],
        },
        "gradient_boosting": {
            "learning_rate": loguniform(0.01, 0.3),
            "n_estimators": randint(50, 300),
            "max_depth": randint(2, 7),
            "subsample": uniform(0.6, 0.4),
            "min_samples_split": randint(2, 9),
        },
        "logistic_regression": {
            "C": loguniform(0.01, 100),
            "penalty": ["l1", "l2"],
            "solver": ["liblinear", "saga"],
            "class_weight": ["balanced"],
            "max_iter": [2000],
        },
    }


def _tune_models(
    features: np.ndarray,
    features_scaled: np.ndarray,
    target: pd.Series,
) -> dict[str, dict]:
    """Run RandomizedSearchCV for each candidate model.

    Returns a dict mapping model name to tuning results including
    the best estimator, best params, and CV score.
    """
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
    param_dists = _get_param_distributions()
    base_models = _build_baseline_candidates()
    tuned: dict[str, dict] = {}

    for name, model in base_models.items():
        input_data = features_scaled if _needs_scaling(name) else features
        logger.info("Tuning %s...", name)

        search = RandomizedSearchCV(
            model,
            param_distributions=param_dists[name],
            n_iter=50,
            cv=cv,
            scoring="roc_auc",
            random_state=42,
            n_jobs=-1,
            error_score="raise",
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            search.fit(input_data, target)

        tuned[name] = {
            "best_estimator": search.best_estimator_,
            "best_params": search.best_params_,
            "mean_auc": float(search.best_score_),
            "std_auc": float(search.cv_results_["std_test_score"][search.best_index_]),
        }
        logger.info(
            "Tuned %s: AUC = %.3f (+/- %.3f) | params = %s",
            name, search.best_score_,
            search.cv_results_["std_test_score"][search.best_index_],
            search.best_params_,
        )

    return tuned


# ---------------------------------------------------------------------------
# SMOTE pipeline evaluation
# ---------------------------------------------------------------------------

def _evaluate_smote_pipeline(
    features: np.ndarray,
    features_scaled: np.ndarray,
    target: pd.Series,
    tuned_models: dict[str, dict],
) -> dict[str, dict]:
    """Compare SMOTE vs class_weight='balanced' for each tuned model.

    Uses imblearn.Pipeline to apply SMOTE inside each CV fold
    (preventing data leakage).
    """
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)
    n_minority = int(target.sum())
    # k_neighbors must be < minority class count
    k_neighbors = min(5, n_minority - 1)

    smote_results: dict[str, dict] = {}

    for name, result in tuned_models.items():
        input_data = features_scaled if _needs_scaling(name) else features
        base_model = result["best_estimator"]

        smote_pipe = ImbPipeline([
            ("smote", SMOTE(random_state=42, k_neighbors=k_neighbors)),
            ("model", base_model),
        ])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            smote_scores = cross_val_score(
                smote_pipe, input_data, target, cv=cv, scoring="roc_auc",
            )

        smote_auc = float(smote_scores.mean())
        base_auc = result["mean_auc"]

        if smote_auc > base_auc:
            logger.info(
                "SMOTE improved %s: %.3f -> %.3f", name, base_auc, smote_auc,
            )
            smote_results[name] = {
                "mean_auc": smote_auc,
                "std_auc": float(smote_scores.std()),
                "used_smote": True,
                "best_estimator": smote_pipe,
            }
        else:
            logger.info(
                "SMOTE did not improve %s (%.3f vs %.3f), keeping original",
                name, smote_auc, base_auc,
            )
            smote_results[name] = {
                "mean_auc": base_auc,
                "std_auc": result["std_auc"],
                "used_smote": False,
                "best_estimator": base_model,
            }

    return smote_results


# ---------------------------------------------------------------------------
# Feature selection
# ---------------------------------------------------------------------------

def _select_features(
    features: pd.DataFrame,
    target: pd.Series,
    feature_columns: list[str],
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Use SelectKBest to find optimal feature subset.

    Tries k values from 8 to len(features) and picks the k with highest
    cross-validated AUC on a simple Random Forest.
    """
    best_k = len(feature_columns)
    best_score = 0.0
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for k in range(8, len(feature_columns) + 1):
        selector = SelectKBest(f_classif, k=k)
        X_selected = selector.fit_transform(features, target)
        scores = cross_val_score(
            RandomForestClassifier(
                n_estimators=100, class_weight="balanced", random_state=42,
            ),
            X_selected, target, cv=cv, scoring="roc_auc",
        )
        mean_score = scores.mean()
        if mean_score > best_score:
            best_score = mean_score
            best_k = k

    selector = SelectKBest(f_classif, k=best_k)
    X_selected = selector.fit_transform(features, target)
    mask = selector.get_support()
    kept = [col for col, m in zip(feature_columns, mask) if m]
    dropped = [col for col, m in zip(feature_columns, mask) if not m]

    logger.info(
        "Feature selection: kept %d/%d features (best k=%d, AUC=%.3f)",
        len(kept), len(feature_columns), best_k, best_score,
    )
    if dropped:
        logger.info("Dropped features: %s", dropped)

    return pd.DataFrame(X_selected, columns=kept), kept, dropped


# ---------------------------------------------------------------------------
# Stacking ensemble
# ---------------------------------------------------------------------------

def _build_stacking_ensemble(
    tuned_models: dict[str, dict],
) -> StackingClassifier:
    """Build a StackingClassifier from the tuned base models."""
    estimators = [
        (name, result["best_estimator"])
        for name, result in tuned_models.items()
    ]
    return StackingClassifier(
        estimators=estimators,
        final_estimator=LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=42,
        ),
        cv=5,
        passthrough=False,
        n_jobs=-1,
    )


# ---------------------------------------------------------------------------
# Feature importance extraction
# ---------------------------------------------------------------------------

def _extract_feature_importance(
    model: Any,
    feature_columns: list[str],
) -> list[tuple[str, float]]:
    """Extract and rank feature importances from a trained model.

    Supports tree-based models (feature_importances_), linear
    models (coef_), stacking classifiers, imblearn pipelines,
    and calibrated classifiers.
    """
    # Unwrap calibrated classifiers
    if hasattr(model, "calibrated_classifiers_"):
        # Average importances across calibrated sub-models
        all_importances = []
        for cal in model.calibrated_classifiers_:
            inner = cal.estimator
            imp = _get_raw_importance(inner, feature_columns)
            if imp is not None:
                all_importances.append(imp)
        if all_importances:
            importances = np.mean(all_importances, axis=0)
        else:
            importances = np.zeros(len(feature_columns))
    else:
        imp = _get_raw_importance(model, feature_columns)
        importances = imp if imp is not None else np.zeros(len(feature_columns))

    return sorted(
        zip(feature_columns, importances.tolist()),
        key=lambda pair: pair[1],
        reverse=True,
    )


def _get_raw_importance(model: Any, feature_columns: list[str]) -> np.ndarray | None:
    """Get raw importance array from a model, unwrapping pipelines/stacking."""
    # Unwrap imblearn pipeline
    if hasattr(model, "named_steps") and "model" in model.named_steps:
        model = model.named_steps["model"]

    if hasattr(model, "feature_importances_"):
        return model.feature_importances_
    elif hasattr(model, "coef_"):
        return np.abs(model.coef_[0])
    elif isinstance(model, StackingClassifier):
        # Average importances from stacking base estimators
        all_imp = []
        for _, est in model.estimators:
            imp = _get_raw_importance(est, feature_columns)
            if imp is not None:
                all_imp.append(imp)
        if all_imp:
            return np.mean(all_imp, axis=0)
    return None


# ---------------------------------------------------------------------------
# Artifact persistence
# ---------------------------------------------------------------------------

def _save_model_artifact(
    model: Any,
    scaler: StandardScaler,
    model_name: str,
    feature_columns: list[str],
    feature_importance: list[tuple[str, float]],
    cv_results: dict[str, dict],
) -> dict[str, Any]:
    """Serialize the trained model and metadata to disk."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": model,
        "scaler": scaler,
        "model_name": model_name,
        "feature_columns": feature_columns,
        "feature_importance": feature_importance,
        "metrics": cv_results,
        "best_metrics": cv_results[model_name],
    }
    joblib.dump(artifact, MODEL_PATH)
    logger.info("Model artifact saved to %s", MODEL_PATH)
    return artifact


def _save_metrics_report(
    model_name: str,
    baseline_results: dict[str, dict],
    tuned_results: dict[str, dict],
    feature_importance: list[tuple[str, float]],
    target: pd.Series,
    predicted_proba: np.ndarray,
    predicted_labels: np.ndarray,
    selected_features: list[str],
    dropped_features: list[str],
) -> None:
    """Write a metrics JSON report with baseline vs tuned comparison."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics = {
        "best_model": model_name,
        "baseline_results": {
            name: {"mean_auc": r["mean_auc"], "std_auc": r["std_auc"]}
            for name, r in baseline_results.items()
        },
        "tuned_results": {
            name: {
                "mean_auc": r["mean_auc"],
                "std_auc": r["std_auc"],
                "used_smote": r.get("used_smote", False),
            }
            for name, r in tuned_results.items()
        },
        "feature_importance": feature_importance,
        "selected_features": selected_features,
        "dropped_features": dropped_features,
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
    """Train candidate models with full tuning pipeline and persist artifacts.

    Workflow:
        1. Load the feature matrix from DuckDB.
        2. Run baseline cross-validation for comparison.
        3. Perform feature selection with SelectKBest.
        4. Hyperparameter-tune all candidates via RandomizedSearchCV.
        5. Compare SMOTE vs class_weight='balanced' for each model.
        6. Build a stacking ensemble from tuned models.
        7. Select the candidate with the highest mean AUC.
        8. Calibrate the best model's probabilities.
        9. Save the model artifact and metrics report.

    Returns:
        The model artifact dictionary.
    """
    df = load_feature_matrix()
    logger.info("Feature matrix: %d rows, %d columns", df.shape[0], df.shape[1])
    logger.info("Default rate: %.1f%%", df[TARGET_COLUMN].mean() * 100)

    features_raw = df[FEATURE_COLUMNS].fillna(0)
    target = df[TARGET_COLUMN]

    # --- Step 1: Baseline cross-validation ---
    logger.info("=" * 60)
    logger.info("STEP 1: Baseline cross-validation")
    logger.info("=" * 60)

    scaler = StandardScaler()
    features_scaled_raw = scaler.fit_transform(features_raw)

    baseline_candidates = _build_baseline_candidates()
    baseline_results = _baseline_cross_validate(
        baseline_candidates, features_raw, features_scaled_raw, target,
    )

    baseline_best = max(baseline_results, key=lambda n: baseline_results[n]["mean_auc"])
    logger.info(
        "Baseline best: %s (AUC = %.3f)",
        baseline_best, baseline_results[baseline_best]["mean_auc"],
    )

    # --- Step 2: Feature selection ---
    logger.info("=" * 60)
    logger.info("STEP 2: Feature selection")
    logger.info("=" * 60)

    features_selected, selected_features, dropped_features = _select_features(
        features_raw, target, FEATURE_COLUMNS,
    )

    # Re-fit scaler on selected features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features_selected)

    # --- Step 3: Hyperparameter tuning ---
    logger.info("=" * 60)
    logger.info("STEP 3: Hyperparameter tuning (RandomizedSearchCV)")
    logger.info("=" * 60)

    features_scaled_df = pd.DataFrame(features_scaled, columns=selected_features)
    tuned = _tune_models(features_selected, features_scaled_df, target)

    # --- Step 4: SMOTE comparison ---
    logger.info("=" * 60)
    logger.info("STEP 4: SMOTE vs class_weight comparison")
    logger.info("=" * 60)

    smote_results = _evaluate_smote_pipeline(
        features_selected, features_scaled_df, target, tuned,
    )

    # --- Step 5: Stacking ensemble ---
    logger.info("=" * 60)
    logger.info("STEP 5: Stacking ensemble")
    logger.info("=" * 60)

    stacking = _build_stacking_ensemble(tuned)
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=10, random_state=42)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        stacking_scores = cross_val_score(
            stacking, features_scaled_df, target, cv=cv, scoring="roc_auc",
        )

    smote_results["stacking"] = {
        "mean_auc": float(stacking_scores.mean()),
        "std_auc": float(stacking_scores.std()),
        "used_smote": False,
        "best_estimator": stacking,
    }
    logger.info(
        "Stacking: AUC = %.3f (+/- %.3f)",
        stacking_scores.mean(), stacking_scores.std(),
    )

    # --- Step 6: Select best model ---
    logger.info("=" * 60)
    logger.info("STEP 6: Select best and calibrate")
    logger.info("=" * 60)

    best_name = max(smote_results, key=lambda n: smote_results[n]["mean_auc"])
    best_model = smote_results[best_name]["best_estimator"]
    logger.info(
        "Best tuned model: %s (AUC = %.3f)",
        best_name, smote_results[best_name]["mean_auc"],
    )

    # Fit on full dataset
    training_input = features_scaled_df if _needs_scaling(best_name) else features_selected
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        best_model.fit(training_input, target)

    # --- Step 7: Probability calibration ---
    logger.info("Calibrating probabilities...")
    calibrated = CalibratedClassifierCV(best_model, cv=5, method="sigmoid")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        calibrated.fit(training_input, target)

    # Build combined results dict for metrics (include all candidate + stacking)
    all_results = {}
    for name, result in smote_results.items():
        all_results[name] = {
            "mean_auc": result["mean_auc"],
            "std_auc": result["std_auc"],
            "used_smote": result.get("used_smote", False),
        }

    feature_importance = _extract_feature_importance(calibrated, selected_features)

    predicted_proba = calibrated.predict_proba(training_input)[:, 1]
    predicted_labels = calibrated.predict(training_input)

    logger.info("Full dataset AUC: %.3f", roc_auc_score(target, predicted_proba))
    logger.info("Accuracy: %.3f", accuracy_score(target, predicted_labels))
    logger.info("Classification Report:\n%s", classification_report(target, predicted_labels))
    logger.info("Confusion Matrix:\n%s", confusion_matrix(target, predicted_labels))

    # --- Comparison summary ---
    logger.info("=" * 60)
    logger.info("COMPARISON: Baseline vs Tuned")
    logger.info("=" * 60)
    for name in baseline_results:
        base_auc = baseline_results[name]["mean_auc"]
        tuned_auc = smote_results.get(name, {}).get("mean_auc", 0)
        delta = tuned_auc - base_auc
        logger.info(
            "%s: %.3f -> %.3f (%+.3f)",
            name, base_auc, tuned_auc, delta,
        )
    if "stacking" in smote_results:
        logger.info(
            "stacking (new): %.3f",
            smote_results["stacking"]["mean_auc"],
        )

    artifact = _save_model_artifact(
        model=calibrated,
        scaler=scaler,
        model_name=best_name,
        feature_columns=selected_features,
        feature_importance=feature_importance,
        cv_results=all_results,
    )

    _save_metrics_report(
        model_name=best_name,
        baseline_results=baseline_results,
        tuned_results=all_results,
        feature_importance=feature_importance,
        target=target,
        predicted_proba=predicted_proba,
        predicted_labels=predicted_labels,
        selected_features=selected_features,
        dropped_features=dropped_features,
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
