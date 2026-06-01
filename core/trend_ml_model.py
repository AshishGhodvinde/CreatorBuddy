import numpy as np
import logging

logger = logging.getLogger("TrendMLRanker")

try:
    from sklearn.ensemble import RandomForestRegressor
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

class TrendMLRanker:
    def __init__(self):
        self.model = None
        self.feature_names = [
            "growth_velocity",
            "search_interest",
            "engagement_potential",
            "novelty",
            "audience_relevance"
        ]
        self.X_train, self.y_train = self._generate_historical_seed_dataset()
        self.train_model()

    def _generate_historical_seed_dataset(self):
        np.random.seed(42)
        n_samples = 150
        
        velocity = np.random.randint(55, 100, n_samples)
        search = np.random.randint(50, 98, n_samples)
        engagement = np.random.randint(55, 99, n_samples)
        novelty = np.random.randint(45, 100, n_samples)
        relevance = np.random.randint(60, 100, n_samples)
        
        X = np.stack([velocity, search, engagement, novelty, relevance], axis=1).astype(float)
        y = []
        
        for i in range(n_samples):
            v, s, e, n, r = X[i]
            base = (0.22 * v) + (0.15 * s) + (0.18 * e) + (0.10 * n) + (0.10 * r)
            synergy_vn = 0.12 * (v * n / 100.0)
            synergy_rs = 0.08 * (r * s / 100.0)
            penalty_n = -12.0 if n < 55 else 0.0
            penalty_e = -8.0 if e < 60 else 0.0
            noise = np.random.normal(0, 1.5)
            
            score = base + synergy_vn + synergy_rs + penalty_n + penalty_e + noise
            score = max(min(score, 100.0), 10.0)
            y.append(round(score, 1))
            
        return X, np.array(y)

    def train_model(self):
        if HAS_SKLEARN:
            try:
                self.model = RandomForestRegressor(
                    n_estimators=60,
                    max_depth=6,
                    random_state=42
                )
                self.model.fit(self.X_train, self.y_train)
            except Exception:
                self._train_numpy_fallback()
        else:
            self._train_numpy_fallback()

    def _train_numpy_fallback(self):
        self.numpy_weights, self.numpy_bias = self._fit_ridge_regression()

    def _fit_ridge_regression(self, alpha=0.1):
        X_expanded = self._expand_features(self.X_train)
        y = self.y_train
        
        y_mean = np.mean(y)
        y_centered = y - y_mean
        
        X_mean = np.mean(X_expanded, axis=0)
        X_centered = X_expanded - X_mean
        
        n_features = X_expanded.shape[1]
        XTX = np.dot(X_centered.T, X_centered)
        XTX_reg = XTX + alpha * np.eye(n_features)
        XTy = np.dot(X_centered.T, y_centered)
        
        weights = np.linalg.solve(XTX_reg, XTy)
        bias = y_mean - np.dot(X_mean, weights)
        
        return weights, bias

    def _expand_features(self, X):
        n_samples = X.shape[0]
        v = X[:, 0]
        s = X[:, 1]
        e = X[:, 2]
        n = X[:, 3]
        r = X[:, 4]
        
        synergy_vn = (v * n / 100.0)
        synergy_rs = (r * s / 100.0)
        penalty_n = (n < 55).astype(float)
        penalty_e = (e < 60).astype(float)
        
        return np.stack([v, s, e, n, r, synergy_vn, synergy_rs, penalty_n, penalty_e], axis=1)

    def predict(self, velocity: float, search: float, engagement: float, novelty: float, relevance: float) -> float:
        x_input = np.array([[velocity, search, engagement, novelty, relevance]], dtype=float)
        
        if HAS_SKLEARN and hasattr(self.model, "predict"):
            pred = self.model.predict(x_input)[0]
        else:
            x_expanded = self._expand_features(x_input)
            pred = np.dot(x_expanded, self.numpy_weights)[0] + self.numpy_bias
            
        return float(round(max(min(pred, 100.0), 10.0), 1))

    def get_explainability_report(self, velocity: float, search: float, engagement: float, novelty: float, relevance: float) -> dict:
        baseline_score = np.mean(self.y_train)
        target_score = self.predict(velocity, search, engagement, novelty, relevance)
        
        perturbation = 5.0
        contributions = []
        raw_inputs = [velocity, search, engagement, novelty, relevance]
        
        for idx in range(5):
            inputs_p = list(raw_inputs)
            inputs_p[idx] = min(inputs_p[idx] + perturbation, 100.0)
            score_p = self.predict(*inputs_p)
            
            inputs_n = list(raw_inputs)
            inputs_n[idx] = max(inputs_n[idx] - perturbation, 0.0)
            score_n = self.predict(*inputs_n)
            
            sensitivity = (score_p - score_n) / (2 * perturbation)
            contributions.append(max(0.001, abs(sensitivity)))
            
        total_sensitivity = sum(contributions)
        shares = [round((c / total_sensitivity) * 100, 0) for c in contributions]
        
        diff = 100 - sum(shares)
        shares[0] += diff
        
        return {
            "predicted_score": target_score,
            "baseline_score": round(baseline_score, 1),
            "contributions": {
                "Growth Velocity": f"{shares[0]:.0f}%",
                "Search Interest": f"{shares[1]:.0f}%",
                "Engagement Potential": f"{shares[2]:.0f}%",
                "Novelty Index": f"{shares[3]:.0f}%",
                "Audience Relevance": f"{shares[4]:.0f}%"
            },
            "shares_list": shares
        }
