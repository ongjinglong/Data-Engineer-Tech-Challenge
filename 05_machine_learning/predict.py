import pandas as pd
import pickle
import json
import argparse

def load_data(args):
    df = pd.DataFrame(args, index=[0])
    cols = ['maint','doors','persons','lug_boot','safety','class']
    if df.isna().sum().sum() > 0:
        
        null_cols = df.columns[df.isna().any()].tolist()
        valid_cols = df.columns[df.isna().any()==False].tolist()
        print(f'missing input values: {",".join(null_cols)}')
        print(f'searching for other rows with the same values for the remaing columns: {",".join(valid_cols)}')

        data_df = pd.read_csv('data/car.data', header=None)
        data_df.columns = ['buying'] + cols

        merged_df = data_df.merge(df[valid_cols], on=valid_cols)
        if merged_df.empty:
            print(f'no other rows with the same values... proceeding to the mode of all rows for columns: {",".join(null_cols)}')
            new_df = data_df[null_cols].mode().reset_index(drop=True).iloc[0:1,:]
        else:
            print(f'rows found. using mode of these rows for columns: {",".join(null_cols)}')
            new_df = merged_df.groupby(valid_cols).agg(lambda x: pd.Series.mode(x)[0]).reset_index(drop=True)

        df = pd.concat([df[valid_cols],new_df], axis=1)[cols]
    
    print(df)
    return df

def transform_data(df):
    transformer = pickle.load(open('model/oneHotEncTransformer.sav', 'rb'))
    df = transformer.transform(df)
    
    return df

def inverse_transform_prediction(pred):
    transformer = pickle.load(open('model/colEncTransformer.sav', 'rb'))
    pred = transformer.inverse_transform(pred)
    
    return pred

def get_prediction(args):
    df = load_data(args)
    df = transform_data(df)

    model = pickle.load(open('model/rfclassifier.sav', 'rb'))
    prediction = model.predict(df)

    return inverse_transform_prediction(prediction)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Define module')
    parser.add_argument('--maint', help='price of the maintenance')
    parser.add_argument('--doors', help='number of doors')
    parser.add_argument('--persons', help='capacity in terms of persons to carry')
    parser.add_argument('--lug_boot', help='the size of luggage boot')
    parser.add_argument('--safety', help='estimated safety of the car')
    parser.add_argument('--class', help='car evaluation class')
    args = vars(parser.parse_args())
    print(args)

    print('\nBuying price is predicted to be', get_prediction(args)[0])