import os
import pandas as pd
import torch
import ast
from backend.utils.preprocessing import process_customer, process_product, interaction_score

class RecommendationModel:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')

        self.customers = pd.read_csv(os.path.join(data_dir, 'customer_data_collection.csv'))
        self.products = pd.read_csv(os.path.join(data_dir, 'product_recommendation_data.csv'))

        self.category_map = {cat: idx for idx, cat in enumerate(self.products['Category'].unique())}
        self.segment_map = {seg: idx for idx, seg in enumerate(self.customers['Customer_Segment'].unique())}
        self.gender_map = {'Male': 0, 'Female': 1, 'Other': 2}

    def recommend(self, customer_id):
        customer = self.customers[self.customers['Customer_ID'].str.upper() == customer_id.upper()].iloc[0]
        customer_features = process_customer(customer, self.segment_map, self.gender_map)
        browsing_list = ast.literal_eval(customer['Browsing_History'])

        recommendations = []
        for _, product in self.products.iterrows():
            product_features = process_product(product, self.category_map)
            score = interaction_score(browsing_list, product['Category'])
            similarity = torch.dot(customer_features, product_features) + score

            recommendations.append({
                "name": f"{product['Category']} - {product['Subcategory']}",
                "category": product['Category'],
                "price": product['Price'],
                "brand": product['Brand'],
                "similarity": similarity.item()
            })

        recommendations = sorted(recommendations, key=lambda x: x['similarity'], reverse=True)[:3]
        return recommendations
