import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load data
df = pd.read_csv('investment_data.csv')

# Encode categorical features
le_risk = LabelEncoder()
le_goal = LabelEncoder()
le_product = LabelEncoder()

df['risk_level'] = le_risk.fit_transform(df['risk_level'])
df['goal'] = le_goal.fit_transform(df['goal'])
df['product_name'] = le_product.fit_transform(df['product_name'])

X = df[['risk_level', 'amount', 'duration_months', 'goal']]
y = df['product_name']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model & label encoders
joblib.dump(model, 'model.pkl')
joblib.dump(le_risk, 'risk_encoder.pkl')
joblib.dump(le_goal, 'goal_encoder.pkl')
joblib.dump(le_product, 'product_encoder.pkl')

# Load your trained model and encoders (already done)


