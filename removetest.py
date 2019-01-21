import numpy as np
import lightgbm as lgb
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error

def modeling_cross_validation(params, X, y, nr_folds=5):
    oof_preds = np.zeros(X.shape[0])
    # Split data with kfold
    folds = KFold(n_splits=nr_folds, shuffle=False, random_state=4096)
    
    for fold_, (trn_idx, val_idx) in enumerate(folds.split(X, y)):
        print("fold n°{}".format(fold_ + 1))
        trn_data = lgb.Dataset(X[trn_idx], y[trn_idx])
        val_data = lgb.Dataset(X[val_idx], y[val_idx])
        
        num_round = 20000
        clf = lgb.train(params, trn_data, num_round, valid_sets=[trn_data, val_data], verbose_eval=1000,
                        early_stopping_rounds=100)
        oof_preds[val_idx] = clf.predict(X[val_idx], num_iteration=clf.best_iteration)
    
    score = mean_squared_error(oof_preds, y)

return score / 2

def featureSelect(init_cols, train, label):
    params = {  'num_leaves': 120,
                'min_data_in_leaf': 30,
                'objective': 'regression',
                'max_depth': -1,
                'learning_rate': 0.05,
                "min_child_samples": 30,
                "boosting": "gbdt",
                "feature_fraction": 0.9,
                "bagging_freq": 1,
                "bagging_fraction": 0.9,
                "bagging_seed": 11,
                "metric": 'mse',
                "lambda_l1": 0.02,
                "verbosity": -1}
    best_cols = init_cols.copy()
    best_score = modeling_cross_validation(params, train[init_cols].values, label.values,  nr_folds=5)
    print("inital score: {:<8.8f}".format(best_score))
    for f in init_cols:
        
        best_cols.remove(f)
        score = modeling_cross_validation(params, train[best_cols].values, label.values, nr_folds=5)
        diff = best_score - score
        print('-' * 100)
        if diff > 0.0000002:
            print("remove feature: {}, CV score: {:<8.8f}, best cv score: {:<8.8f}, remove".format(f, score, best_score))
            best_score = score
        else:
            print("remove feature: {}, CV score: {:<8.8f}, best cv score: {:<8.8f}, keep".format(f, score, best_score))
            best_cols.append(f)
print('-' * 10)
print("selected CV score: {:<8.8f}".format(best_score))

return best_cols


# best_features = featureSelect(train.columns.tolist())
