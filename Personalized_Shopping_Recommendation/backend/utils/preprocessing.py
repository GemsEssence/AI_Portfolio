import torch

def encode_gender(gender):
    mapping = {'Male': 0, 'Female': 1, 'Other': 2}
    return mapping.get(gender, 2)

def encode_segment(segment):
    mapping = {'New Visitor': 0, 'Occasional Shopper': 1, 'Frequent Buyer': 2}
    return mapping.get(segment, 0)

def normalize_price(price):
    return price / 5000  # assuming max price

def normalize_rating(rating):
    return rating / 5  # assuming max rating

def interaction_score(browsing_list, product_category):
    matches = sum(1 for item in browsing_list if item == product_category)
    return matches / max(len(browsing_list), 1)

def process_customer(customer, segment_map, gender_map):
    # Handle dict, pandas Series, or Pydantic model
    if isinstance(customer, dict):
        age_norm = customer['Age'] / 100
        gender = encode_gender(customer['Gender'])
        segment = segment_map.get(customer['Customer_Segment'], 0)
    else:
        # works for pandas Series or Pydantic
        age_norm = customer.Age if hasattr(customer, 'Age') else customer.age
        gender = encode_gender(customer.Gender if hasattr(customer, 'Gender') else customer.gender)
        segment_key = customer.Customer_Segment if hasattr(customer, 'Customer_Segment') else customer.segment
        segment = segment_map.get(segment_key, 0)

    return torch.tensor([age_norm, gender, segment], dtype=torch.float)


# def process_product(product, category_map):
#     price = normalize_price(product['Price'])
#     rating = normalize_rating(product['Product_Rating'])
#     category = category_map.get(product['Category'], 0)
#     return torch.tensor([price, rating, category], dtype=torch.float)

def process_product(product, category_map):
    price = normalize_price(product['Price'])
    rating = normalize_rating(product['Product_Rating'])
    category = category_map.get(product['Category'], 0)
    category_norm = category / max(len(category_map) - 1, 1)  # normalize category
    return torch.tensor([price, rating, category_norm], dtype=torch.float)

