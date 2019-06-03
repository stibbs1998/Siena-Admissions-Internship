### This code is taken straight from https://github.com/dataworkshop/xgboost/blob/master/step3.ipynb

def ssing_test_samples(data, last_training_day=0.3, seed=1):
    days = data.day.unique()
    np.random.seed(seed)
    np.random.shuffle(days)
    test_days = days[: int(len(days) * 0.3)]
    
    data['is_test'] = data.day.isin(test_days)


def select_features(data):
    columns = data.columns[ (data.dtypes == np.int64) | (data.dtypes == np.float64) | (data.dtypes == np.bool) ].values    
    return [feat for feat in columns if feat not in ['count', 'casual', 'registered'] and 'log' not in feat ] 

def get_X_y(data, target_variable):
    features = select_features(data)
        
    X = data[features].values
    y = data[target_variable].values
    
    return X,y

def train_test_split(train, target_variable):
    df_train = train[train.is_test == False]
    df_test  = train[train.is_test == True]
    
    X_train, y_train = get_X_y(df_train, target_variable)
    X_test, y_test = get_X_y(df_test, target_variable)
    
    return X_train, X_test, y_train, y_test



def fit_and_predict(train, model, target_variable):
    X_train, X_test, y_train, y_test = train_test_split(train, target_variable)
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    return (y_test, y_pred)

def post_pred(y_pred):
    y_pred[y_pred < 0] = 0
    return y_pred

def rmsle(y_true, y_pred, y_pred_only_positive=True):
    if y_pred_only_positive: y_pred = post_pred(y_pred)
        
    diff = np.log(y_pred+1) - np.log(y_true+1)
    mean_error = np.square(diff).mean()
    return np.sqrt(mean_error)

##########

def count_prediction(train, model, target_variable='count'):
    (y_test, y_pred) = fit_and_predict(train, model, target_variable)

    if target_variable == 'count_log': 
        y_test = train[train.is_test == True]['count']
        y_pred = np.exp2(y_pred)
        
    return rmsle(y_test, y_pred)

    
def registered_casual_prediction(train, model):
    (_, registered_pred) = fit_and_predict(train, model, 'registered')
    (_, casual_pred) = fit_and_predict(train, model, 'casual')

    y_test = train[train.is_test == True]['count']
    y_pred = registered_pred + casual_pred
    
    return rmsle(y_test, y_pred)

def log_registered_casual_prediction(train, model):
    (_, registered_pred) = fit_and_predict(train, model, 'registered_log')
    (_, casual_pred) = fit_and_predict(train, model, 'casual_log')
   
    y_test = train[train.is_test == True]['count']
    y_pred = (np.exp2(registered_pred) - 1) + (np.exp2(casual_pred) -1)
    
    return rmsle(y_test, y_pred)
    
##########

def importance_features(model, data):
    impdf = []
    fscore = model.booster().get_fscore()
    maps_name = dict([ ("f{0}".format(i), col) for i, col in enumerate(data.columns)])

    for ft, score in fscore.iteritems():
        impdf.append({'feature': maps_name[ft], 'importance': score})
    impdf = pd.DataFrame(impdf)
    impdf = impdf.sort_values(by='importance', ascending=False).reset_index(drop=True)
    impdf['importance'] /= impdf['importance'].sum()
    impdf.index = impdf['feature']
        
    return impdf  

def draw_importance_features(model, train):
    impdf = importance_features(model, train)
    return impdf.plot(kind='bar', title='Importance Features', figsize=(20, 8))
    
    
assing_test_samples(train)

